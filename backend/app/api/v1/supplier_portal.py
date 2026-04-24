"""
供应商门户 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import json

from app.core.database import get_db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus, SupplierConfirmStatus
from app.models.purchase_inbound import PurchaseInbound, Settlement
from app.models.supplier import Supplier
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class SupplierProfileResponse(BaseModel):
    """供应商档案响应"""
    id: int
    name: str
    credit_code: Optional[str]
    contact_name: Optional[str]
    contact_phone: Optional[str]
    address: Optional[str]
    bank_name: Optional[str]
    bank_account: Optional[str]
    settlement_type: str


class SupplierProfileUpdateRequest(BaseModel):
    """供应商档案更新请求"""
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None


class OrderAdjustmentRequest(BaseModel):
    """订单调整申请请求"""
    reason: str
    adjustment_items: Optional[list] = None  # 调整明细列表


@router.get("/orders")
async def list_supplier_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """供应商查看我的订单列表"""
    # 确保当前用户是供应商角色
    if not current_user.supplier_id:
        raise HTTPException(status_code=403, detail="非供应商账号")

    query = select(PurchaseOrder).where(PurchaseOrder.supplier_id == current_user.supplier_id)

    if status:
        query = query.where(PurchaseOrder.status == status)

    # 按创建时间倒序
    query = query.order_by(PurchaseOrder.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    orders = result.scalars().all()

    # 获取总数
    count_query = select(func.count(PurchaseOrder.id)).where(PurchaseOrder.supplier_id == current_user.supplier_id)
    if status:
        count_query = count_query.where(PurchaseOrder.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "total_amount": float(o.total_amount),
                "status": o.status.value,
                "supplier_confirm_status": o.supplier_confirm_status.value if o.supplier_confirm_status else None,
                "created_at": o.created_at,
                "supplier_confirmed_at": o.supplier_confirmed_at,
            }
            for o in orders
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/orders/{order_id}")
async def get_supplier_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """供应商查看订单详情"""
    if not current_user.supplier_id:
        raise HTTPException(status_code=403, detail="非供应商账号")

    result = await db.execute(
        select(PurchaseOrder)
        .where(PurchaseOrder.id == order_id)
        .where(PurchaseOrder.supplier_id == current_user.supplier_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return {
        "id": order.id,
        "order_no": order.order_no,
        "total_amount": float(order.total_amount),
        "status": order.status.value,
        "supplier_confirm_status": order.supplier_confirm_status.value if order.supplier_confirm_status else None,
        "remark": order.remark,
        "created_at": order.created_at,
        "confirmed_at": order.confirmed_at,
        "supplier_confirmed_at": order.supplier_confirmed_at,
        "items": [
            {
                "id": i.id,
                "product_id": i.product_id,
                "product_name": i.product.name if i.product else None,
                "quantity": i.quantity,
                "cost_price": float(i.cost_price),
                "subtotal": float(i.subtotal),
            }
            for i in order.items
        ],
    }


@router.post("/orders/{order_id}/confirm")
async def confirm_supplier_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """供应商确认供货"""
    if not current_user.supplier_id:
        raise HTTPException(status_code=403, detail="非供应商账号")

    result = await db.execute(
        select(PurchaseOrder)
        .where(PurchaseOrder.id == order_id)
        .where(PurchaseOrder.supplier_id == current_user.supplier_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.supplier_confirm_status == SupplierConfirmStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="订单已确认")

    order.supplier_confirm_status = SupplierConfirmStatus.CONFIRMED
    order.supplier_confirmed_at = datetime.now()
    await db.commit()

    return {"message": "已确认供货"}


@router.post("/orders/{order_id}/reject")
async def reject_supplier_order(
    order_id: int,
    request: OrderAdjustmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """供应商申请修改订单（拒绝原订单）"""
    if not current_user.supplier_id:
        raise HTTPException(status_code=403, detail="非供应商账号")

    result = await db.execute(
        select(PurchaseOrder)
        .where(PurchaseOrder.id == order_id)
        .where(PurchaseOrder.supplier_id == current_user.supplier_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 创建调整申请
    from app.models.purchase_order_adjustment import PurchaseOrderAdjustment, AdjustmentStatus

    adjustment = PurchaseOrderAdjustment(
        order_id=order.id,
        supplier_id=current_user.supplier_id,
        reason=request.reason,
        adjustment_items=json.dumps(request.adjustment_items) if request.adjustment_items else None,
        status=AdjustmentStatus.PENDING,
    )
    db.add(adjustment)

    # 更新订单状态
    order.supplier_confirm_status = SupplierConfirmStatus.REJECTED
    await db.commit()

    return {"message": "已提交修改申请", "adjustment_id": adjustment.id}


@router.get("/inbounds")
async def list_supplier_inbounds(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """供应商查看入库记录"""
    if not current_user.supplier_id:
        raise HTTPException(status_code=403, detail="非供应商账号")

    query = (
        select(PurchaseInbound)
        .join(PurchaseOrder)
        .where(PurchaseOrder.supplier_id == current_user.supplier_id)
    )

    # 按创建时间倒序
    query = query.order_by(PurchaseInbound.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    inbounds = result.scalars().all()

    # 获取总数
    count_query = (
        select(func.count(PurchaseInbound.id))
        .join(PurchaseOrder)
        .where(PurchaseOrder.supplier_id == current_user.supplier_id)
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": i.id,
                "order_id": i.order_id,
                "order_no": i.order.order_no,
                "total_quantity": i.total_quantity,
                "status": i.status.value,
                "created_at": i.created_at,
            }
            for i in inbounds
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/settlements")
async def list_supplier_settlements(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """供应商查看结算记录"""
    if not current_user.supplier_id:
        raise HTTPException(status_code=403, detail="非供应商账号")

    query = (
        select(Settlement)
        .join(PurchaseOrder)
        .where(PurchaseOrder.supplier_id == current_user.supplier_id)
    )

    # 按创建时间倒序
    query = query.order_by(Settlement.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    settlements = result.scalars().all()

    # 获取总数
    count_query = (
        select(func.count(Settlement.id))
        .join(PurchaseOrder)
        .where(PurchaseOrder.supplier_id == current_user.supplier_id)
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": s.id,
                "order_id": s.order_id,
                "order_no": s.order.order_no,
                "amount": float(s.amount),
                "type": s.type.value,
                "status": s.status.value,
                "paid_at": s.paid_at,
                "created_at": s.created_at,
            }
            for s in settlements
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/profile")
async def get_supplier_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """供应商查看自己的档案"""
    if not current_user.supplier_id:
        raise HTTPException(status_code=403, detail="非供应商账号")

    result = await db.execute(select(Supplier).where(Supplier.id == current_user.supplier_id))
    supplier = result.scalar_one_or_none()

    if not supplier:
        raise HTTPException(status_code=404, detail="供应商档案不存在")

    return {
        "id": supplier.id,
        "name": supplier.name,
        "credit_code": supplier.credit_code,
        "contact_name": supplier.contact_name,
        "contact_phone": supplier.contact_phone,
        "address": supplier.address,
        "bank_name": supplier.bank_name,
        "bank_account": supplier.bank_account,
        "settlement_type": supplier.settlement_type,
        "status": supplier.status,
    }


@router.put("/profile")
async def update_supplier_profile(
    request: SupplierProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """供应商更新自己的档案"""
    if not current_user.supplier_id:
        raise HTTPException(status_code=403, detail="非供应商账号")

    result = await db.execute(select(Supplier).where(Supplier.id == current_user.supplier_id))
    supplier = result.scalar_one_or_none()

    if not supplier:
        raise HTTPException(status_code=404, detail="供应商档案不存在")

    # 只允许更新联系方式和银行账户
    if request.contact_name is not None:
        supplier.contact_name = request.contact_name
    if request.contact_phone is not None:
        supplier.contact_phone = request.contact_phone
    if request.address is not None:
        supplier.address = request.address
    if request.bank_name is not None:
        supplier.bank_name = request.bank_name
    if request.bank_account is not None:
        supplier.bank_account = request.bank_account

    await db.commit()

    return {"message": "档案已更新"}
