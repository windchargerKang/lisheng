"""
收益 API 路由 - 分润记录和提现管理
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.profit import ProfitRecord, WithdrawalRequest, ProfitStatus, WithdrawalStatus
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class WithdrawalRequestCreate(BaseModel):
    """提现申请请求"""
    amount: float


class ProfitRecordResponse(BaseModel):
    """分润记录响应"""
    id: int
    order_id: Optional[int]
    amount: float
    status: str
    created_at: datetime


class WithdrawalRecordResponse(BaseModel):
    """提现记录响应"""
    id: int
    amount: float
    status: str
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime


@router.get("/overview")
async def get_profit_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取收益总览"""
    # 查询总分润
    total_query = select(func.sum(ProfitRecord.amount)).where(
        ProfitRecord.user_id == current_user.id
    )
    total_result = await db.execute(total_query)
    total_profit = total_result.scalar() or 0

    # 查询可提现金额（已结算但未提现）
    available_query = select(func.sum(ProfitRecord.amount)).where(
        ProfitRecord.user_id == current_user.id,
        ProfitRecord.status == ProfitStatus.PAID
    )
    available_result = await db.execute(available_query)
    available_amount = available_result.scalar() or 0

    # 查询已提现金额
    withdrawn_query = select(func.sum(ProfitRecord.amount)).where(
        ProfitRecord.user_id == current_user.id,
        ProfitRecord.status == ProfitStatus.WITHDRAWN
    )
    withdrawn_result = await db.execute(withdrawn_query)
    withdrawn_amount = withdrawn_result.scalar() or 0

    # 查询待结算金额
    pending_query = select(func.sum(ProfitRecord.amount)).where(
        ProfitRecord.user_id == current_user.id,
        ProfitRecord.status == ProfitStatus.PENDING
    )
    pending_result = await db.execute(pending_query)
    pending_amount = pending_result.scalar() or 0

    return {
        "total_profit": float(total_profit),
        "available_amount": float(available_amount),
        "withdrawn_amount": float(withdrawn_amount),
        "pending_amount": float(pending_amount),
    }


@router.get("/records")
async def list_profit_records(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分润记录列表"""
    query = select(ProfitRecord).where(ProfitRecord.user_id == current_user.id)

    if status:
        query = query.where(ProfitRecord.status == status)

    # 按创建时间倒序
    query = query.order_by(ProfitRecord.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    records = result.scalars().all()

    # 获取总数
    count_query = select(func.count(ProfitRecord.id)).where(
        ProfitRecord.user_id == current_user.id
    )
    if status:
        count_query = count_query.where(ProfitRecord.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": r.id,
                "order_id": r.order_id,
                "amount": float(r.amount),
                "status": r.status.value,
                "created_at": r.created_at,
                "remark": r.remark,
            }
            for r in records
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/withdrawals")
async def list_withdrawal_records(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取提现记录列表"""
    query = select(WithdrawalRequest).where(
        WithdrawalRequest.user_id == current_user.id
    )

    if status:
        query = query.where(WithdrawalRequest.status == status)

    # 按创建时间倒序
    query = query.order_by(WithdrawalRequest.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    records = result.scalars().all()

    # 获取总数
    count_query = select(func.count(WithdrawalRequest.id)).where(
        WithdrawalRequest.user_id == current_user.id
    )
    if status:
        count_query = count_query.where(WithdrawalRequest.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": w.id,
                "amount": float(w.amount),
                "status": w.status.value,
                "remark": w.remark,
                "created_at": w.created_at,
                "updated_at": w.updated_at,
            }
            for w in records
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/withdrawals")
async def create_withdrawal(
    request: WithdrawalRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """申请提现"""
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="提现金额必须大于 0")

    # 检查可提现余额
    available_query = select(func.sum(ProfitRecord.amount)).where(
        ProfitRecord.user_id == current_user.id,
        ProfitRecord.status == ProfitStatus.PAID
    )
    available_result = await db.execute(available_query)
    available_amount = available_result.scalar() or 0

    if request.amount > float(available_amount):
        raise HTTPException(status_code=400, detail="可提现余额不足")

    # 创建提现申请
    withdrawal = WithdrawalRequest(
        user_id=current_user.id,
        amount=request.amount,
        status=WithdrawalStatus.PENDING,
    )
    db.add(withdrawal)
    await db.commit()
    await db.refresh(withdrawal)

    return {
        "id": withdrawal.id,
        "amount": float(withdrawal.amount),
        "status": withdrawal.status.value,
        "created_at": withdrawal.created_at,
    }


@router.get("/withdrawals/{withdrawal_id}")
async def get_withdrawal_detail(
    withdrawal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取提现详情"""
    result = await db.execute(
        select(WithdrawalRequest).where(
            WithdrawalRequest.id == withdrawal_id,
            WithdrawalRequest.user_id == current_user.id
        )
    )
    withdrawal = result.scalar_one_or_none()

    if not withdrawal:
        raise HTTPException(status_code=404, detail="提现记录不存在")

    return {
        "id": withdrawal.id,
        "amount": float(withdrawal.amount),
        "status": withdrawal.status.value,
        "remark": withdrawal.remark,
        "created_at": withdrawal.created_at,
        "updated_at": withdrawal.updated_at,
    }
