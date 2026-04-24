"""
Wallet 数据模型 - 用户钱包管理
"""
from sqlalchemy import Column, Integer, DECIMAL, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Wallet(Base):
    """用户钱包模型"""
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, unique=True)  # 用户 ID，唯一索引
    balance = Column(DECIMAL(10, 2), nullable=False, default=0.00)  # 余额，单位：元
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="wallet")
