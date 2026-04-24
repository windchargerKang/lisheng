"""
ProfitRecord 和 WithdrawalRequest 数据模型 - 收益和提现管理
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ProfitStatus(str, enum.Enum):
    """分润状态枚举"""
    PENDING = "pending"    # 待结算
    PAID = "paid"          # 已结算
    WITHDRAWN = "withdrawn"  # 已提现


class WithdrawalStatus(str, enum.Enum):
    """提现状态枚举"""
    PENDING = "pending"    # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝


class ProfitRecord(Base):
    """分润记录表"""
    __tablename__ = "profit_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(Enum(ProfitStatus), nullable=False, default=ProfitStatus.PENDING)
    remark = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    user = relationship("User")
    order = relationship("Order")


class WithdrawalRequest(Base):
    """提现申请表"""
    __tablename__ = "withdrawal_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(WithdrawalStatus), nullable=False, default=WithdrawalStatus.PENDING)
    remark = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关联
    user = relationship("User")
