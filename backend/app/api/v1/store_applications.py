"""
店铺/区代申请管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.store_application import StoreApplication, StoreApplicationStatus, StoreApplicationType
from app.models.user import User
from app.models.shop import Shop
from app.models.agent import Agent
from app.models.region import Region
from app.models.role import Role
from app.api.v1.auth import get_current_user

router = APIRouter()


class StoreApplicationCreateRequest(BaseModel):
    """提交申请请求"""
    apply_type: StoreApplicationType

    # 店铺申请字段
    shop_name: Optional[str] = None
    shop_region_id: Optional[int] = None
    shop_agent_id: Optional[int] = None
    shop_latitude: Optional[float] = None
    shop_longitude: Optional[float] = None

    # 区代申请字段
    agent_name: Optional[str] = None
    agent_region_id: Optional[int] = None
    referrer_id: Optional[int] = None


class StoreApplicationResponse(BaseModel):
    """申请详情响应"""
    id: int
    user_id: int
    apply_type: str
    shop_name: Optional[str]
    shop_region_id: Optional[int]
    shop_agent_id: Optional[int]
    shop_latitude: Optional[float]
    shop_longitude: Optional[float]
    agent_name: Optional[str]
    agent_region_id: Optional[int]
    referrer_id: Optional[int]
    status: str
    reject_reason: Optional[str]
    created_at: datetime


@router.get("/check-region")
async def check_region_availability(
    region_id: int = Query(..., description="区域 ID"),
    type: str = Query(..., description="申请类型"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """检查区域是否可用（区代申请专用）"""
    if type != "AGENT":
        return {"available": True, "message": "仅区代申请需要校验区域"}

    # 检查是否已有区代
    result = await db.execute(
        select(Agent).where(Agent.region_id == region_id)
    )
    existing_agent = result.scalar_one_or_none()

    if existing_agent:
        return {"available": False, "message": "该区域已有区代"}

    # 检查是否有待审核的区代申请
    result = await db.execute(
        select(StoreApplication).where(
            StoreApplication.agent_region_id == region_id,
            StoreApplication.apply_type == StoreApplicationType.AGENT,
            StoreApplication.status == StoreApplicationStatus.PENDING
        )
    )
    pending_app = result.scalar_one_or_none()

    if pending_app:
        return {"available": False, "message": "该区域已有待审核的区代申请"}

    return {"available": True}


@router.get("/my")
async def get_my_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的申请记录列表"""
    result = await db.execute(
        select(StoreApplication)
        .where(StoreApplication.user_id == current_user.id)
        .order_by(StoreApplication.created_at.desc(), StoreApplication.id.desc())
    )
    applications = result.scalars().all()

    return {
        "items": [
            {
                "id": app.id,
                "apply_type": app.apply_type.value,
                "shop_name": app.shop_name,
                "agent_name": app.agent_name,
                "status": app.status.value,
                "reject_reason": app.reject_reason,
                "created_at": app.created_at,
            }
            for app in applications
        ]
    }


