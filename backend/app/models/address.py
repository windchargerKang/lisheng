"""
用户地址管理数据模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UserAddress(Base):
    """用户收货地址表"""
    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 收货人信息
    receiver_name = Column(String(100), nullable=False)
    receiver_phone = Column(String(20), nullable=False)
    receiver_address = Column(String(500), nullable=False)

    # 地址详情
    province = Column(String(50), nullable=True)  # 省
    city = Column(String(50), nullable=True)      # 市
    district = Column(String(50), nullable=True)  # 区
    detail_address = Column(String(200), nullable=True)  # 详细地址

    # 标记
    is_default = Column(Boolean, default=False, nullable=False)  # 是否默认地址
    is_active = Column(Boolean, default=True, nullable=False)    # 是否启用

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关联
    user = relationship("User")
