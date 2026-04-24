"""
核销管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.verification_code_service import VerificationCodeService
from app.services.profit_service import ProfitService
from app.schemas.verification import VerificationRequest, VerificationResponse, VerificationCodeResponse

router = APIRouter()


@router.get("/{code}")
async def get_verification_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """验证核销码（查询核销码状态）

    仅店铺账号可以查询
    """
    # 检查是否为店铺账号
    if current_user.role_type not in ["shop", "admin"]:
        raise HTTPException(status_code=403, detail="只有店铺账号可以查询核销码")

    verification_service = VerificationCodeService(db)
    verification_code = await verification_service.get_by_code(code)

    if not verification_code:
        raise HTTPException(status_code=404, detail="核销码不存在")

    return {
        "code": verification_code.code,
        "status": verification_code.status.value,
        "order_id": verification_code.order_id,
        "order_no": verification_code.order.order_no if verification_code.order else None,
        "created_at": verification_code.created_at,
        "used_at": verification_code.used_at,
    }


@router.post("/verify")
async def verify_order(
    request: VerificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """核销订单

    流程：
    1. 验证核销码有效且未使用
    2. 计算分润（服务费 30%，区代利润 10%）
    3. 执行分润转账
    4. 更新订单状态为 verified

    仅店铺账号可以执行核销
    """
    # 检查是否为店铺账号
    if current_user.role_type not in ["shop", "admin"]:
        raise HTTPException(status_code=403, detail="只有店铺账号可以执行核销")

    verification_service = VerificationCodeService(db)
    profit_service = ProfitService(db)

    try:
        # 验证并使用核销码
        verification_code, order = await verification_service.verify_and_use(
            code=request.verification_code,
            verified_by=current_user.id
        )

        # 执行分润转账
        service_fee, agent_profit = await profit_service.distribute_profit(
            order=order,
            verifier_user_id=current_user.id
        )

        await db.commit()

        return {
            "message": "核销成功",
            "order_id": order.id,
            "order_no": order.order_no,
            "service_fee": float(service_fee),
            "agent_profit": float(agent_profit),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
