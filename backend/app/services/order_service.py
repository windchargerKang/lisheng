"""
订单管理服务
"""
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderStatus, OrderType
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction, TransactionType, TransactionStatus
from app.services.verification_code_service import VerificationCodeService


class OrderService:
    """订单服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _generate_order_no(self) -> str:
        """生成订单号"""
        import datetime
        import uuid

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:4].upper()
        return f"ORD{timestamp}{unique_id}"

    async def _get_wallet_by_user_id(self, user_id: int) -> Wallet:
        """获取用户钱包（不存在则创建）"""
        result = await self.db.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        wallet = result.scalar_one_or_none()

        if not wallet:
            wallet = Wallet(user_id=user_id, balance=Decimal("0.00"))
            self.db.add(wallet)
            await self.db.flush()

        return wallet

    async def create_order(
        self,
        user: User,
        cart_item_ids: Optional[List[int]] = None,
        items: Optional[List[dict]] = None,  # 立即购买模式：[{product_id, quantity}, ...]
        receiver_name: Optional[str] = None,
        receiver_phone: Optional[str] = None,
        receiver_address: Optional[str] = None,
        remark: Optional[str] = None
    ) -> Tuple[Order, List[OrderItem]]:
        """
        创建订单

        根据用户角色自动设置订单类型：
        - customer → verification（核销模式，生成核销码）
        - shop/agent → ecommerce（电商模式）

        Args:
            user: 当前用户
            cart_item_ids: 购物车项 ID 列表（购物车结算模式）
            items: 商品列表，格式：[{product_id, quantity}, ...]（立即购买模式）
            receiver_name: 收货人姓名
            receiver_phone: 收货人电话
            receiver_address: 收货地址
            remark: 订单备注

        Returns:
            (Order, List[OrderItem]) 元组

        Raises:
            ValueError: 购物车为空或商品库存不足
        """
        # 判断模式：购物车结算 or 立即购买
        is_buy_now_mode = items is not None and len(items) > 0

        if is_buy_now_mode:
            # 立即购买模式：直接使用传入的商品列表
            cart_items = []
            # 获取商品信息
            product_ids = [item['product_id'] for item in items]
            product_result = await self.db.execute(
                select(Product)
                .options(selectinload(Product.prices))
                .where(Product.id.in_(product_ids))
            )
            products = {p.id: p for p in product_result.scalars().all()}

            # 验证商品并准备数据
            for item in items:
                product = products.get(item['product_id'])
                if not product:
                    raise ValueError(f"商品 {item['product_id']} 不存在")
                if product.stock < item['quantity']:
                    raise ValueError(f"商品 {product.name} 库存不足")
        else:
            # 购物车结算模式
            if not cart_item_ids:
                raise ValueError("请选择要结算的商品")

            # 获取购物车项
            cart_result = await self.db.execute(
                select(CartItem)
                .where(CartItem.id.in_(cart_item_ids))
                .where(CartItem.user_id == user.id)
            )
            cart_items = cart_result.scalars().all()

            if not cart_items:
                raise ValueError("请选择要结算的商品")

        # 生成订单号
        order_no = await self._generate_order_no()

        # 计算总金额，准备订单项数据
        total_amount = Decimal("0.00")
        order_items_data = []

        if is_buy_now_mode:
            # 立即购买模式：使用传入的商品列表
            for item in items:
                product = products.get(item['product_id'])
                # 根据用户角色获取对应层级价格
                user_tier = user.role.code if user and user.role else "retail"
                tier_price = next((p for p in product.prices if p.tier_type == user_tier), None)
                price = Decimal(str(tier_price.price)) if tier_price else Decimal(str(product.prices[0].price))
                subtotal = price * item['quantity']
                total_amount += subtotal

                order_items_data.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "quantity": item['quantity'],
                    "unit_price": price,
                    "subtotal": subtotal,
                })
        else:
            # 购物车结算模式
            for cart_item in cart_items:
                # 获取产品信息（预加载价格）
                product_result = await self.db.execute(
                    select(Product)
                    .options(selectinload(Product.prices))
                    .where(Product.id == cart_item.product_id)
                )
                product = product_result.scalar_one_or_none()

                if not product:
                    raise ValueError(f"商品 {cart_item.product_id} 不存在")

                if product.stock < cart_item.quantity:
                    raise ValueError(f"商品 {product.name} 库存不足")

                # 根据用户角色获取对应层级价格
                user_tier = user.role.code if user and user.role else "retail"
                tier_price = next((p for p in product.prices if p.tier_type == user_tier), None)
                price = Decimal(str(tier_price.price)) if tier_price else Decimal(str(product.prices[0].price))
                subtotal = price * cart_item.quantity
                total_amount += subtotal

                order_items_data.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "quantity": cart_item.quantity,
                    "unit_price": price,
                    "subtotal": subtotal,
                })

        # 根据用户角色设置订单类型
        # customer → verification（核销模式）
        # shop/agent/admin/operator/supplier → ecommerce（电商模式）
        # 使用 user.role_type 兼容属性（从 role.code 获取）
        order_type = OrderType.VERIFICATION if user.role_type == "customer" else OrderType.ECOMMERCE

        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=user.id,
            order_type=order_type.value,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            receiver_address=receiver_address,
            remark=remark,
        )
        self.db.add(order)
        await self.db.flush()

        # 创建订单项
        order_items = []
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                subtotal=item_data["subtotal"],
            )
            self.db.add(order_item)
            order_items.append(order_item)

        # 删除已结算的购物车项
        for cart_item in cart_items:
            await self.db.delete(cart_item)

        await self.db.flush()

        return order, order_items

    async def confirm_order(
        self,
        order_id: int,
        user: User
    ) -> Order:
        """
        确认订单（从用户钱包扣款）

        流程：
        1. 检查订单状态为 pending
        2. 检查用户钱包余额充足
        3. 用户钱包 - 订单金额（ORDER_PAYMENT）
        4. lisheng 钱包 + 订单金额（ORDER_PAYMENT）
        5. 订单状态 → completed

        Args:
            order_id: 订单 ID
            user: 当前用户（订单所有者）

        Returns:
            Order 订单对象

        Raises:
            ValueError: 订单不存在/状态不正确/余额不足
        """
        # 获取订单
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order_id)
            .where(Order.user_id == user.id)
        )
        order = result.scalar_one_or_none()

        if not order:
            raise ValueError("订单不存在")

        if order.status != OrderStatus.PENDING:
            raise ValueError(f"订单状态不正确，当前状态：{order.status.value}")

        # 获取用户钱包
        user_wallet = await self._get_wallet_by_user_id(user.id)

        # 检查余额
        if user_wallet.balance < order.total_amount:
            raise ValueError(
                f"钱包余额不足（订单金额：{order.total_amount}，当前余额：{user_wallet.balance}）"
            )

        # 获取 lisheng 账号钱包
        from app.models.user import User as UserModel
        lisheng_result = await self.db.execute(
            select(UserModel.id).where(UserModel.username == "lisheng")
        )
        lisheng_user_id = lisheng_result.scalar_one_or_none()

        if not lisheng_user_id:
            raise ValueError("系统账号 lisheng 不存在")

        lisheng_wallet = await self._get_wallet_by_user_id(lisheng_user_id)

        # 扣款
        user_wallet.balance -= order.total_amount
        lisheng_wallet.balance += order.total_amount

        # 创建用户钱包流水
        user_transaction = WalletTransaction(
            wallet_id=user_wallet.id,
            transaction_type=TransactionType.ORDER_PAYMENT,
            amount=-order.total_amount,
            balance_after=user_wallet.balance,
            transaction_no=f"OP{order.order_no}",
            status=TransactionStatus.COMPLETED,
            remark=f"订单{order.order_no}支付"
        )
        self.db.add(user_transaction)

        # 创建 lisheng 钱包流水
        lisheng_transaction = WalletTransaction(
            wallet_id=lisheng_wallet.id,
            transaction_type=TransactionType.ORDER_PAYMENT,
            amount=order.total_amount,
            balance_after=lisheng_wallet.balance,
            transaction_no=f"OR{order.order_no}",
            status=TransactionStatus.COMPLETED,
            remark=f"订单{order.order_no}收入"
        )
        self.db.add(lisheng_transaction)

        # 更新订单状态：根据订单类型设置不同状态
        # 核销模式：支付后直接完成（待核销）
        # 电商模式：支付后待发货
        if order.order_type == OrderType.VERIFICATION.value:
            order.status = OrderStatus.COMPLETED
            # 生成核销码
            verification_service = VerificationCodeService(self.db)
            await verification_service.generate_verification_code(order.id)
        else:
            order.status = OrderStatus.CONFIRMED

        await self.db.flush()

        return order
