"""
供应商管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.supplier import Supplier
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class SupplierCreateRequest(BaseModel):
    """创建供应商请求"""
    name: str
    credit_code: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    settlement_type: str = "cash"


class SupplierUpdateRequest(BaseModel):
    """更新供应商请求"""
    name: Optional[str] = None
    credit_code: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    settlement_type: Optional[str] = None
    status: Optional[str] = None


@router.get("")
async def list_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取供应商列表（分页、筛选）"""
    query = select(Supplier)

    if status:
        query = query.where(Supplier.status == status)

    # 按创建时间倒序
    query = query.order_by(Supplier.created_at.desc())

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    suppliers = result.scalars().all()

    # 获取总数
    count_query = select(func.count(Supplier.id))
    if status:
        count_query = count_query.where(Supplier.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "credit_code": s.credit_code,
                "contact_name": s.contact_name,
                "contact_phone": s.contact_phone,
                "settlement_type": s.settlement_type,
                "status": s.status,
                "created_at": s.created_at,
            }
            for s in suppliers
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
async def create_supplier(
    request: SupplierCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建供应商"""
    supplier = Supplier(
        name=request.name,
        credit_code=request.credit_code,
        contact_name=request.contact_name,
        contact_phone=request.contact_phone,
        address=request.address,
        bank_name=request.bank_name,
        bank_account=request.bank_account,
        settlement_type=request.settlement_type,
    )
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)

    return {
        "id": supplier.id,
        "name": supplier.name,
        "credit_code": supplier.credit_code,
    }


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取供应商详情"""
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()

    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    return {
        "id": supplier.id,
        "name": supplier.name,
        "credit_code": supplier.credit_code,
        "contact_name": supplier.contact_name,
        "contact_phone": supplier.contact_phone,
        "address": supplier.address,
        "bank_name": supplier.bank_name,
        "bank_account": supplier.bank_account,
        "settlement_type": supplier.settlement_type,
        "status": supplier.status,
        "created_at": supplier.created_at,
    }


@router.put("/{supplier_id}")
async def update_supplier(
    supplier_id: int,
    request: SupplierUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新供应商"""
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()

    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    if request.name:
        supplier.name = request.name
    if request.credit_code:
        supplier.credit_code = request.credit_code
    if request.contact_name:
        supplier.contact_name = request.contact_name
    if request.contact_phone:
        supplier.contact_phone = request.contact_phone
    if request.address:
        supplier.address = request.address
    if request.bank_name:
        supplier.bank_name = request.bank_name
    if request.bank_account:
        supplier.bank_account = request.bank_account
    if request.settlement_type:
        supplier.settlement_type = request.settlement_type
    if request.status:
        supplier.status = request.status

    await db.commit()
    await db.refresh(supplier)

    return {"id": supplier.id, "name": supplier.name}


@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除供应商"""
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()

    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    # 检查是否有关联的采购订单
    from app.models.purchase_order import PurchaseOrder
    order_result = await db.execute(
        select(PurchaseOrder).where(PurchaseOrder.supplier_id == supplier_id)
    )
    orders = order_result.scalars().all()

    if orders:
        raise HTTPException(status_code=400, detail="供应商存在关联的采购订单，无法删除")

    await db.delete(supplier)
    await db.commit()

    return {"message": "删除成功"}
