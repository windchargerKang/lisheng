"""
区代管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.agent import Agent
from app.models.user import User
from app.models.region import Region
from app.api.v1.auth import get_current_user

router = APIRouter()


class AgentCreateRequest(BaseModel):
    """创建区代请求"""
    user_id: int
    region_id: int
    name: Optional[str] = None  # 区代名称
    referrer_id: Optional[int] = None


class AgentUpdateRequest(BaseModel):
    """更新区代请求"""
    name: Optional[str] = None
    user_id: Optional[int] = None
    region_id: Optional[int] = None
    referrer_id: Optional[int] = None
    status: Optional[str] = None


@router.get("")
async def list_agents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    region_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取区代列表（分页、筛选）"""
    from sqlalchemy.orm import aliased

    # 使用别名来支持自连接查询推荐区代
    ReferrerAgent = aliased(Agent)

    query = (
        select(Agent, User, Region, ReferrerAgent)
        .join(User, Agent.user_id == User.id)
        .join(Region, Agent.region_id == Region.id)
        .outerjoin(ReferrerAgent, Agent.referrer_id == ReferrerAgent.id)
    )

    if region_id:
        query = query.where(Agent.region_id == region_id)
    if status:
        query = query.where(Agent.status == status)

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    rows = result.all()

    # 获取总数
    count_query = select(func.count(Agent.id))
    if region_id:
        count_query = count_query.where(Agent.region_id == region_id)
    if status:
        count_query = count_query.where(Agent.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": agent.id,
                "user_id": agent.user_id,
                "username": user.username,
                "name": agent.name,
                "region_id": agent.region_id,
                "region_name": region.name,
                "referrer_id": agent.referrer_id,
                "referrer_name": referrer_agent.name if referrer_agent else None,
                "status": agent.status,
            }
            for agent, user, region, referrer_agent in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
async def create_agent(
    request: AgentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建区代"""
    # 检查该用户是否已是区代
    existing = await db.execute(select(Agent).where(Agent.user_id == request.user_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该用户已是区代")

    # 检查该区域是否已有区代
    region_exists = await db.execute(select(Agent).where(Agent.region_id == request.region_id))
    if region_exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该区域已有区代")

    agent = Agent(
        user_id=request.user_id,
        region_id=request.region_id,
        name=request.name,
        referrer_id=request.referrer_id,
        status="active"
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return {"id": agent.id, "user_id": agent.user_id, "name": agent.name, "region_id": agent.region_id}


@router.get("/{agent_id}")
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取区代详情"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="区代不存在")

    return {
        "id": agent.id,
        "user_id": agent.user_id,
        "name": agent.name,
        "region_id": agent.region_id,
        "referrer_id": agent.referrer_id,
        "status": agent.status,
    }


@router.put("/{agent_id}")
async def update_agent(
    agent_id: int,
    request: AgentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新区代"""
    import logging
    logger = logging.getLogger(__name__)

    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="区代不存在")

    # 记录接收到的请求数据
    logger.info(f"更新区代 {agent_id}: 接收到的数据 - name={request.name}, region_id={request.region_id}, referrer_id={request.referrer_id}, status={request.status}")
    logger.info(f"更新前 agent.referrer_id = {agent.referrer_id}")

    if request.name is not None:
        agent.name = request.name
    if request.user_id is not None:
        # 检查该用户是否已是区代
        existing = await db.execute(select(Agent).where(
            Agent.user_id == request.user_id,
            Agent.id != agent_id
        ))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="该用户已是区代")
        agent.user_id = request.user_id
    if request.region_id is not None:
        # 检查新区域是否已有区代
        existing = await db.execute(select(Agent).where(
            Agent.region_id == request.region_id,
            Agent.id != agent_id
        ))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="该区域已有区代")
        agent.region_id = request.region_id
    if request.referrer_id is not None:
        agent.referrer_id = request.referrer_id
        logger.info(f"设置 agent.referrer_id = {request.referrer_id}")

    if request.status is not None:
        agent.status = request.status

    await db.commit()
    await db.refresh(agent)

    logger.info(f"更新后 agent.referrer_id = {agent.referrer_id}")

    return {"id": agent.id, "region_id": agent.region_id, "status": agent.status}
