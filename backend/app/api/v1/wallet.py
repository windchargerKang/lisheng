"""
钱包管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from typing import Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.wallet import Wallet
from app.models.wallet_transaction import TransactionType, TransactionStatus
from app.services.wallet_service import WalletService
from app.schemas.wallet import (
    WalletResponse,
    WalletTransactionResponse,
    RechargeRequest,
    WithdrawRequest,
    ApproveWithdrawRequest,
    WalletListResponse,
    WalletTransactionListResponse,
)

router = APIRouter()


@router.get("", response_model=WalletResponse)
async def get_wallet(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询当前用户钱包余额"""
    wallet_service = WalletService(db)
    wallet = await wallet_service.get_wallet_by_user_id(current_user.id)

    if not wallet:
        raise HTTPException(status_code=404, detail="钱包不存在")

    return wallet


@router.post("/recharge")
async def recharge(
    request: RechargeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """充值接口
    - 普通用户：只能给自己充值（user_id 必须等于当前用户 ID）
    - 管理员：可以给任何用户充值（代客充值）
    """
    wallet_service = WalletService(db)

    # 非管理员只能给自己充值
    if current_user.role_type != "admin":
        if request.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="只能给自己充值")
    # 管理员可以给任何人充值

    try:
        wallet, transaction = await wallet_service.recharge(
            user_id=request.user_id,
            amount=request.amount,
            remark=request.remark
        )
        await db.commit()

        return {
            "message": "充值成功",
            "wallet": {
                "id": wallet.id,
                "user_id": wallet.user_id,
                "balance": wallet.balance,
            },
            "transaction": {
                "id": transaction.id,
                "transaction_no": transaction.transaction_no,
                "amount": transaction.amount,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/withdraw")
async def withdraw(
    request: WithdrawRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """用户申请提现"""
    wallet_service = WalletService(db)

    try:
        wallet, transaction = await wallet_service.withdraw(
            user_id=current_user.id,
            amount=request.amount,
            withdraw_method=request.withdraw_method,
            withdraw_account=request.withdraw_account,
            remark=request.remark
        )
        await db.commit()

        return {
            "message": "提现申请已提交，等待审核",
            "transaction": {
                "id": transaction.id,
                "transaction_no": transaction.transaction_no,
                "amount": transaction.amount,
                "status": transaction.status,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/withdraw/{transaction_id}/approve")
async def approve_withdraw(
    transaction_id: int,
    request: ApproveWithdrawRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员审核提现申请"""
    # 检查管理员权限
    if current_user.role_type != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以执行审核操作")

    wallet_service = WalletService(db)

    try:
        wallet, transaction = await wallet_service.approve_withdraw(
            transaction_id=transaction_id,
            approved=request.approved
        )
        await db.commit()

        status_msg = "审核通过，提现已完成" if request.approved else "审核拒绝"
        return {
            "message": status_msg,
            "transaction": {
                "id": transaction.id,
                "status": transaction.status,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions", response_model=WalletTransactionListResponse)
async def get_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    wallet_id: Optional[int] = Query(None),
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询流水记录
    - 普通用户：查询自己的流水（wallet_id 参数无效）
    - 管理员：可查询指定钱包的流水（需传 wallet_id）
    """
    wallet_service = WalletService(db)

    # 管理员可以查询指定钱包的流水
    if current_user.role_type == "admin" and wallet_id:
        target_wallet_id = wallet_id
    else:
        # 普通用户只能查询自己的钱包
        wallet = await wallet_service.get_wallet_by_user_id(current_user.id)
        if not wallet:
            raise HTTPException(status_code=404, detail="钱包不存在")
        target_wallet_id = wallet.id

    result = await wallet_service.get_transactions(
        wallet_id=target_wallet_id,
        page=page,
        page_size=page_size,
        transaction_type=transaction_type,
        status=status
    )

    return {
        "items": result["items"],
        "total": result["total"],
        "page": page,
        "page_size": page_size,
    }


@router.get("/admin/wallets", response_model=WalletListResponse)
async def get_all_wallets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员查看所有用户钱包"""
    # 检查管理员权限
    if current_user.role_type != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以查看此信息")

    wallet_service = WalletService(db)
    result = await wallet_service.get_all_wallets(
        page=page,
        page_size=page_size,
        user_id=user_id
    )

    return {
        "items": result["items"],
        "total": result["total"],
        "page": page,
        "page_size": page_size,
    }


@router.get("/admin/transactions", response_model=WalletTransactionListResponse)
async def get_all_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员查看所有流水记录"""
    # 检查管理员权限
    if current_user.role_type != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以查看此信息")

    wallet_service = WalletService(db)
    result = await wallet_service.get_all_transactions(
        page=page,
        page_size=page_size,
        transaction_type=transaction_type,
        status=status
    )

    return {
        "items": result["items"],
        "total": result["total"],
        "page": page,
        "page_size": page_size,
    }
