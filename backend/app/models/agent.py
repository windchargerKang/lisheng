"""
Agent 数据模型 - 区代管理
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Agent(Base):
    """区代模型 - 一个区代只能管理一个区域"""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), unique=True, nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="RESTRICT"), unique=True, nullable=False)
    referrer_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)  # 推荐区代
    name = Column(String(100), nullable=True)  # 区代名称
    status = Column(String(20), nullable=False, default="active")

    # 关联
    region = relationship("Region")
    referrer = relationship("Agent", remote_side=[id], backref="referrals")
