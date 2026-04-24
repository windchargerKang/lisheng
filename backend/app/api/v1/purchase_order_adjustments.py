"""
采购订单调整申请 API 路由（运营端）
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import json

from app.core.database import get_db
from app.models.purchase_order import PurchaseOrder, SupplierConfirmStatus
from app.models.purchase_order_adjustment import PurchaseOrderAdjustment, AdjustmentStatus
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class AdjustmentApproveRequest(BaseModel):
    """批准调整申请请求"""
    remark: Optional[str] = None


@router.get("/adjustments")
async def list_adjustments(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    order_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查看调整申请列表（运营端）"""
    query = select(PurchaseOrderAdjustment)

    if status:
        query = query.where(PurchaseOrderAdjustment.status == status)
    if order_id:
        query = query.where(PurchaseOrderAdjustment.order_id == order_id)

    # 按创建时间倒序
    query = query.order_by(PurchaseOrderAdjustment.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    adjustments = result.scalars().all()

    # 获取总数
    count_query = select(func.count(PurchaseOrderAdjustment.id))
    if status:
        count_query = count_query.where(PurchaseOrderAdjustment.status == status)
    if order_id:
        count_query = count_query.where(PurchaseOrderAdjustment.order_id == order_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": a.id,
                "order_id": a.order_id,
                "order_no": a.order.order_no if a.order else None,
                "supplier_id": a.supplier_id,
                "supplier_name": a.supplier.name if a.supplier else None,
                "reason": a.reason,
                "adjustment_items": json.loads(a.adjustment_items) if a.adjustment_items else None,
                "status": a.status.value,
                "reviewed_at": a.reviewed_at,
                "reviewed_by": a.reviewed_by,
                "created_at": a.created_at,
            }
            for a in adjustments
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/orders/{order_id}/adjustments")
async def get_order_adjustments(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查看订单的调整申请历史"""
    result = await db.execute(
        select(PurchaseOrderAdjustment)
        .where(PurchaseOrderAdjustment.order_id == order_id)
        .order_by(PurchaseOrderAdjustment.created_at.desc())
    )
    adjustments = result.scalars().all()

    return {
        "items": [
            {
                "id": a.id,
                "order_id": a.order_id,
                "reason": a.reason,
                "adjustment_items": json.loads(a.adjustment_items) if a.adjustment_items else None,
                "status": a.status.value,
                "reviewed_at": a.reviewed_at,
                "reviewed_by": a.reviewed_by,
                "created_at": a.created_at,
            }
            for a in adjustments
        ],
    }


@router.post("/orders/{order_id}/adjustments/{adjustment_id}/approve")
async def approve_adjustment(
    order_id: int,
    adjustment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批准调整申请"""
    # 获取调整申请
    result = await db.execute(
        select(PurchaseOrderAdjustment)
        .where(PurchaseOrderAdjustment.id == adjustment_id)
        .where(PurchaseOrderAdjustment.order_id == order_id)
    )
    adjustment = result.scalar_one_or_none()

    if not adjustment:
        raise HTTPException(status_code=404, detail="调整申请不存在")

    if adjustment.status != AdjustmentStatus.PENDING:
        raise HTTPException(status_code=400, detail="申请已处理")

    # 更新申请状态
    adjustment.status = AdjustmentStatus.APPROVED
    adjustment.reviewed_at = datetime.now()
    adjustment.reviewed_by = current_user.id

    # 重置订单的供应商确认状态，允许供应商重新确认
    order_result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == order_id))
    order = order_result.scalar_one_or_none()

    if order:
        order.supplier_confirm_status = None  # 重置为待确认
        order.supplier_confirmed_at = None

    await db.commit()

    return {"message": "已批准调整申请"}


@router.post("/orders/{order_id}/adjustments/{adjustment_id}/reject")
async def reject_adjustment(
    order_id: int,
    adjustment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """拒绝调整申请"""
    # 获取调整申请
    result = await db.execute(
        select(PurchaseOrderAdjustment)
        .where(PurchaseOrderAdjustment.id == adjustment_id)
        .where(PurchaseOrderAdjustment.order_id == order_id)
    )
    adjustment = result.scalar_one_or_none()

    if not adjustment:
        raise HTTPException(status_code=404, detail="调整申请不存在")

    if adjustment.status != AdjustmentStatus.PENDING:
        raise HTTPException(status_code=400, detail="申请已处理")

    # 更新申请状态
    adjustment.status = AdjustmentStatus.REJECTED
    adjustment.reviewed_at = datetime.now()
    adjustment.reviewed_by = current_user.id

    await db.commit()

    return {"message": "已拒绝调整申请"}
