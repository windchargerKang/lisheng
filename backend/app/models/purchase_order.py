"""
PurchaseOrder 和 PurchaseOrderItem 数据模型 - 采购订单管理
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class PurchaseOrderStatus(str, enum.Enum):
    """采购订单状态枚举"""
    PENDING = "pending"      # 待确认
    CONFIRMED = "confirmed"  # 已确认
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class SupplierConfirmStatus(str, enum.Enum):
    """供应商确认状态枚举"""
    PENDING = "pending"      # 待确认
    CONFIRMED = "confirmed"  # 已确认供货
    REJECTED = "rejected"    # 已拒绝/申请修改


class PurchaseOrder(Base):
    """采购订单主表"""
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, index=True, nullable=False)  # 订单号
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)  # 供应商 ID
    purchaser_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 采购员 ID
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)  # 订单总额
    status = Column(Enum(PurchaseOrderStatus), nullable=False, default=PurchaseOrderStatus.PENDING)
    supplier_confirm_status = Column(Enum(SupplierConfirmStatus), nullable=True)  # 供应商确认状态
    remark = Column(String(255), nullable=True)  # 备注
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)  # 确认时间（运营端确认）
    supplier_confirmed_at = Column(DateTime(timezone=True), nullable=True)  # 供应商确认时间

    # 关联
    supplier = relationship("Supplier")
    purchaser = relationship("User")
    items = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")
    inbounds = relationship("PurchaseInbound", back_populates="order", cascade="all, delete-orphan")
    settlement = relationship("Settlement", back_populates="order", uselist=False, cascade="all, delete-orphan")
    adjustments = relationship("PurchaseOrderAdjustment", back_populates="order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    """采购订单明细表"""
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)  # 采购数量
    cost_price = Column(Numeric(10, 2), nullable=False)  # 采购单价
    subtotal = Column(Numeric(10, 2), nullable=False)  # 小计

    # 关联
    order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")
