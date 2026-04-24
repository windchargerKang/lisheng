"""
采购订单 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus
from app.models.supplier import Supplier
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class PurchaseOrderItemRequest(BaseModel):
    """采购订单项请求"""
    product_id: int
    quantity: int
    cost_price: float


class PurchaseOrderCreateRequest(BaseModel):
    """创建采购订单请求"""
    supplier_id: int
    items: list[PurchaseOrderItemRequest]
    remark: Optional[str] = None


@router.get("")
async def list_purchase_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    supplier_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取采购订单列表（分页、筛选）"""
    query = select(PurchaseOrder)

    if status:
        query = query.where(PurchaseOrder.status == status)
    if supplier_id:
        query = query.where(PurchaseOrder.supplier_id == supplier_id)

    # 按创建时间倒序
    query = query.order_by(PurchaseOrder.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    orders = result.scalars().all()

    # 获取总数
    count_query = select(func.count(PurchaseOrder.id))
    if status:
        count_query = count_query.where(PurchaseOrder.status == status)
    if supplier_id:
        count_query = count_query.where(PurchaseOrder.supplier_id == supplier_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "supplier_id": o.supplier_id,
                "supplier_name": o.supplier.name if o.supplier else None,
                "total_amount": float(o.total_amount),
                "status": o.status.value,
                "created_at": o.created_at,
            }
            for o in orders
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{order_id}")
async def get_purchase_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取采购订单详情"""
    result = await db.execute(
        select(PurchaseOrder)
        .where(PurchaseOrder.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return {
        "id": order.id,
        "order_no": order.order_no,
        "supplier_id": order.supplier_id,
        "supplier_name": order.supplier.name if order.supplier else None,
        "purchaser_id": order.purchaser_id,
        "total_amount": float(order.total_amount),
        "status": order.status.value,
        "remark": order.remark,
        "created_at": order.created_at,
        "confirmed_at": order.confirmed_at,
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


@router.post("")
async def create_purchase_order(
    request: PurchaseOrderCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建采购订单"""
    # 验证供应商是否存在
    supplier_result = await db.execute(select(Supplier).where(Supplier.id == request.supplier_id))
    supplier = supplier_result.scalar_one_or_none()

    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    # 生成订单号
    order_no = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4].upper()}"

    # 创建订单
    order = PurchaseOrder(
        order_no=order_no,
        supplier_id=request.supplier_id,
        purchaser_id=current_user.id,
        total_amount=0,
        status=PurchaseOrderStatus.PENDING,
        remark=request.remark,
    )
    db.add(order)
    await db.flush()

    # 创建订单项
    total_amount = 0
    for item_req in request.items:
        item = PurchaseOrderItem(
            order_id=order.id,
            product_id=item_req.product_id,
            quantity=item_req.quantity,
            cost_price=item_req.cost_price,
            subtotal=item_req.quantity * item_req.cost_price,
        )
        db.add(item)
        total_amount += float(item.subtotal)

    order.total_amount = total_amount
    await db.commit()
    await db.refresh(order)

    return {
        "id": order.id,
        "order_no": order.order_no,
        "total_amount": float(order.total_amount),
        "status": order.status.value,
    }


@router.put("/{order_id}/confirm")
async def confirm_purchase_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """确认采购订单"""
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status != PurchaseOrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="只有待确认订单可以确认")

    order.status = PurchaseOrderStatus.CONFIRMED
    order.confirmed_at = datetime.now()
    await db.commit()

    return {"message": "订单已确认"}


@router.post("/{order_id}/cancel")
async def cancel_purchase_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消采购订单"""
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status not in [PurchaseOrderStatus.PENDING, PurchaseOrderStatus.CONFIRMED]:
        raise HTTPException(status_code=400, detail="当前状态不允许取消")

    order.status = PurchaseOrderStatus.CANCELLED
    await db.commit()

    return {"message": "订单已取消"}
