"""
分享 API 路由 - 分享追踪和团队管理
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.referral import Referral
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class ReferralStatsResponse(BaseModel):
    """分享统计响应"""
    total_referrals: int  # 累计分享人数
    active_referrals: int  # 有效分享人数


class ReferralRecordResponse(BaseModel):
    """分享记录响应"""
    id: int
    referee_id: int
    referee_username: str
    referrer_type: str
    created_at: datetime


@router.get("/code")
async def get_referral_code(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的分享码"""
    # 使用用户 ID 作为分享码（简单实现）
    # 可以扩展为生成自定义分享码
    referral_code = str(current_user.id)

    return {
        "referral_code": referral_code,
        "share_link": f"/h5/register?referrer={referral_code}",
    }


@router.get("/stats")
async def get_referral_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分享统计"""
    # 查询累计分享人数
    total_query = select(func.count(Referral.id)).where(
        Referral.referrer_id == current_user.id
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0

    # 查询有效分享人数（这里简化为所有分享）
    # 可以根据实际业务逻辑定义"有效"的标准
    active_query = select(func.count(Referral.id)).where(
        Referral.referrer_id == current_user.id
    )
    active_result = await db.execute(active_query)
    active = active_result.scalar() or 0

    return {
        "total_referrals": total,
        "active_referrals": active,
    }


@router.get("/records")
async def list_referral_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分享记录列表"""
    query = select(Referral).where(Referral.referrer_id == current_user.id)

    # 按创建时间倒序
    query = query.order_by(Referral.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    referrals = result.scalars().all()

    # 获取总数
    count_query = select(func.count(Referral.id)).where(
        Referral.referrer_id == current_user.id
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # 获取被推荐人信息
    referee_ids = [r.referee_id for r in referrals]
    if referee_ids:
        users_result = await db.execute(
            select(User).where(User.id.in_(referee_ids))
        )
        users_map = {u.id: u for u in users_result.scalars().all()}
    else:
        users_map = {}

    return {
        "items": [
            {
                "id": r.id,
                "referee_id": r.referee_id,
                "referee_username": users_map.get(r.referee_id, User).username if users_map.get(r.referee_id) else "未知",
                "referrer_type": r.referrer_type,
                "created_at": r.created_at,
            }
            for r in referrals
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/team")
async def get_team_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取团队列表（所有下级用户）"""
    query = select(Referral).where(Referral.referrer_id == current_user.id)
    query = query.order_by(Referral.created_at.desc())

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    referrals = result.scalars().all()

    # 获取团队成员信息
    referee_ids = [r.referee_id for r in referrals]
    if referee_ids:
        users_result = await db.execute(
            select(User).where(User.id.in_(referee_ids))
        )
        users = users_result.scalars().all()
    else:
        users = []

    return {
        "items": [
            {
                "id": u.id,
                "username": u.username,
                "role_type": u.role_type,
                "created_at": u.created_at,
            }
            for u in users
        ],
        "total": len(referrals),
    }
