"""
RolePermission 数据模型
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class RolePermission(Base):
    """角色权限关联模型"""
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 唯一约束
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="unique_role_permission"),
    )

    # 关系
    role = relationship("Role", back_populates="role_permissions", overlaps="permissions,roles")
    permission = relationship("Permission", back_populates="role_permissions", overlaps="permissions,roles")


# 添加到 Role 和 Permission 模型的关系引用
# 在 Role 模型中：role_permissions = relationship("RolePermission", back_populates="role")
# 在 Permission 模型中：role_permissions = relationship("RolePermission", back_populates="permission")
