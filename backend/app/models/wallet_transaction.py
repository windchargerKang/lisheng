"""
WalletTransaction 数据模型 - 钱包流水管理
"""
import enum
from sqlalchemy import Column, Integer, DECIMAL, DateTime, String, ForeignKey, Index, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class TransactionType(str, enum.Enum):
    """交易类型"""
    RECHARGE = "RECHARGE"              # 充值
    WITHDRAW = "WITHDRAW"              # 提现
    ORDER_PAYMENT = "ORDER_PAYMENT"    # 订单支付
    SERVICE_FEE = "SERVICE_FEE"        # 服务费返还
    AGENT_PROFIT = "AGENT_PROFIT"      # 区代利润


class TransactionStatus(str, enum.Enum):
    """交易状态"""
    PENDING = "PENDING"  # 待审核（提现）
    APPROVED = "APPROVED"  # 审核通过（提现）
    REJECTED = "REJECTED"  # 审核拒绝（提现）
    COMPLETED = "COMPLETED"  # 已完成（充值/提现打款后）


class WalletTransaction(Base):
    """钱包流水模型"""
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)  # 交易金额
    balance_after = Column(DECIMAL(10, 2), nullable=False)  # 交易后余额
    transaction_no = Column(String(50), nullable=False, unique=True)  # 流水号
    status = Column(Enum(TransactionStatus), nullable=False)
    withdraw_method = Column(String(50), nullable=True)  # 提现方式
    withdraw_account = Column(String(100), nullable=True)  # 提现账号
    remark = Column(String(255), nullable=True)  # 备注
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    wallet = relationship("Wallet", backref="transactions")


# 索引
WalletTransaction.__table_args__ = (
    Index("idx_transactions_wallet_id", "wallet_id"),
    Index("idx_transactions_transaction_no", "transaction_no", unique=True),
    Index("idx_transactions_status", "status"),
)
