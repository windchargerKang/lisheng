"""
产品管理 API 路由
"""
import bleach
import uuid
import os
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from pydantic import BaseModel

from app.core.database import get_db
from app.models.product import Product, PriceTier
from app.models.user import User
from app.models.shop import Shop
from app.models.agent import Agent
from app.api.v1.auth import get_current_user
from app.core.config import settings

# 允许的 HTML 标签白名单
ALLOWED_TAGS = [
    "p", "br", "strong", "em", "b", "i", "u",
    "ul", "ol", "li",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "pre", "code",
    "img", "a", "span", "div"
]

# 允许的属性
ALLOWED_ATTRIBUTES = {
    "*": ["class"],
    "a": ["href", "title", "target"],
    "img": ["src", "alt", "width", "height"]
}


def sanitize_html(content: Optional[str]) -> Optional[str]:
    """过滤 HTML 内容，防止 XSS 攻击"""
    if not content:
        return content
    return bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

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
    image_url: Optional[str] = None  # 产品主图 URL
    images: Optional[List[str]] = None  # 产品多图
    detail: Optional[str] = None  # 产品详情 HTML
    service_fee_rate: Optional[float] = None  # 服务费比例 (0.30 = 30%)
    agent_profit_rate: Optional[float] = None  # 区代利润比例 (0.10 = 10%)


class ProductUpdateRequest(BaseModel):
    """更新产品请求"""
    name: Optional[str] = None
    sku_code: Optional[str] = None
    status: Optional[str] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    detail: Optional[str] = None
    service_fee_rate: Optional[float] = None  # 服务费比例 (0.30 = 30%)
    agent_profit_rate: Optional[float] = None  # 区代利润比例 (0.10 = 10%)


class ProductPricesRequest(BaseModel):
    """设置产品价格请求"""
    prices: List[PriceTierInput]
    service_fee_rate: Optional[float] = None  # 服务费比例 (0.30 = 30%)
    agent_profit_rate: Optional[float] = None  # 区代利润比例 (0.10 = 10%)


@router.get("")
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取产品列表（根据用户角色过滤价格）"""
    query = select(Product).options(selectinload(Product.prices))

    if status:
        query = query.where(Product.status == status)

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    products = result.scalars().unique().all()

    # 获取总数（使用 count 查询，避免大数据量下性能问题）
    count_query = select(func.count(Product.id))
    if status:
        count_query = count_query.where(Product.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # 根据用户角色过滤价格
    visible_tier_types = []

    # 管理员可以看到所有价格
    if current_user.role_type == "admin":
        visible_tier_types = ["retail", "shop", "agent"]
    else:
        # 非管理员用户，根据其角色类型显示对应价格
        # 检查是否是店铺账号
        shop_query = select(Shop).where(Shop.user_id == current_user.id)
        shop_result = (await db.execute(shop_query)).scalar_one_or_none()
        if shop_result:
            visible_tier_types.append("shop")

        # 检查是否是区代账号
        agent_query = select(Agent).where(Agent.user_id == current_user.id)
        agent_result = (await db.execute(agent_query)).scalar_one_or_none()
        if agent_result:
            visible_tier_types.append("agent")

        # 如果是普通客户或没有特殊身份，只显示零售价
        if not visible_tier_types:
            visible_tier_types.append("retail")

    return {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "sku_code": p.sku_code,
                "status": p.status,
                "image": p.image,
                "image_url": p.image_url,
                "images": p.images or [],
                "description": p.description,
                "detail": p.detail,
                "is_new": bool(p.is_new),
                "service_fee_rate": float(p.service_fee_rate) if p.service_fee_rate else None,
                "agent_profit_rate": float(p.agent_profit_rate) if p.agent_profit_rate else None,
                "prices": [
                    {"tier_type": pt.tier_type, "price": float(pt.price)}
                    for pt in p.prices
                    if pt.tier_type in visible_tier_types
                ]
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
        status="active",
        image_url=request.image_url,
        images=request.images,
        detail=sanitize_html(request.detail),
        service_fee_rate=request.service_fee_rate,
        agent_profit_rate=request.agent_profit_rate
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
    """获取产品详情（根据用户角色过滤价格）"""
    result = await db.execute(select(Product).options(selectinload(Product.prices)).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    # 根据用户角色过滤价格
    visible_tier_types = []

    # 管理员可以看到所有价格
    if current_user.role_type == "admin":
        visible_tier_types = ["retail", "shop", "agent"]
    else:
        # 非管理员用户，根据其角色类型显示对应价格
        # 检查是否是店铺账号
        shop_query = select(Shop).where(Shop.user_id == current_user.id)
        shop_result = (await db.execute(shop_query)).scalar_one_or_none()
        if shop_result:
            visible_tier_types.append("shop")

        # 检查是否是区代账号
        agent_query = select(Agent).where(Agent.user_id == current_user.id)
        agent_result = (await db.execute(agent_query)).scalar_one_or_none()
        if agent_result:
            visible_tier_types.append("agent")

        # 如果是普通客户或没有特殊身份，只显示零售价
        if not visible_tier_types:
            visible_tier_types.append("retail")

    return {
        "id": product.id,
        "name": product.name,
        "sku_code": product.sku_code,
        "status": product.status,
        "image": product.image,
        "image_url": product.image_url,
        "images": product.images or [],
        "description": product.description,
        "detail": product.detail,
        "stock": product.stock,
        "is_new": bool(product.is_new),
        "service_fee_rate": float(product.service_fee_rate) if product.service_fee_rate else None,
        "agent_profit_rate": float(product.agent_profit_rate) if product.agent_profit_rate else None,
        "prices": [
            {"tier_type": pt.tier_type, "price": float(pt.price)}
            for pt in product.prices
            if pt.tier_type in visible_tier_types
        ]
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
    if request.image_url is not None:
        product.image_url = request.image_url
    if request.images is not None:
        product.images = request.images
    if request.detail is not None:
        product.detail = sanitize_html(request.detail)
    if request.service_fee_rate is not None:
        product.service_fee_rate = request.service_fee_rate
    if request.agent_profit_rate is not None:
        product.agent_profit_rate = request.agent_profit_rate

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
    result = await db.execute(
        select(Product).options(selectinload(Product.prices)).where(Product.id == product_id)
    )
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

    # 更新分润比例
    if request.service_fee_rate is not None:
        product.service_fee_rate = request.service_fee_rate
    if request.agent_profit_rate is not None:
        product.agent_profit_rate = request.agent_profit_rate

    await db.commit()

    return {"message": "价格设置成功"}


@router.post("/upload")
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传产品图片"""
    import pathlib

    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的文件格式，仅支持 JPG/PNG/GIF/WebP")

    # 验证文件大小（5MB）
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")

    # 使用绝对路径：backend/uploads/products (与 main.py 静态文件目录一致)
    # __file__ = backend/app/api/v1/products.py
    # 需要到 backend/uploads
    base_dir = pathlib.Path(__file__).resolve().parent.parent.parent.parent  # backend
    upload_dir = base_dir / "uploads" / "products"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 生成唯一文件名
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = upload_dir / filename

    # 保存文件
    with open(filepath, "wb") as f:
        f.write(content)

    # 返回访问 URL（相对于后端服务）
    image_url = f"/uploads/products/{filename}"

    return {"url": image_url, "filename": filename}


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除产品"""
    # 查询产品
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    # 删除产品（级联删除价格）
    await db.delete(product)
    await db.commit()

    return {"message": "删除成功"}
