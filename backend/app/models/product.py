"""
Product 和 PriceTier 数据模型 - 产品管理
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Product(Base):
    """产品模型"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    sku_code = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), nullable=False, default="active")

    # 关联
    prices = relationship("PriceTier", back_populates="product", cascade="all, delete-orphan")


class PriceTier(Base):
    """价格层级模型 - 三级定价（零售/店铺/区代）"""
    __tablename__ = "price_tiers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    tier_type = Column(String(20), nullable=False)  # retail/shop/agent
    price = Column(Numeric(10, 2), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关联
    product = relationship("Product", back_populates="prices")
