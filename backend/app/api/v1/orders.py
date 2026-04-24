"""
订单 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid
import time

from app.core.database import get_db
from app.models.order import Order, OrderItem, OrderStatus, OrderType
from app.models.cart import CartItem
from app.models.product import Product
from app.models.payment import PaymentRecord, PaymentStatus, PaymentMethod
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.services.order_service import OrderService

router = APIRouter()


class OrderItemRequest(BaseModel):
    """订单项请求（立即购买模式）"""
    product_id: int
    quantity: int


class OrderCreateRequest(BaseModel):
    """创建订单请求"""
    cart_item_ids: Optional[list[int]] = None  # 购物车结算模式
    items: Optional[list[OrderItemRequest]] = None  # 立即购买模式
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    receiver_address: Optional[str] = None
    remark: Optional[str] = None


class PaymentRequest(BaseModel):
    """支付请求"""
    payment_method: str  # wechat/alipay/bank
    transaction_id: Optional[str] = None


class OrderItemResponse(BaseModel):
    """订单明细响应"""
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_no: str
    total_amount: float
    status: str
    created_at: datetime
    items: list[OrderItemResponse]


@router.get("")
async def list_orders(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取订单列表"""
    from sqlalchemy.orm import selectinload

    query = select(Order).options(
        selectinload(Order.items)
    ).where(Order.user_id == current_user.id)

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
    count_query = select(func.count(Order.id)).where(Order.user_id == current_user.id)
    if status:
        count_query = count_query.where(Order.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "order_type": o.order_type,
                "total_amount": float(o.total_amount),
                "status": o.status.value,
                "created_at": o.created_at,
                "items_count": len(o.items),
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
    """获取订单详情"""
    from sqlalchemy.orm import selectinload
    from app.models.verification_code import VerificationCode

    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.verification_code)
        )
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.unique().scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return {
        "id": order.id,
        "order_no": order.order_no,
        "order_type": order.order_type,
        "total_amount": float(order.total_amount),
        "status": order.status.value,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "receiver_name": order.receiver_name,
        "receiver_phone": order.receiver_phone,
        "receiver_address": order.receiver_address,
        "remark": order.remark,
        "verification_code_obj": {
            "code": order.verification_code.code,
            "status": order.verification_code.status.value,
        } if order.verification_code else None,
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


@router.post("")
async def create_order(
    request: OrderCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建订单

    支持两种模式：
    - 购物车结算：传入 cart_item_ids
    - 立即购买：传入 items（商品 ID 和数量列表）

    根据用户角色自动设置订单类型：
    - customer → verification（核销模式，生成核销码）
    - shop/agent → ecommerce（电商模式）
    """
    order_service = OrderService(db)

    try:
        order, order_items = await order_service.create_order(
            user=current_user,
            cart_item_ids=request.cart_item_ids,
            items=[{"product_id": i.product_id, "quantity": i.quantity} for i in request.items] if request.items else None,
            receiver_name=request.receiver_name,
            receiver_phone=request.receiver_phone,
            receiver_address=request.receiver_address,
            remark=request.remark,
        )
        await db.commit()
        await db.refresh(order)

        return {
            "id": order.id,
            "order_no": order.order_no,
            "order_type": order.order_type,
            "total_amount": float(order.total_amount),
            "status": order.status.value,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新订单状态"""
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 验证状态转换
    try:
        new_status = OrderStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的订单状态")

    # 状态机转换规则
    allowed_transitions = {
        OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [OrderStatus.SHIPPED],
        OrderStatus.SHIPPED: [OrderStatus.COMPLETED],
    }

    if order.status not in allowed_transitions:
        raise HTTPException(status_code=400, detail="当前状态不允许转换")

    if new_status not in allowed_transitions.get(order.status, []):
        raise HTTPException(status_code=400, detail="不允许的状态转换")

    order.status = new_status
    await db.commit()

    return {"message": "订单状态已更新"}


class OrderAddressUpdateRequest(BaseModel):
    """订单地址更新请求"""
    receiver_name: str
    receiver_phone: str
    receiver_address: str


class OrderRemarkUpdateRequest(BaseModel):
    """订单备注更新请求"""
    remark: str


@router.put("/{order_id}/address")
async def update_order_address(
    order_id: int,
    request: OrderAddressUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新订单收货地址（仅限待确认订单）"""
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 只有待确认订单可以修改地址
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="只有待确认订单可以修改收货地址")

    order.receiver_name = request.receiver_name
    order.receiver_phone = request.receiver_phone
    order.receiver_address = request.receiver_address
    await db.commit()

    return {"message": "收货地址已更新"}


@router.put("/{order_id}/remark")
async def update_order_remark(
    order_id: int,
    request: OrderRemarkUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新订单备注（仅限待确认订单）"""
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 只有待确认订单可以修改备注
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="只有待确认订单可以修改备注")

    order.remark = request.remark
    await db.commit()

    return {"message": "订单备注已更新"}


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消订单"""
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="只有待确认订单可以取消")

    order.status = OrderStatus.CANCELLED
    await db.commit()

    return {"message": "订单已取消"}


@router.post("/{order_id}/pay")
async def pay_order(
    order_id: int,
    request: PaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """订单支付（模拟）"""
    from sqlalchemy.orm import selectinload

    # 获取订单（预加载支付记录）
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.payment))
        .where(Order.id == order_id)
    )
    order = result.unique().scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 验证订单属于当前用户
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此订单")

    # 验证订单状态
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        raise HTTPException(status_code=400, detail="订单状态不支持支付")

    # 更新订单状态
    order.status = OrderStatus.PAID
    order.paid_at = datetime.now(timezone.utc)

    # 创建支付记录
    payment = PaymentRecord(
        order_id=order_id,
        payment_method=request.payment_method,
        transaction_id=request.transaction_id or f"MOCK_{int(time.time())}",
        amount=order.total_amount,
        status=PaymentStatus.SUCCESS,
    )
    db.add(payment)

    await db.commit()

    return {"message": "支付成功", "order_id": order_id}


@router.post("/{order_id}/confirm")
async def confirm_receipt(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """确认订单并支付

    核销模式（customer）：待确认 → 钱包扣款 → 已完成（生成核销码）
    电商模式（shop/agent）：待确认 → 钱包扣款 → 待发货
    """
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 待确认订单：钱包扣款
    if order.status == OrderStatus.PENDING:
        order_service = OrderService(db)
        try:
            updated_order = await order_service.confirm_order(order_id, current_user)
            await db.commit()

            # 根据订单类型返回不同的状态
            if order.order_type == OrderType.VERIFICATION.value:
                return {
                    "message": "订单确认成功",
                    "order_id": order_id,
                    "status": updated_order.status.value,
                }
            else:
                # 电商模式：支付后进入待发货状态
                return {
                    "message": "订单支付成功",
                    "order_id": order_id,
                    "status": updated_order.status.value,
                }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # 电商模式已发货订单：确认收货
    if order.order_type == OrderType.ECOMMERCE and order.status == OrderStatus.SHIPPED:
        order.status = OrderStatus.COMPLETED
        await db.commit()

        return {
            "message": "确认收货成功",
            "order_id": order_id,
            "status": order.status.value,
        }

    # 其他情况
    raise HTTPException(
        status_code=400,
        detail=f"当前订单状态不支持确认操作，状态：{order.status.value}"
    )
