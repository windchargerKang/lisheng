"""
Shop 数据模型 - 店铺管理
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.core.database import Base


class Shop(Base):
    """店铺模型"""
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)  # 绑定区代
    name = Column(String(100), nullable=True)  # 店铺名称
    status = Column(String(20), nullable=False, default="active")
    latitude = Column(Numeric(10, 8), nullable=True)  # 店铺纬度
    longitude = Column(Numeric(11, 8), nullable=True)  # 店铺经度

    # 关联
    region = relationship("Region")
    agent = relationship("Agent", backref="shops")
