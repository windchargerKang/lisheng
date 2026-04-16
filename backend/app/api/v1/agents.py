"""
区代管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models.agent import Agent
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class AgentCreateRequest:
    """创建区代请求"""
    def __init__(self, user_id: int, region_id: int, referrer_id: Optional[int] = None):
        self.user_id = user_id
        self.region_id = region_id
        self.referrer_id = referrer_id


class AgentUpdateRequest:
    """更新区代请求"""
    def __init__(self, region_id: Optional[int] = None, status: Optional[str] = None):
        self.region_id = region_id
        self.status = status


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
    query = select(Agent)

    if region_id:
        query = query.where(Agent.region_id == region_id)
    if status:
        query = query.where(Agent.status == status)

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    agents = result.scalars().all()

    # 获取总数（使用 count 查询，避免大数据量下性能问题）
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
                "region_id": agent.region_id,
                "referrer_id": agent.referrer_id,
                "status": agent.status,
            }
            for agent in agents
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
        referrer_id=request.referrer_id,
        status="active"
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return {"id": agent.id, "user_id": agent.user_id, "region_id": agent.region_id}


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
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="区代不存在")

    if request.region_id:
        # 检查新区域是否已有区代
        existing = await db.execute(select(Agent).where(
            Agent.region_id == request.region_id,
            Agent.id != agent_id
        ))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="该区域已有区代")
        agent.region_id = request.region_id

    if request.status:
        agent.status = request.status

    await db.commit()
    await db.refresh(agent)

    return {"id": agent.id, "region_id": agent.region_id, "status": agent.status}
