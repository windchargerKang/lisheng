"""
用户管理相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    role_id: Optional[int] = Field(None, description="角色 ID")


class UserUpdate(BaseModel):
    """更新用户请求"""
    role_id: Optional[int] = Field(None, description="角色 ID")
    password: Optional[str] = Field(None, min_length=6, max_length=128, description="新密码")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    role_code: Optional[str] = None
    status: str = Field(..., description="用户状态：ACTIVE/DISABLED")
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """从 ORM 对象创建响应（兼容 role_type 字段）"""
        role_code = None
        role_name = None
        if hasattr(obj, 'role') and obj.role:
            role_code = obj.role.code
            role_name = obj.role.name
        return cls(
            id=obj.id,
            username=obj.username,
            role_id=obj.role_id,
            role_name=role_name,
            role_code=role_code,
            status=obj.status,
            last_login_at=obj.last_login_at,
            last_login_ip=obj.last_login_ip,
            created_at=obj.created_at,
        )


class UserListResponse(BaseModel):
    """用户列表响应"""
    items: List[UserResponse]
    total: int
    page: int
    page_size: int


class DisableUserRequest(BaseModel):
    """禁用用户请求"""
    disable: bool = Field(True, description="是否禁用")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    password: str = Field(..., min_length=6, max_length=128, description="新密码")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user: dict
