"""
权限检查中间件/装饰器
"""
from functools import wraps
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.permission_service import PermissionService

security = HTTPBearer(auto_error=False)


class PermissionDenied(Exception):
    """权限不足异常"""
    pass


def require_permission(permission_code: str):
    """
    权限检查装饰器

    使用方式：
    @router.get("/users")
    @require_permission("user:view")
    async def list_users(...):
        ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中获取 request 和 current_user
            request = None
            current_user = None
            db = None

            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                elif isinstance(arg, User):
                    current_user = arg
                elif isinstance(arg, AsyncSession):
                    db = arg

            # 从 kwargs 获取
            if request is None:
                request = kwargs.get("request")
            if current_user is None:
                current_user = kwargs.get("current_user")
            if db is None:
                db = kwargs.get("db")

            if not current_user:
                raise HTTPException(status_code=401, detail="未认证")

            if not current_user.role_id:
                raise HTTPException(status_code=403, detail="用户未分配角色")

            # 检查权限
            if db:
                permission_service = PermissionService(db)
                has_permission = await permission_service.has_permission(current_user, permission_code)
                if not has_permission:
                    raise HTTPException(status_code=403, detail=f"缺少权限：{permission_code}")

            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def check_permission(
    user: User,
    permission_code: str,
    db: AsyncSession
) -> bool:
    """
    检查用户是否有指定权限

    使用方式：
    has_perm = await check_permission(current_user, "user:view", db)
    if not has_perm:
        raise HTTPException(status_code=403, detail="缺少权限")
    """
    if not user.role_id:
        return False

    permission_service = PermissionService(db)
    return await permission_service.has_permission(user, permission_code)


async def get_user_permission_codes(
    user: User,
    db: AsyncSession
) -> list[str]:
    """
    获取用户的权限代码列表

    使用方式：
    permissions = await get_user_permission_codes(current_user, db)
    """
    if not user.role_id:
        return []

    permission_service = PermissionService(db)
    return await permission_service.get_user_permission_codes(user)
