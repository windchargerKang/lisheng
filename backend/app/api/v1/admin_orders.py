"""
运营管理端订单 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from typing import Optional

from app.core.database import get_db
from app.models.order import Order, OrderStatus, OrderItem
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.schemas.order import OrderShipRequest, AdminOrderResponse, AdminOrderDetailResponse, OrderShipResponse

router = APIRouter()


@router.get("")
async def list_orders(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理端订单列表（支持状态筛选、分页）"""
    # 验证管理员权限
    if current_user.role_type not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="权限不足")

    query = select(Order).options(
        selectinload(Order.items)
    )

    if status:
        query = query.where(Order.status == status)

    # 按创建时间倒序
    query = query.order_by(Order.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    orders = result.unique().scalars().all()

    # 获取总数
    count_query = select(func.count(Order.id))
    if status:
        count_query = count_query.where(Order.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "user_id": o.user_id,
                "total_amount": float(o.total_amount),
                "status": o.status.value,
                "receiver_name": o.receiver_name,
                "receiver_phone": o.receiver_phone,
                "receiver_address": o.receiver_address,
                "courier_company": o.courier_company,
                "courier_no": o.courier_no,
                "shipped_at": o.shipped_at,
                "created_at": o.created_at,
            }
            for o in orders
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{order_id}")
async def get_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理端订单详情"""
    # 验证管理员权限
    if current_user.role_type not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="权限不足")

    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.id == order_id)
    )
    order = result.unique().scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return {
        "id": order.id,
        "order_no": order.order_no,
        "user_id": order.user_id,
        "total_amount": float(order.total_amount),
        "status": order.status.value,
        "receiver_name": order.receiver_name,
        "receiver_phone": order.receiver_phone,
        "receiver_address": order.receiver_address,
        "remark": order.remark,
        "courier_company": order.courier_company,
        "courier_no": order.courier_no,
        "shipped_at": order.shipped_at,
        "shipper_id": order.shipper_id,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else "",
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.subtotal),
            }
            for item in order.items
        ],
    }


@router.post("/{order_id}/ship")
async def ship_order(
    order_id: int,
    request: OrderShipRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """订单发货操作"""
    # 验证管理员权限
    if current_user.role_type not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="权限不足")

    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 验证订单状态（只有待发货订单可以发货）
    if order.status != OrderStatus.CONFIRMED:
        raise HTTPException(
            status_code=400,
            detail=f"只有待发货订单可以执行发货操作，当前状态：{order.status.value}"
        )

    # 更新订单状态和物流信息
    order.status = OrderStatus.SHIPPED
    order.courier_company = request.courier_company
    order.courier_no = request.courier_no
    order.shipped_at = datetime.now(timezone.utc)
    order.shipper_id = current_user.id

    await db.commit()
    await db.refresh(order)

    return {
        "id": order.id,
        "order_no": order.order_no,
        "status": order.status.value,
        "courier_company": order.courier_company,
        "courier_no": order.courier_no,
        "shipped_at": order.shipped_at,
    }
