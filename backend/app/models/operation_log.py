"""
OperationLog 数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class OperationLog(Base):
    """操作日志模型"""
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # LOGIN, CREATE, DELETE, UPDATE
    resource_type = Column(String(50), nullable=True)  # USER, ROLE, ORDER
    resource_id = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", back_populates="operation_logs")

    # 索引
    __table_args__ = (
        Index("idx_user_action", "user_id", "action"),
        Index("idx_created_at", "created_at"),
    )
