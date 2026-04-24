"""
PurchaseOrderAdjustment 数据模型 - 订单调整申请
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class AdjustmentStatus(str, enum.Enum):
    """调整申请状态枚举"""
    PENDING = "pending"      # 待审批
    APPROVED = "approved"    # 已批准
    REJECTED = "rejected"    # 已拒绝


class PurchaseOrderAdjustment(Base):
    """采购订单调整申请表"""
    __tablename__ = "purchase_order_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)  # 订单 ID
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)  # 供应商 ID
    reason = Column(String(500), nullable=False)  # 修改原因
    adjustment_items = Column(Text, nullable=True)  # 调整明细（JSON 格式）
    status = Column(Enum(AdjustmentStatus), nullable=False, default=AdjustmentStatus.PENDING)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)  # 审批时间
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 审批人 ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    order = relationship("PurchaseOrder", back_populates="adjustments")
    supplier = relationship("Supplier")
    reviewer = relationship("User")
