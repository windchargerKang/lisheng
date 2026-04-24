"""
User 数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserStatus(str, enum.Enum):
    """用户状态"""
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)  # 手机号（支持手机号登录）
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)  # RBAC 角色 ID
    supplier_id = Column(Integer, nullable=True)  # 关联供应商 ID（仅 supplier 角色需要）
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    role = relationship("Role", back_populates="users", lazy="selectin")
    operation_logs = relationship("OperationLog", back_populates="user")
    wallet = relationship("Wallet", back_populates="user", uselist=False)  # 钱包关系（一对一）

    @property
    def role_type(self) -> str:
        """兼容属性：从 role.code 获取角色类型"""
        return self.role.code if self.role else "customer"


# 添加索引
User.__table_args__ = (
    Index("idx_role_id", "role_id"),
    Index("idx_status", "status"),
)
