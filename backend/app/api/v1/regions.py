"""
区域管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db
from app.models.region import Region
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter()


class RegionCreateRequest:
    """创建区域请求"""
    def __init__(self, name: str, parent_id: int = None, level: int = 1):
        self.name = name
        self.parent_id = parent_id
        self.level = level


class RegionUpdateRequest:
    """更新区域请求"""
    def __init__(self, name: str = None, level: int = None):
        self.name = name
        self.level = level


def build_region_tree(regions: List[Region], parent_id: int = None) -> List[dict]:
    """构建区域树形结构"""
    result = []
    for region in regions:
        if region.parent_id == parent_id:
            children = build_region_tree(regions, region.id)
            result.append({
                "id": region.id,
                "name": region.name,
                "level": region.level,
                "path": region.path,
                "parent_id": region.parent_id,
                "children": children
            })
    return result


@router.get("")
async def list_regions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取区域树"""
    result = await db.execute(select(Region).order_by(Region.path))
    regions = result.scalars().all()
    tree = build_region_tree(regions)
    return {"regions": tree}


@router.post("")
async def create_region(
    request: RegionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建区域"""
    # 验证父区域是否存在
    if request.parent_id:
        parent_result = await db.execute(select(Region).where(Region.id == request.parent_id))
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=400, detail="父区域不存在")

        # 构建路径
        path = f"{parent.path}/{request.parent_id}"
        level = parent.level + 1
    else:
        path = str(request.level)  # 顶级区域
        level = 1

    # 创建区域
    region = Region(
        name=request.name,
        parent_id=request.parent_id,
        level=level,
        path=path
    )
    db.add(region)
    await db.commit()
    await db.refresh(region)

    return {"id": region.id, "name": region.name, "path": region.path}


@router.get("/{region_id}")
async def get_region(
    region_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取区域详情"""
    result = await db.execute(select(Region).where(Region.id == region_id))
    region = result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail="区域不存在")

    return {
        "id": region.id,
        "name": region.name,
        "level": region.level,
        "path": region.path,
        "parent_id": region.parent_id
    }


@router.put("/{region_id}")
async def update_region(
    region_id: int,
    request: RegionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新区域"""
    result = await db.execute(select(Region).where(Region.id == region_id))
    region = result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail="区域不存在")

    if request.name:
        region.name = request.name
    if request.level:
        region.level = request.level

    await db.commit()
    await db.refresh(region)

    return {"id": region.id, "name": region.name, "level": region.level}


@router.delete("/{region_id}")
async def delete_region(
    region_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除区域"""
    result = await db.execute(select(Region).where(Region.id == region_id))
    region = result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail="区域不存在")

    # 检查是否有子区域
    children_result = await db.execute(select(Region).where(Region.parent_id == region_id))
    children = children_result.scalars().all()

    if children:
        raise HTTPException(status_code=400, detail="存在子区域，无法删除")

    await db.delete(region)
    await db.commit()

    return {"message": "删除成功"}
