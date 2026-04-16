"""
Region 数据模型 - 区域管理
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Region(Base):
    """区域模型 - 支持树形结构"""
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False, default=1)  # 1=省，2=市，3=区
    path = Column(String(255), nullable=False)  # 如 "1/5/12"

    # 自关联
    parent = relationship("Region", remote_side=[id], backref="children")
