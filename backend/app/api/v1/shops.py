"""
店铺管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.core.database import get_db
from app.models.shop import Shop
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class ShopCreateRequest:
    """创建店铺请求"""
    def __init__(self, user_id: int, region_id: int, referrer_id: Optional[int] = None):
        self.user_id = user_id
        self.region_id = region_id
        self.referrer_id = referrer_id


class ShopUpdateRequest:
    """更新店铺请求"""
    def __init__(self, region_id: Optional[int] = None, status: Optional[str] = None):
        self.region_id = region_id
        self.status = status


@router.get("")
async def list_shops(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    region_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取店铺列表（分页、筛选）"""
    query = select(Shop)

    if region_id:
        query = query.where(Shop.region_id == region_id)
    if status:
        query = query.where(Shop.status == status)

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    shops = result.scalars().all()

    # 获取总数（使用 count 查询，避免大数据量下性能问题）
    count_query = select(func.count(Shop.id))
    if region_id:
        count_query = count_query.where(Shop.region_id == region_id)
    if status:
        count_query = count_query.where(Shop.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": shop.id,
                "user_id": shop.user_id,
                "region_id": shop.region_id,
                "referrer_id": shop.referrer_id,
                "status": shop.status,
            }
            for shop in shops
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
async def create_shop(
    request: ShopCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建店铺"""
    shop = Shop(
        user_id=request.user_id,
        region_id=request.region_id,
        referrer_id=request.referrer_id,
        status="active"
    )
    db.add(shop)
    await db.commit()
    await db.refresh(shop)

    return {"id": shop.id, "user_id": shop.user_id, "region_id": shop.region_id}


@router.get("/{shop_id}")
async def get_shop(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取店铺详情"""
    result = await db.execute(select(Shop).where(Shop.id == shop_id))
    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")

    return {
        "id": shop.id,
        "user_id": shop.user_id,
        "region_id": shop.region_id,
        "referrer_id": shop.referrer_id,
        "status": shop.status,
    }


@router.put("/{shop_id}")
async def update_shop(
    shop_id: int,
    request: ShopUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新店铺"""
    result = await db.execute(select(Shop).where(Shop.id == shop_id))
    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")

    if request.region_id:
        shop.region_id = request.region_id
    if request.status:
        shop.status = request.status

    await db.commit()
    await db.refresh(shop)

    return {"id": shop.id, "region_id": shop.region_id, "status": shop.status}
