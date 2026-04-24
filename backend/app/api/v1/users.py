"""
用户管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.services.user_service import UserService
from app.services.wallet_service import WalletService
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse, DisableUserRequest, ResetPasswordRequest

router = APIRouter(prefix="/users", tags=["用户管理"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """获取用户服务实例"""
    return UserService(db)


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    role_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """获取用户列表"""
    result = await user_service.get_list(
        page=page,
        page_size=page_size,
        role_id=role_id,
        status=status,
        username=username,
    )

    return {
        "items": [
            UserResponse(
                id=user.id,
                username=user.username,
                role_id=user.role_id,
                role_name=user.role.name if user.role else None,
                role_code=user.role.code if user.role else None,
                status=user.status.value if user.status else "ACTIVE",
                last_login_at=user.last_login_at,
                last_login_ip=user.last_login_ip,
                created_at=user.created_at,
            )
            for user in result["items"]
        ],
        "total": result["total"],
        "page": page,
        "page_size": page_size,
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """获取用户详情"""
    user = await user_service.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return UserResponse(
        id=user.id,
        username=user.username,
        role_id=user.role_id,
        role_name=user.role.name if user.role else None,
        role_code=user.role.code if user.role else None,
        status=user.status.value if user.status else "ACTIVE",
        last_login_at=user.last_login_at,
        last_login_ip=user.last_login_ip,
        created_at=user.created_at,
    )


@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """创建用户"""
    import logging
    logger = logging.getLogger(__name__)

    try:
        user = await user_service.create(
            username=user_data.username,
            password=user_data.password,
            role_id=user_data.role_id,
        )
        logger.info(f"创建用户成功：{user.id}, {user.username}, role_id={user.role_id}")

        # 为用户创建钱包
        wallet_service = WalletService(db)
        await wallet_service.create_wallet(user_id=user.id)
        logger.info(f"创建钱包成功：user_id={user.id}")

        # 重新查询带角色关联的用户
        result = await db.execute(
            select(User).options(selectinload(User.role)).where(User.id == user.id)
        )
        user_with_role = result.scalar_one_or_none()
        logger.info(f"查询用户带角色：{user_with_role}")
        logger.info(f"角色对象：{user_with_role.role if user_with_role else None}")

        response_data = UserResponse(
            id=user_with_role.id,
            username=user_with_role.username,
            role_id=user_with_role.role_id,
            role_name=user_with_role.role.name if user_with_role.role else None,
            role_code=user_with_role.role.code if user_with_role.role else None,
            status=user_with_role.status.value if user_with_role.status else "ACTIVE",
            last_login_at=user_with_role.last_login_at,
            last_login_ip=user_with_role.last_login_ip,
            created_at=user_with_role.created_at,
        )
        logger.info(f"响应数据：{response_data}")
        return response_data
    except Exception as e:
        logger.error(f"创建用户失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """更新用户"""
    try:
        user = await user_service.update(
            user_id=user_id,
            role_id=user_data.role_id,
            password=user_data.password,
        )
        return UserResponse(
            id=user.id,
            username=user.username,
            role_id=user.role_id,
            role_name=user.role.name if user.role else None,
            role_code=user.role.code if user.role else None,
            status=user.status.value if user.status else "ACTIVE",
            last_login_at=user.last_login_at,
            last_login_ip=user.last_login_ip,
            created_at=user.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """删除用户"""
    try:
        await user_service.delete(user_id, current_user.id)
        return {"message": "用户删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{user_id}/disable")
async def disable_user(
    user_id: int,
    disable_data: DisableUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """禁用/启用用户"""
    try:
        user = await user_service.toggle_status(user_id, current_user.id, disable_data.disable)
        status_text = "已禁用" if disable_data.disable else "已启用"
        return {"message": f"用户{status_text}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    password_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """重置密码"""
    try:
        await user_service.reset_password(user_id, password_data.password)
        return {"message": "密码重置成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
