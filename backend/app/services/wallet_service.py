"""
钱包管理服务
"""
from typing import Optional, List, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction, TransactionType, TransactionStatus
from app.models.user import User


class WalletLockError(Exception):
    """钱包锁定失败异常"""
    pass


class WalletService:
    """钱包服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_wallet_by_user_id(self, user_id: int) -> Optional[Wallet]:
        """根据用户 ID 获取钱包"""
        result = await self.db.execute(select(Wallet).where(Wallet.user_id == user_id))
        return result.scalar_one_or_none()

    async def create_wallet(self, user_id: int) -> Wallet:
        """创建钱包（用户注册时自动创建）"""
        # 检查是否已存在
        existing = await self.get_wallet_by_user_id(user_id)
        if existing:
            return existing

        wallet = Wallet(user_id=user_id, balance=Decimal("0.00"))
        self.db.add(wallet)
        await self.db.flush()  # 获取 ID 但不提交
        return wallet

    async def recharge(
        self,
        user_id: int,
        amount: Decimal,
        remark: str
    ) -> Tuple[Wallet, WalletTransaction]:
        """
        充值（管理员操作）
        返回：钱包和流水记录
        """
        # 获取钱包
        wallet = await self.get_wallet_by_user_id(user_id)
        if not wallet:
            raise ValueError("用户钱包不存在")

        # 生成流水号
        transaction_no = await self._generate_transaction_no(TransactionType.RECHARGE)

        # 计算新余额
        new_balance = wallet.balance + amount

        # 创建流水记录
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=TransactionType.RECHARGE,
            amount=amount,
            balance_after=new_balance,
            transaction_no=transaction_no,
            status=TransactionStatus.COMPLETED,
            remark=remark
        )

        # 更新钱包余额
        wallet.balance = new_balance

        self.db.add(transaction)
        await self.db.flush()

        return wallet, transaction

    async def _get_pending_withdraw_total(self, wallet_id: int) -> Decimal:
        """获取待审核提现总额（PENDING 状态的提现申请总和）"""
        result = await self.db.execute(
            select(func.sum(WalletTransaction.amount)).where(
                WalletTransaction.wallet_id == wallet_id,
                WalletTransaction.transaction_type == TransactionType.WITHDRAW,
                WalletTransaction.status == TransactionStatus.PENDING
            )
        )
        return result.scalar() or Decimal("0.00")

    async def _get_wallet_with_lock(self, user_id: int) -> Wallet:
        """使用 FOR UPDATE 锁定钱包记录（防止并发）"""
        result = await self.db.execute(
            select(Wallet).where(Wallet.user_id == user_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def withdraw(
        self,
        user_id: int,
        amount: Decimal,
        withdraw_method: str,
        withdraw_account: str,
        remark: str
    ) -> Tuple[Wallet, WalletTransaction]:
        """
        申请提现（用户操作）
        返回：钱包和流水记录

        注意：此方法必须在事务中调用，调用方需要负责锁定钱包记录
        """
        # 使用 FOR UPDATE 锁定钱包记录（防止并发提现）
        wallet = await self._get_wallet_with_lock(user_id)
        if not wallet:
            raise ValueError("用户钱包不存在")

        # 计算可用余额 = 钱包余额 - 待审核提现总额
        pending_total = await self._get_pending_withdraw_total(wallet.id)
        available_balance = wallet.balance - pending_total

        # 检查可用余额是否充足
        if available_balance < amount:
            raise ValueError("可用余额不足（当前余额：{}，待审核提现：{}）".format(
                wallet.balance, pending_total
            ))

        # 生成流水号
        transaction_no = await self._generate_transaction_no(TransactionType.WITHDRAW)

        # 创建流水记录（状态为待审核，此时不扣减余额）
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=TransactionType.WITHDRAW,
            amount=amount,
            balance_after=wallet.balance,  # 提现申请时余额不变
            transaction_no=transaction_no,
            status=TransactionStatus.PENDING,
            withdraw_method=withdraw_method,
            withdraw_account=withdraw_account,
            remark=remark
        )

        self.db.add(transaction)
        await self.db.flush()

        return wallet, transaction

    async def approve_withdraw(
        self,
        transaction_id: int,
        approved: bool
    ) -> Tuple[Wallet, WalletTransaction]:
        """
        审核提现（管理员操作）
        approved: True 通过，False 拒绝
        返回：钱包和流水记录
        """
        # 获取流水记录
        result = await self.db.execute(
            select(WalletTransaction)
            .options(selectinload(WalletTransaction.wallet))
            .where(WalletTransaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            raise ValueError("提现记录不存在")

        if transaction.status != TransactionStatus.PENDING:
            raise ValueError("提现记录状态不正确")

        wallet = transaction.wallet

        if approved:
            # 审核通过：扣减余额，状态改为已完成
            if wallet.balance < transaction.amount:
                raise ValueError("余额不足，无法完成提现")

            new_balance = wallet.balance - transaction.amount
            wallet.balance = new_balance
            transaction.balance_after = new_balance
            transaction.status = TransactionStatus.COMPLETED
        else:
            # 审核拒绝：状态改为已拒绝，不扣减余额
            transaction.status = TransactionStatus.REJECTED

        await self.db.flush()

        return wallet, transaction

    async def get_transactions(
        self,
        wallet_id: int,
        page: int = 1,
        page_size: int = 10,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> dict:
        """
        查询流水记录
        """
        # 构建查询条件
        conditions = [WalletTransaction.wallet_id == wallet_id]
        if transaction_type:
            conditions.append(WalletTransaction.transaction_type == transaction_type)
        if status:
            conditions.append(WalletTransaction.status == status)

        # 查询总数
        count_query = select(func.count()).select_from(WalletTransaction)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # 查询列表
        query = (
            select(WalletTransaction)
            .where(and_(*conditions))
            .order_by(WalletTransaction.created_at.desc())
        )

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        transactions = result.scalars().all()

        return {
            "items": transactions,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_all_wallets(
        self,
        page: int = 1,
        page_size: int = 10,
        user_id: Optional[int] = None
    ) -> dict:
        """
        查询所有钱包（管理员）- 返回钱包和关联的用户信息
        """
        # 构建查询条件
        conditions = []
        if user_id:
            conditions.append(Wallet.user_id == user_id)

        # 查询总数
        count_query = select(func.count()).select_from(Wallet)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # 查询列表（JOIN 用户表获取用户名）
        query = (
            select(Wallet, User.username)
            .join(User, Wallet.user_id == User.id)
            .order_by(Wallet.created_at.desc())
        )
        if conditions:
            query = query.where(and_(*conditions))

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        rows = result.all()

        return {
            "items": [
                {
                    "id": wallet.id,
                    "user_id": wallet.user_id,
                    "username": username,
                    "balance": wallet.balance,
                    "created_at": wallet.created_at,
                    "updated_at": wallet.updated_at,
                }
                for wallet, username in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_all_transactions(
        self,
        page: int = 1,
        page_size: int = 10,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> dict:
        """
        查询所有流水记录（管理员）
        """
        # 构建查询条件
        conditions = []
        if transaction_type:
            conditions.append(WalletTransaction.transaction_type == transaction_type)
        if status:
            conditions.append(WalletTransaction.status == status)

        # 查询总数
        count_query = select(func.count()).select_from(WalletTransaction)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # 查询列表
        query = (
            select(WalletTransaction)
            .options(selectinload(WalletTransaction.wallet))
            .where(and_(*conditions) if conditions else True)
            .order_by(WalletTransaction.created_at.desc())
        )

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        transactions = result.scalars().all()

        return {
            "items": transactions,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def _generate_transaction_no(self, transaction_type: TransactionType) -> str:
        """
        生成流水号
        格式：{R/W}{YYYY-MM-DD}{4 位序号}
        """
        # 获取今日前缀（使用带横杠的格式，与数据库 date() 函数返回格式一致）
        today = datetime.now().strftime("%Y-%m-%d")
        prefix = "R" if transaction_type == TransactionType.RECHARGE else "W"

        # 查询今日已有流水数
        result = await self.db.execute(
            select(func.count()).select_from(WalletTransaction).where(
                WalletTransaction.transaction_type == transaction_type,
                func.date(WalletTransaction.created_at) == today
            )
        )
        count = result.scalar() or 0

        # 生成序号（4 位，从 0001 开始）
        sequence = count + 1

        # 流水号使用无横杠格式
        today_compact = datetime.now().strftime("%Y%m%d")
        return f"{prefix}{today_compact}{sequence:04d}"
