"""
分润管理服务
"""
import json
import os
from decimal import Decimal
from typing import Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction, TransactionType, TransactionStatus
from app.models.user import User
from app.models.order import Order
from app.models.shop import Shop
from app.models.agent import Agent


class ProfitService:
    """分润服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._config = None
        self._lisheng_user_id = None

    def _load_config(self) -> dict:
        """加载分润配置文件"""
        if self._config is not None:
            return self._config

        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            # 默认配置
            self._config = {
                "profit": {
                    "service_fee_rate": 0.30,
                    "agent_profit_rate": 0.10
                },
                "system_account": {
                    "username": "lisheng"
                }
            }
        return self._config

    async def _get_lisheng_user_id(self) -> int:
        """获取 lisheng 账号的 user_id"""
        if self._lisheng_user_id is not None:
            return self._lisheng_user_id

        config = self._load_config()
        username = config.get("system_account", {}).get("username", "lisheng")

        result = await self.db.execute(
            select(User.id).where(User.username == username)
        )
        user_id = result.scalar_one_or_none()

        if not user_id:
            raise ValueError(f"系统账号 '{username}' 不存在")

        self._lisheng_user_id = user_id
        return user_id

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

    def _calculate_profit(self, order_amount: Decimal) -> Tuple[Decimal, Decimal]:
        """
        计算分润金额

        Returns:
            (service_fee, agent_profit) 元组
        """
        config = self._load_config()
        profit_config = config.get("profit", {})

        service_fee_rate = Decimal(str(profit_config.get("service_fee_rate", 0.30)))
        agent_profit_rate = Decimal(str(profit_config.get("agent_profit_rate", 0.10)))

        # 计算分润金额（四舍五入到分，使用 ROUND_HALF_UP）
        from decimal import ROUND_HALF_UP
        service_fee = (order_amount * service_fee_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        agent_profit = (order_amount * agent_profit_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return service_fee, agent_profit

    async def _create_transaction(
        self,
        wallet_id: int,
        transaction_type: TransactionType,
        amount: Decimal,
        balance_after: Decimal,
        remark: str
    ) -> WalletTransaction:
        """创建钱包流水"""
        # 生成流水号：{类型首字母}{YYYYMMDDHHmmss}{4 位随机数}
        import datetime
        import random
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        sequence = random.randint(1000, 9999)
        transaction_no = f"{transaction_type.value[:1]}{timestamp}{sequence}"

        transaction = WalletTransaction(
            wallet_id=wallet_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=balance_after,
            transaction_no=transaction_no,
            status=TransactionStatus.COMPLETED,
            remark=remark
        )
        self.db.add(transaction)
        await self.db.flush()

        return transaction

    async def distribute_profit(
        self,
        order: Order,
        verifier_user_id: int
    ) -> Tuple[Decimal, Decimal]:
        """
        执行分润转账

        流程：
        1. 计算分润金额（服务费 30%，区代利润 10%）
        2. 从 lisheng 钱包扣除服务费 → 转入店铺钱包
        3. 从 lisheng 钱包扣除区代利润 → 转入区代钱包

        Args:
            order: 订单对象
            verifier_user_id: 核销店铺 user_id

        Returns:
            (service_fee, agent_profit) 分润金额元组

        Raises:
            ValueError: 分润执行失败
        """
        # 二次验证核销码状态已在 verify_and_use 中完成，此处不再重复检查
        # 避免触发 lazy loading 导致异步错误

        # 获取店铺信息（包含绑定的区代）
        shop_result = await self.db.execute(
            select(Shop)
            .where(Shop.user_id == verifier_user_id)
        )
        shop = shop_result.scalar_one_or_none()

        if not shop:
            raise ValueError("核销店铺信息不存在")

        # 获取 lisheng 账号
        lisheng_user_id = await self._get_lisheng_user_id()

        # 获取钱包
        lisheng_wallet = await self._get_wallet_by_user_id(lisheng_user_id)
        shop_wallet = await self._get_wallet_by_user_id(verifier_user_id)

        # 计算分润金额
        service_fee, agent_profit = self._calculate_profit(order.total_amount)

        # 检查 lisheng 余额是否充足
        total_profit = service_fee + agent_profit
        if lisheng_wallet.balance < total_profit:
            raise ValueError(
                f"lisheng 账号余额不足（当前：{lisheng_wallet.balance}，需要：{total_profit}）"
            )

        # 1. 发放服务费给店铺
        lisheng_wallet.balance -= service_fee
        shop_wallet.balance += service_fee

        # 创建服务费流水
        await self._create_transaction(
            wallet_id=lisheng_wallet.id,
            transaction_type=TransactionType.SERVICE_FEE,
            amount=-service_fee,
            balance_after=lisheng_wallet.balance,
            remark=f"订单{order.order_no}核销 - 服务费支出"
        )
        await self._create_transaction(
            wallet_id=shop_wallet.id,
            transaction_type=TransactionType.SERVICE_FEE,
            amount=service_fee,
            balance_after=shop_wallet.balance,
            remark=f"订单{order.order_no}核销 - 服务费收入"
        )

        # 2. 发放区代利润给区代（如果有绑定区代）
        if shop.agent_id:
            agent_result = await self.db.execute(
                select(Agent).where(Agent.id == shop.agent_id)
            )
            agent = agent_result.scalar_one_or_none()

            if agent:
                agent_wallet = await self._get_wallet_by_user_id(agent.user_id)
                lisheng_wallet.balance -= agent_profit
                agent_wallet.balance += agent_profit

                # 创建区代利润流水
                await self._create_transaction(
                    wallet_id=lisheng_wallet.id,
                    transaction_type=TransactionType.AGENT_PROFIT,
                    amount=-agent_profit,
                    balance_after=lisheng_wallet.balance,
                    remark=f"订单{order.order_no}核销 - 区代利润支出"
                )
                await self._create_transaction(
                    wallet_id=agent_wallet.id,
                    transaction_type=TransactionType.AGENT_PROFIT,
                    amount=agent_profit,
                    balance_after=agent_wallet.balance,
                    remark=f"订单{order.order_no}核销 - 区代利润收入"
                )
        else:
            # 没有绑定区代，区代利润不发放（留在 lisheng 账号）
            pass

        await self.db.flush()

        return service_fee, agent_profit
