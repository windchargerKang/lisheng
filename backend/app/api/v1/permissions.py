"""
权限管理 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/permissions", tags=["权限管理"])


def get_permission_service(db: AsyncSession = Depends(get_db)) -> PermissionService:
    """获取权限服务实例"""
    return PermissionService(db)


@router.get("/my")
async def get_my_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
):
    """获取当前用户权限列表"""
    permissions = await permission_service.get_user_permissions(current_user)

    return {
        "permissions": [
            {"code": p.code, "name": p.name, "type": p.type.value}
            for p in permissions
        ]
    }


@router.get("")
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
):
    """获取所有权限列表"""
    permissions_by_type = await permission_service.get_all_grouped()

    return {
        ptype: [
            {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "type": ptype,
                "parent_id": p.parent_id,
            }
            for p in perms
        ]
        for ptype, perms in permissions_by_type.items()
    }
