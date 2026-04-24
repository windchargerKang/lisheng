"""
Order 数据模型 - 订单管理
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class OrderType(str, enum.Enum):
    """订单类型枚举"""
    VERIFICATION = "verification"  # 核销模式（消费者）
    ECOMMERCE = "ecommerce"        # 电商模式（店铺/区代）


class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"      # 待确认
    CONFIRMED = "confirmed"  # 待发货
    SHIPPED = "shipped"      # 已发货
    COMPLETED = "completed"  # 已完成
    VERIFIED = "verified"    # 已核销（核销模式订单）
    CANCELLED = "cancelled"  # 已取消
    PAID = "paid"            # 已支付


class Order(Base):
    """订单主表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_type = Column(String(20), nullable=False, default="ecommerce")  # 订单类型：verification/ecommerce
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    verified_at = Column(DateTime(timezone=True), nullable=True)  # 核销时间

    # 收货信息
    receiver_name = Column(String(100), nullable=True)
    receiver_phone = Column(String(20), nullable=True)
    receiver_address = Column(String(500), nullable=True)
    remark = Column(String(500), nullable=True)

    # 支付时间
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # 发货信息
    courier_company = Column(String(100), nullable=True)
    courier_no = Column(String(50), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    shipper_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关联
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    user = relationship("User", foreign_keys=[user_id])
    payment = relationship("PaymentRecord", back_populates="order", uselist=False, cascade="all, delete-orphan")
    shipper = relationship("User", foreign_keys=[shipper_id])
    verification_code = relationship("VerificationCode", back_populates="order", uselist=False, cascade="all, delete-orphan")


class OrderItem(Base):
    """订单明细表"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    # 关联
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
