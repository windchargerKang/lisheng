"""
角色管理相关的 Pydantic Schemas
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    """角色基础 Schema"""
    name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    code: str = Field(..., min_length=1, max_length=50, description="角色代码")
    description: Optional[str] = Field(None, max_length=200, description="角色描述")


class RoleCreate(RoleBase):
    """创建角色请求"""
    pass


class RoleUpdate(BaseModel):
    """更新角色请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="角色名称")
    description: Optional[str] = Field(None, max_length=200, description="角色描述")


class RoleResponse(BaseModel):
    """角色响应"""
    id: int
    name: str
    code: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    """权限基础 Schema"""
    code: str = Field(..., min_length=1, max_length=100, description="权限代码")
    name: str = Field(..., min_length=1, max_length=50, description="权限名称")
    type: str = Field(..., description="权限类型：MENU/BUTTON/DATA")


class PermissionResponse(PermissionBase):
    """权限响应"""
    id: int
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True


class RoleWithPermissions(RoleResponse):
    """带权限的角色响应"""
    permissions: List[PermissionResponse] = []


class RolePermissionUpdate(BaseModel):
    """角色权限更新请求"""
    permission_ids: List[int] = Field(..., description="权限 ID 列表")


class RoleListResponse(BaseModel):
    """角色列表响应"""
    items: List[RoleResponse]
    total: int
    page: int
    page_size: int
