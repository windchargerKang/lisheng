"""
Payment 数据模型 - 支付记录
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    """支付状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class PaymentMethod(str, enum.Enum):
    """支付方式枚举"""
    WECHAT = "wechat"
    ALIPAY = "alipay"
    BANK = "bank"


class PaymentRecord(Base):
    """支付记录表"""
    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True, unique=True)
    payment_method = Column(String(20), nullable=False)
    transaction_id = Column(String(64), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.SUCCESS)
    paid_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    order = relationship("Order", back_populates="payment")
