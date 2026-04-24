"""
购物车 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class CartItemCreateRequest(BaseModel):
    """创建购物车项请求"""
    product_id: int
    quantity: int = 1


class CartItemUpdateRequest(BaseModel):
    """更新购物车项请求"""
    quantity: int


@router.get("/items")
async def list_cart_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的购物车列表"""
    # 使用 selectinload 预加载产品和价格，避免 lazy loading 问题
    from sqlalchemy.orm import joinedload

    query = select(CartItem).options(
        joinedload(CartItem.product).joinedload(Product.prices)
    ).where(CartItem.user_id == current_user.id)

    result = await db.execute(query)
    cart_items = result.scalars().unique().all()

    def get_product_price(product, user) -> float:
        """根据用户角色获取对应价格"""
        if not product or not product.prices:
            return 0.0

        # 根据用户角色获取对应层级价格
        user_tier = user.role.code if user and user.role else "retail"

        # 优先获取用户角色对应价格
        tier_price = next((p for p in product.prices if p.tier_type == user_tier), None)
        if tier_price:
            return float(tier_price.price)

        # 如果没有对应角色价格，返回第一个价格
        return float(product.prices[0].price) if product.prices else 0.0

    return {
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else "",
                "price": get_product_price(item.product, current_user),
                "quantity": item.quantity,
                "image": getattr(item.product, 'image', None),
            }
            for item in cart_items
        ],
        "total": len(cart_items),
    }


@router.post("/items")
async def add_to_cart(
    request: CartItemCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加商品到购物车"""
    # 检查产品是否存在
    product_result = await db.execute(select(Product).where(Product.id == request.product_id))
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 检查购物车中是否已有该商品
    existing_result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == current_user.id,
            CartItem.product_id == request.product_id
        )
    )
    existing_item = existing_result.scalar_one_or_none()

    if existing_item:
        # 更新数量
        existing_item.quantity += request.quantity
    else:
        # 创建新购物车项
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=request.product_id,
            quantity=request.quantity
        )
        db.add(cart_item)

    await db.commit()

    return {"message": "添加成功"}


@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: int,
    request: CartItemUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新购物车商品数量"""
    result = await db.execute(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.user_id == current_user.id
        )
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(status_code=404, detail="购物车商品不存在")

    if request.quantity < 1:
        raise HTTPException(status_code=400, detail="数量必须大于 0")

    if request.quantity > 99:
        raise HTTPException(status_code=400, detail="数量不能超过 99")

    cart_item.quantity = request.quantity
    await db.commit()

    return {"message": "更新成功"}


@router.delete("/items/{item_id}")
async def delete_cart_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除购物车商品"""
    result = await db.execute(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.user_id == current_user.id
        )
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(status_code=404, detail="购物车商品不存在")

    await db.delete(cart_item)
    await db.commit()

    return {"message": "删除成功"}


@router.delete("/items")
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """清空购物车"""
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == current_user.id)
    )
    cart_items = result.scalars().all()

    for item in cart_items:
        await db.delete(item)

    await db.commit()

    return {"message": "清空成功"}
