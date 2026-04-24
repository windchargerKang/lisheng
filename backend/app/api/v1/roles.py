"""
角色管理 API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.services.role_service import RoleService
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleListResponse, RoleWithPermissions, RolePermissionUpdate

router = APIRouter(prefix="/roles", tags=["角色管理"])


def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    """获取角色服务实例"""
    return RoleService(db)


@router.get("", response_model=RoleListResponse)
async def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
):
    """获取角色列表"""
    result = await role_service.get_list(page=page, page_size=page_size)

    return {
        "items": [
            RoleResponse(
                id=role.id,
                name=role.name,
                code=role.code,
                description=role.description,
                created_at=role.created_at,
                updated_at=role.updated_at,
            )
            for role in result["items"]
        ],
        "total": result["total"],
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
):
    """创建角色"""
    try:
        role = await role_service.create(
            name=role_data.name,
            code=role_data.code,
            description=role_data.description,
        )
        return RoleResponse(
            id=role.id,
            name=role.name,
            code=role.code,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{role_id}", response_model=RoleWithPermissions)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
):
    """获取角色详情"""
    role = await role_service.get_by_id(role_id)

    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    return RoleWithPermissions(
        id=role.id,
        name=role.name,
        code=role.code,
        description=role.description,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permissions=[
            {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "type": p.type.value,
                "parent_id": p.parent_id,
            }
            for p in role.permissions
        ],
    )


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
):
    """更新角色"""
    try:
        role = await role_service.update(
            role_id=role_id,
            name=role_data.name,
            description=role_data.description,
        )
        return RoleResponse(
            id=role.id,
            name=role.name,
            code=role.code,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
):
    """删除角色"""
    try:
        await role_service.delete(role_id)
        return {"message": "角色删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{role_id}/permissions")
async def get_role_permissions(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
):
    """获取角色权限"""
    try:
        permissions = await role_service.get_permissions(role_id)
        return {
            "role_id": role_id,
            "permissions": [
                {"id": p.id, "code": p.code, "name": p.name, "type": p.type.value, "parent_id": p.parent_id}
                for p in permissions
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{role_id}/permissions")
async def update_role_permissions(
    role_id: int,
    permission_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
):
    """配置角色权限"""
    try:
        await role_service.update_permissions(role_id, permission_ids)
        return {"message": "权限配置成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
