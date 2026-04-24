"""
用户地址管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models.address import UserAddress
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class UserAddressCreateRequest(BaseModel):
    """创建地址请求"""
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detail_address: Optional[str] = None
    is_default: bool = False


class UserAddressUpdateRequest(BaseModel):
    """更新地址请求"""
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    receiver_address: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detail_address: Optional[str] = None
    is_default: Optional[bool] = None


class UserAddressResponse(BaseModel):
    """地址响应"""
    id: int
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detail_address: Optional[str] = None
    is_default: bool
    is_active: bool


@router.get("")
async def list_addresses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户地址列表"""
    query = select(UserAddress).where(
        UserAddress.user_id == current_user.id,
        UserAddress.is_active == True
    ).order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc())

    result = await db.execute(query)
    addresses = result.scalars().all()

    return {
        "items": [
            {
                "id": addr.id,
                "receiver_name": addr.receiver_name,
                "receiver_phone": addr.receiver_phone,
                "receiver_address": addr.receiver_address,
                "province": addr.province,
                "city": addr.city,
                "district": addr.district,
                "detail_address": addr.detail_address,
                "is_default": addr.is_default,
            }
            for addr in addresses
        ],
        "total": len(addresses),
    }


@router.get("/{address_id}")
async def get_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取地址详情"""
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_id == current_user.id,
            UserAddress.is_active == True
        )
    )
    address = result.scalar_one_or_none()

    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    return {
        "id": address.id,
        "receiver_name": address.receiver_name,
        "receiver_phone": address.receiver_phone,
        "receiver_address": address.receiver_address,
        "province": address.province,
        "city": address.city,
        "district": address.district,
        "detail_address": address.detail_address,
        "is_default": address.is_default,
    }


@router.post("")
async def create_address(
    request: UserAddressCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加新地址"""
    # 如果设置为默认地址，在同一事务中先取消其他默认地址
    if request.is_default:
        # 只在存在默认地址时才执行 UPDATE
        await db.execute(
            UserAddress.__table__.update()
            .where(UserAddress.user_id == current_user.id)
            .where(UserAddress.is_default == True)
            .values(is_default=False)
        )

    address = UserAddress(
        user_id=current_user.id,
        receiver_name=request.receiver_name,
        receiver_phone=request.receiver_phone,
        receiver_address=request.receiver_address,
        province=request.province,
        city=request.city,
        district=request.district,
        detail_address=request.detail_address,
        is_default=request.is_default,
    )
    db.add(address)
    await db.commit()
    await db.refresh(address)

    return {
        "id": address.id,
        "message": "地址添加成功",
    }


@router.put("/{address_id}")
async def update_address(
    address_id: int,
    request: UserAddressUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新地址"""
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_id == current_user.id,
            UserAddress.is_active == True
        )
    )
    address = result.scalar_one_or_none()

    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    # 更新字段
    update_data = request.model_dump(exclude_unset=True)

    # 如果设置为默认地址，在同一事务中先取消其他默认地址
    if update_data.get("is_default"):
        await db.execute(
            UserAddress.__table__.update()
            .where(UserAddress.user_id == current_user.id)
            .where(UserAddress.id != address_id)
            .where(UserAddress.is_default == True)
            .values(is_default=False)
        )

    for field, value in update_data.items():
        setattr(address, field, value)

    await db.commit()
    await db.refresh(address)

    return {
        "id": address.id,
        "message": "地址更新成功",
    }


@router.delete("/{address_id}")
async def delete_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除地址（软删除）"""
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_id == current_user.id
        )
    )
    address = result.scalar_one_or_none()

    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    # 软删除
    address.is_active = False
    await db.commit()

    return {"message": "地址删除成功"}


@router.post("/{address_id}/default")
async def set_default_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """设置默认地址"""
    # 先取消所有默认（只在存在默认地址时才执行 UPDATE）
    await db.execute(
        UserAddress.__table__.update()
        .where(UserAddress.user_id == current_user.id)
        .where(UserAddress.is_default == True)
        .values(is_default=False)
    )

    # 设置新的默认地址
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_id == current_user.id,
            UserAddress.is_active == True
        )
    )
    address = result.scalar_one_or_none()

    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    address.is_default = True
    await db.commit()

    return {
        "id": address.id,
        "message": "默认地址设置成功",
    }
