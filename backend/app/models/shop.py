"""
Shop 数据模型 - 店铺管理
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Shop(Base):
    """店铺模型"""
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False)
    referrer_id = Column(Integer, ForeignKey("shops.id", ondelete="SET NULL"), nullable=True)  # 推荐店铺
    status = Column(String(20), nullable=False, default="active")

    # 关联
    region = relationship("Region")
    referrer = relationship("Shop", remote_side=[id], backref="referrals")
