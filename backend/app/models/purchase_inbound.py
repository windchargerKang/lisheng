"""
PurchaseInbound 和 Settlement 数据模型 - 入库和结算管理
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class InboundStatus(str, enum.Enum):
    """入库状态枚举"""
    COMPLETED = "completed"  # 已完成


class SettlementType(str, enum.Enum):
    """结算类型枚举"""
    CASH = "cash"      # 现款
    CREDIT = "credit"  # 账期


class SettlementStatus(str, enum.Enum):
    """结算状态枚举"""
    PAID = "paid"  # 已付款


class PurchaseInbound(Base):
    """采购入库记录表"""
    __tablename__ = "purchase_inbounds"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    warehouse_operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 入库操作人 ID
    total_quantity = Column(Integer, nullable=False, default=0)  # 入库总数量
    status = Column(Enum(InboundStatus), nullable=False, default=InboundStatus.COMPLETED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    order = relationship("PurchaseOrder", back_populates="inbounds")


class Settlement(Base):
    """结算记录表"""
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, unique=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)  # 结算金额
    type = Column(Enum(SettlementType), nullable=False, default=SettlementType.CASH)
    status = Column(Enum(SettlementStatus), nullable=False, default=SettlementStatus.PAID)
    paid_at = Column(DateTime(timezone=True), nullable=True)  # 付款时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    supplier = relationship("Supplier")
    order = relationship("PurchaseOrder", back_populates="settlement")
