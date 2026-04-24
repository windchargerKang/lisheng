"""
Referral 数据模型 - 分享追踪管理
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Referral(Base):
    """分享追踪表"""
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    referee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    referrer_type = Column(String(20), nullable=False)  # customer/shop/agent
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    referrer = relationship("User", foreign_keys=[referrer_id], backref="referrals_sent")
    referee = relationship("User", foreign_keys=[referee_id], backref="referrals_received")
