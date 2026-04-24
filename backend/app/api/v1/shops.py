"""
店铺管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from typing import Optional, List
from pydantic import BaseModel

from app.core.database import get_db
from app.models.shop import Shop
from app.models.user import User
from app.models.region import Region
from app.models.agent import Agent
from app.api.v1.auth import get_current_user

router = APIRouter()


class ShopCreateRequest(BaseModel):
    """创建店铺请求"""
    user_id: int
    region_id: int
    name: Optional[str] = None  # 店铺名称
    agent_id: Optional[int] = None  # 绑定区代


class ShopUpdateRequest(BaseModel):
    """更新店铺请求"""
    name: Optional[str] = None
    user_id: Optional[int] = None
    region_id: Optional[int] = None
    agent_id: Optional[int] = None
    status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


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
    # 使用 join 查询获取关联名称
    query = (
        select(Shop, User, Region, Agent)
        .join(User, Shop.user_id == User.id)
        .join(Region, Shop.region_id == Region.id)
        .outerjoin(Agent, Shop.agent_id == Agent.id)
    )

    if region_id:
        query = query.where(Shop.region_id == region_id)
    if status:
        query = query.where(Shop.status == status)

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    rows = result.all()

    # 获取总数
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
                "username": user.username,
                "name": shop.name,
                "region_id": shop.region_id,
                "region_name": region.name,
                "agent_id": shop.agent_id,
                "agent_name": agent.name if agent else None,
                "status": shop.status,
                "latitude": float(shop.latitude) if shop.latitude else None,
                "longitude": float(shop.longitude) if shop.longitude else None,
            }
            for shop, user, region, agent in rows
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
        name=request.name,
        agent_id=request.agent_id,
        status="active"
    )
    db.add(shop)
    await db.commit()
    await db.refresh(shop)

    return {"id": shop.id, "user_id": shop.user_id, "name": shop.name, "region_id": shop.region_id, "agent_id": shop.agent_id}


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
        "name": shop.name,
        "region_id": shop.region_id,
        "agent_id": shop.agent_id,
        "status": shop.status,
        "latitude": float(shop.latitude) if shop.latitude else None,
        "longitude": float(shop.longitude) if shop.longitude else None,
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

    if request.name is not None:
        shop.name = request.name
    if request.user_id is not None:
        shop.user_id = request.user_id
    if request.region_id is not None:
        shop.region_id = request.region_id
    if request.agent_id is not None:
        shop.agent_id = request.agent_id
    if request.status is not None:
        shop.status = request.status
    if request.latitude is not None:
        shop.latitude = request.latitude
    if request.longitude is not None:
        shop.longitude = request.longitude

    await db.commit()
    await db.refresh(shop)

    return {
        "id": shop.id,
        "user_id": shop.user_id,
        "name": shop.name,
        "region_id": shop.region_id,
        "agent_id": shop.agent_id,
        "status": shop.status,
        "latitude": float(shop.latitude) if shop.latitude else None,
        "longitude": float(shop.longitude) if shop.longitude else None,
    }
