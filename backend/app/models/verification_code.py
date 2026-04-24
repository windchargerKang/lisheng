"""
VerificationCode 数据模型 - 核销码管理
"""
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class VerificationCodeStatus(str, enum.Enum):
    """核销码状态"""
    UNUSED = "unused"  # 未使用
    USED = "used"      # 已使用


class VerificationCode(Base):
    """核销码模型"""
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(12), unique=True, index=True, nullable=False)  # 12 位核销码
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    status = Column(Enum(VerificationCodeStatus), nullable=False, default=VerificationCodeStatus.UNUSED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 核销店铺 user_id

    # 关联
    order = relationship("Order", back_populates="verification_code")
    verifier = relationship("User", foreign_keys=[verified_by])


# 索引
VerificationCode.__table_args__ = (
    Index("idx_verification_code_code", "code", unique=True),
    Index("idx_verification_code_order_id", "order_id"),
    Index("idx_verification_code_status", "status"),
)
