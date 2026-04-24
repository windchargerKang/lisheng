"""
采购入库与结算 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

from app.core.database import get_db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus
from app.models.purchase_inbound import PurchaseInbound, Settlement, InboundStatus, SettlementType, SettlementStatus
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class PurchaseInboundCreateRequest(BaseModel):
    """创建采购入库请求"""
    order_id: int


class SettlementListResponse(BaseModel):
    """结算记录响应"""
    id: int
    supplier_id: int
    supplier_name: str
    order_id: int
    order_no: str
    amount: float
    type: str
    status: str
    paid_at: Optional[datetime]
    created_at: datetime


@router.post("")
async def create_purchase_inbound(
    request: PurchaseInboundCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建采购入库记录（增加库存）"""
    # 验证采购订单是否存在
    order_result = await db.execute(
        select(PurchaseOrder).where(PurchaseOrder.id == request.order_id)
    )
    order = order_result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="采购订单不存在")

    # 验证订单状态
    if order.status != PurchaseOrderStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="只有已确认订单可以入库")

    # 检查是否已入库
    existing_inbound = await db.execute(
        select(PurchaseInbound).where(PurchaseInbound.order_id == request.order_id)
    )
    if existing_inbound.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该订单已入库")

    # 创建入库记录
    inbound = PurchaseInbound(
        order_id=request.order_id,
        warehouse_operator_id=current_user.id,
        total_quantity=0,
        status=InboundStatus.COMPLETED,
    )
    db.add(inbound)
    await db.flush()

    # 增加库存
    total_quantity = 0
    for item in order.items:
        product_result = await db.execute(
            select(Product).where(Product.id == item.product_id)
        )
        product = product_result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail=f"商品 {item.product_id} 不存在")

        # 增加库存
        product.stock += item.quantity
        total_quantity += item.quantity

        # 更新商品成本价（加权平均）
        if product.cost_price:
            # 已有成本价，计算加权平均（使用 Decimal 保证精度）
            total_cost = Decimal(str(product.cost_price)) * product.stock + Decimal(str(item.subtotal))
            new_stock = product.stock
            if new_stock > 0:
                product.cost_price = float(total_cost / new_stock)
        else:
            # 首次设置成本价
            product.cost_price = item.cost_price

    inbound.total_quantity = total_quantity
    await db.commit()
    await db.refresh(inbound)

    # 自动创建现款结算记录
    settlement = Settlement(
        supplier_id=order.supplier_id,
        order_id=order.id,
        amount=order.total_amount,
        type=SettlementType.CASH,
        status=SettlementStatus.PAID,
        paid_at=datetime.now(),
    )
    db.add(settlement)
    await db.commit()

    # 更新订单状态为已完成
    order.status = PurchaseOrderStatus.COMPLETED
    await db.commit()

    return {
        "id": inbound.id,
        "order_id": inbound.order_id,
        "total_quantity": inbound.total_quantity,
        "status": inbound.status.value,
        "settlement_id": settlement.id,
    }


@router.get("")
async def list_purchase_inbounds(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    order_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取入库记录列表（分页、筛选）"""
    query = select(PurchaseInbound).join(PurchaseOrder)

    if order_id:
        query = query.where(PurchaseInbound.order_id == order_id)

    # 按创建时间倒序
    query = query.order_by(PurchaseInbound.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    inbounds = result.scalars().all()

    # 获取总数
    count_query = select(func.count(PurchaseInbound.id)).join(PurchaseOrder)
    if order_id:
        count_query = count_query.where(PurchaseInbound.order_id == order_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": i.id,
                "order_id": i.order_id,
                "order_no": i.order.order_no,
                "supplier_id": i.order.supplier_id,
                "supplier_name": i.order.supplier.name if i.order.supplier else None,
                "total_quantity": i.total_quantity,
                "warehouse_operator_id": i.warehouse_operator_id,
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
async def list_settlements(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    supplier_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取结算记录列表（分页、筛选）"""
    query = select(Settlement).join(PurchaseOrder)

    if supplier_id:
        query = query.where(Settlement.supplier_id == supplier_id)
    if status:
        query = query.where(Settlement.status == status)

    # 按创建时间倒序
    query = query.order_by(Settlement.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    settlements = result.scalars().all()

    # 获取总数
    count_query = select(func.count(Settlement.id)).join(PurchaseOrder)
    if supplier_id:
        count_query = count_query.where(Settlement.supplier_id == supplier_id)
    if status:
        count_query = count_query.where(Settlement.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": s.id,
                "supplier_id": s.supplier_id,
                "supplier_name": s.supplier.name if s.supplier else None,
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
