"""
Product 和 PriceTier 数据模型 - 产品管理
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON

from app.core.database import Base


class Product(Base):
    """产品模型"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    sku_code = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), nullable=False, default="active")
    image = Column(String(255), nullable=True)  # 商品图片 URL（旧字段，保留兼容）
    image_url = Column(String(500), nullable=True)  # 产品主图 URL（新字段）
    images = Column(JSON, nullable=True)  # 产品多图 JSON 数组 ["url1", "url2", ...]
    description = Column(String(255), nullable=True)  # 商品简述
    detail = Column(Text, nullable=True)  # 商品详情（HTML 富文本）
    stock = Column(Integer, nullable=False, default=0)  # 库存数量
    is_new = Column(Integer, nullable=False, default=0)  # 是否新品标记
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True, index=True)  # 供应商 ID
    cost_price = Column(Numeric(10, 2), nullable=True)  # 采购成本价
    service_fee_rate = Column(Numeric(5, 4), nullable=True)  # 服务费比例 (0.3000 = 30%)
    agent_profit_rate = Column(Numeric(5, 4), nullable=True)  # 区代利润比例 (0.1000 = 10%)

    # 关联
    prices = relationship("PriceTier", back_populates="product", cascade="all, delete-orphan")
    supplier = relationship("Supplier")


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