@router.post("")
async def create_application(
    request: StoreApplicationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交申请"""
    # 检查是否有待审核的申请
    result = await db.execute(
        select(StoreApplication).where(
            StoreApplication.user_id == current_user.id,
            StoreApplication.status == StoreApplicationStatus.PENDING
        )
    )
    existing_pending = result.scalar_one_or_none()

    if existing_pending:
        raise HTTPException(status_code=400, detail="您有正在审核中的申请，无法提交新的申请")

    # 创建申请
    application = StoreApplication(
        user_id=current_user.id,
        apply_type=request.apply_type,
        shop_name=request.shop_name,
        shop_region_id=request.shop_region_id,
        shop_agent_id=request.shop_agent_id,
        shop_latitude=request.shop_latitude,
        shop_longitude=request.shop_longitude,
        agent_name=request.agent_name,
        agent_region_id=request.agent_region_id,
        referrer_id=request.referrer_id,
        status=StoreApplicationStatus.PENDING,
    )

    db.add(application)
    await db.commit()
    await db.refresh(application)

    return {"id": application.id, "status": application.status.value}


@router.get("/{application_id}")
async def get_application(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取申请详情"""
    result = await db.execute(
        select(StoreApplication)
        .options(
            selectinload(StoreApplication.user),
            selectinload(StoreApplication.shop_region),
            selectinload(StoreApplication.agent_region),
            selectinload(StoreApplication.referrer),
        )
        .where(StoreApplication.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="申请记录不存在")

    # 权限检查：只能查看自己的申请，管理员可以查看所有
    if application.user_id != current_user.id and current_user.role.code != "admin":
        raise HTTPException(status_code=403, detail="无权查看此申请")

    return {
        "id": application.id,
        "user_id": application.user_id,
        "username": application.user.username,
        "apply_type": application.apply_type.value,
        "shop_name": application.shop_name,
        "shop_region_id": application.shop_region_id,
        "shop_region_name": application.shop_region.name if application.shop_region else None,
        "shop_agent_id": application.shop_agent_id,
        "shop_latitude": float(application.shop_latitude) if application.shop_latitude else None,
        "shop_longitude": float(application.shop_longitude) if application.shop_longitude else None,
        "agent_name": application.agent_name,
        "agent_region_id": application.agent_region_id,
        "agent_region_name": application.agent_region.name if application.agent_region else None,
        "referrer_id": application.referrer_id,
        "referrer_name": application.referrer.name if application.referrer else None,
        "status": application.status.value,
        "reject_reason": application.reject_reason,
        "created_at": application.created_at,
    }


@router.get("")
async def list_applications(
    status: Optional[str] = None,
    apply_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取申请列表（管理端）"""
    # 权限检查：仅管理员
    if current_user.role.code != "admin":
        raise HTTPException(status_code=403, detail="无权访问")

    # 加载关联数据：user, region, referrer
    query = select(StoreApplication).options(
        selectinload(StoreApplication.user),
        selectinload(StoreApplication.shop_region),
        selectinload(StoreApplication.agent_region),
    )

    if status:
        query = query.where(StoreApplication.status == StoreApplicationStatus(status))
    if apply_type:
        query = query.where(StoreApplication.apply_type == StoreApplicationType(apply_type))

    # 分页
    offset = (page - 1) * page_size
    query = query.order_by(StoreApplication.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    applications = result.scalars().all()

    # 获取总数
    count_query = select(func.count(StoreApplication.id))
    if status:
        count_query = count_query.where(StoreApplication.status == StoreApplicationStatus(status))
    if apply_type:
        count_query = count_query.where(StoreApplication.apply_type == StoreApplicationType(apply_type))
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # 获取所有区代 ID 用于查找推荐区代名称
    referrer_ids = [app.referrer_id for app in applications if app.referrer_id]
    referrer_names = {}
    if referrer_ids:
        referrer_result = await db.execute(select(Agent).where(Agent.id.in_(referrer_ids)))
        for agent in referrer_result.scalars().all():
            referrer_names[agent.id] = agent.name

    return {
        "items": [
            {
                "id": app.id,
                "user_id": app.user_id,
                "username": app.user.username if app.user else "未知用户",
                "apply_type": app.apply_type.value,
                "shop_name": app.shop_name,
                "agent_name": app.agent_name,
                "status": app.status.value,
                "region_name": (app.shop_region.name if app.shop_region else None) or (app.agent_region.name if app.agent_region else None),
                "referrer_name": referrer_names.get(app.referrer_id) if app.referrer_id else None,
                "reject_reason": app.reject_reason,
                "created_at": app.created_at,
            }
            for app in applications
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/{application_id}/approve")
async def approve_application(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """审核通过申请"""
    # 权限检查：仅管理员
    if current_user.role.code != "admin":
        raise HTTPException(status_code=403, detail="无权访问")

    # 获取申请
    result = await db.execute(
        select(StoreApplication)
        .options(selectinload(StoreApplication.user))
        .where(StoreApplication.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="申请记录不存在")

    # 幂等性处理：已审核的申请返回友好提示
    if application.status == StoreApplicationStatus.APPROVED:
        return {"message": "该申请已通过审核", "application_id": application_id}
    if application.status == StoreApplicationStatus.REJECTED:
        raise HTTPException(status_code=400, detail="该申请已被拒绝，无法重新审核")

    if application.status != StoreApplicationStatus.PENDING:
        raise HTTPException(status_code=400, detail="申请状态异常")

    # 获取角色
    if application.apply_type == StoreApplicationType.SHOP:
        target_role_code = "shop"
    else:
        target_role_code = "agent"

    role_result = await db.execute(select(Role).where(Role.code == target_role_code))
    target_role = role_result.scalar_one_or_none()

    if not target_role:
        raise HTTPException(status_code=500, detail="目标角色不存在")

    # 事务处理：创建 Shop/Agent + 更新用户角色
    try:
        if application.apply_type == StoreApplicationType.SHOP:
            # 创建店铺
            shop = Shop(
                user_id=application.user_id,
                region_id=application.shop_region_id,
                agent_id=application.shop_agent_id,
                name=application.shop_name,
                status="active",
                latitude=application.shop_latitude,
                longitude=application.shop_longitude,
            )
            db.add(shop)
        else:
            # 创建区代
            agent = Agent(
                user_id=application.user_id,
                region_id=application.agent_region_id,
                referrer_id=application.referrer_id,
                name=application.agent_name,
                status="active",
            )
            db.add(agent)

        # 更新用户角色
        application.user.role_id = target_role.id

        # 更新申请状态
        application.status = StoreApplicationStatus.APPROVED

        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"审核失败：{str(e)}")

    return {"message": "审核通过", "application_id": application_id}


@router.post("/{application_id}/reject")
async def reject_application(
    application_id: int,
    reject_reason: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """审核拒绝申请"""
    # 权限检查：仅管理员
    if current_user.role.code != "admin":
        raise HTTPException(status_code=403, detail="无权访问")

    # 获取申请
    result = await db.execute(
        select(StoreApplication)
        .where(StoreApplication.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="申请记录不存在")

    # 幂等性处理：已审核的申请返回友好提示
    if application.status == StoreApplicationStatus.REJECTED:
        return {"message": "该申请已被拒绝", "application_id": application_id}
    if application.status == StoreApplicationStatus.APPROVED:
        raise HTTPException(status_code=400, detail="该申请已通过审核，无法拒绝")

    if application.status != StoreApplicationStatus.PENDING:
        raise HTTPException(status_code=400, detail="申请状态异常")

    # 更新申请状态
    application.status = StoreApplicationStatus.REJECTED
    application.reject_reason = reject_reason

    await db.commit()

    return {"message": "审核拒绝", "application_id": application_id}
