"""
产品管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from pydantic import BaseModel

from app.core.database import get_db
from app.models.product import Product, PriceTier
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class PriceTierInput(BaseModel):
    """价格层级输入"""
    tier_type: str  # retail/shop/agent
    price: float


class ProductCreateRequest(BaseModel):
    """创建产品请求"""
    name: str
    sku_code: str
    prices: List[PriceTierInput]


class ProductUpdateRequest(BaseModel):
    """更新产品请求"""
    name: Optional[str] = None
    sku_code: Optional[str] = None
    status: Optional[str] = None


class ProductPricesRequest(BaseModel):
    """设置产品价格请求"""
    prices: List[PriceTierInput]


@router.get("")
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取产品列表"""
    query = select(Product)

    if status:
        query = query.where(Product.status == status)

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    products = result.scalars().all()

    # 获取总数（使用 count 查询，避免大数据量下性能问题）
    count_query = select(func.count(Product.id))
    if status:
        count_query = count_query.where(Product.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "sku_code": p.sku_code,
                "status": p.status,
                "prices": [{"tier_type": pt.tier_type, "price": float(pt.price)} for pt in p.prices]
            }
            for p in products
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
async def create_product(
    request: ProductCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建产品"""
    # 检查 SKU 是否已存在
    existing = await db.execute(select(Product).where(Product.sku_code == request.sku_code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="SKU 编码已存在")

    product = Product(
        name=request.name,
        sku_code=request.sku_code,
        status="active"
    )
    db.add(product)
    await db.flush()  # 获取 product.id

    # 创建价格层级
    for price_input in request.prices:
        price_tier = PriceTier(
            product_id=product.id,
            tier_type=price_input.tier_type,
            price=price_input.price
        )
        db.add(price_tier)

    await db.commit()
    await db.refresh(product)

    return {"id": product.id, "name": product.name, "sku_code": product.sku_code}


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取产品详情"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    return {
        "id": product.id,
        "name": product.name,
        "sku_code": product.sku_code,
        "status": product.status,
        "prices": [{"tier_type": pt.tier_type, "price": float(pt.price)} for pt in product.prices]
    }


@router.put("/{product_id}")
async def update_product(
    product_id: int,
    request: ProductUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新产品"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    if request.name:
        product.name = request.name
    if request.sku_code:
        # 检查新 SKU 是否已被其他产品使用
        existing = await db.execute(select(Product).where(
            Product.sku_code == request.sku_code,
            Product.id != product_id
        ))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="SKU 编码已存在")
        product.sku_code = request.sku_code
    if request.status:
        product.status = request.status

    await db.commit()
    await db.refresh(product)

    return {"id": product.id, "name": product.name, "sku_code": product.sku_code}


@router.post("/{product_id}/prices")
async def set_product_prices(
    product_id: int,
    request: ProductPricesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """设置产品价格（三级定价）"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    # 删除现有价格
    for pt in product.prices:
        await db.delete(pt)

    # 创建新价格
    for price_input in request.prices:
        price_tier = PriceTier(
            product_id=product_id,
            tier_type=price_input.tier_type,
            price=price_input.price
        )
        db.add(price_tier)

    await db.commit()

    return {"message": "价格设置成功"}
