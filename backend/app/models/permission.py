"""
Permission 数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PermissionType(str, enum.Enum):
    """权限类型"""
    MENU = "MENU"
    BUTTON = "BUTTON"
    DATA = "DATA"


class Permission(Base):
    """权限模型"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # 权限名称
    code = Column(String(100), unique=True, nullable=False)  # 权限代码：user:view, role:edit
    type = Column(Enum(PermissionType), nullable=False)
    parent_id = Column(Integer, ForeignKey("permissions.id"), nullable=True)  # 父权限 ID
    api_path = Column(String(200), nullable=True)  # 对应的 API 路径
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan", overlaps="permissions,role_permissions")
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions", overlaps="role_permissions,permissions")
    children = relationship("Permission", remote_side=[parent_id])
