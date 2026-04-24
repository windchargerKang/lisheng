"""
StoreApplication 数据模型 - 店铺/区代申请管理
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Enum, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class StoreApplicationStatus(str, enum.Enum):
    """申请状态"""
    PENDING = "PENDING"        # 待审核
    APPROVED = "APPROVED"      # 审核通过
    REJECTED = "REJECTED"      # 审核拒绝


class StoreApplicationType(str, enum.Enum):
    """申请类型"""
    SHOP = "SHOP"              # 店铺申请
    AGENT = "AGENT"            # 区代申请


class StoreApplication(Base):
    """申请模型 - 用户申请升级为店铺或区代"""
    __tablename__ = "store_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    apply_type = Column(Enum(StoreApplicationType), nullable=False)

    # 店铺申请字段
    shop_name = Column(String(100), nullable=True)
    shop_region_id = Column(Integer, ForeignKey("regions.id", ondelete="RESTRICT"), nullable=True)
    shop_agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    shop_latitude = Column(Numeric(10, 8), nullable=True)
    shop_longitude = Column(Numeric(11, 8), nullable=True)

    # 区代申请字段
    agent_name = Column(String(100), nullable=True)
    agent_region_id = Column(Integer, ForeignKey("regions.id", ondelete="RESTRICT"), nullable=True)
    referrer_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)

    # 审核状态
    status = Column(Enum(StoreApplicationStatus), nullable=False, default=StoreApplicationStatus.PENDING)
    reject_reason = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联
    user = relationship("User", backref="store_applications")
    shop_region = relationship("Region", foreign_keys=[shop_region_id])
    shop_agent = relationship("Agent", foreign_keys=[shop_agent_id])
    agent_region = relationship("Region", foreign_keys=[agent_region_id])
    referrer = relationship("Agent", foreign_keys=[referrer_id])
