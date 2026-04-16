"""
认证相关的 Pydantic Schemas
"""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user: dict


class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str


class UserCreate(UserBase):
    """创建用户"""
    password: str


class UserInDB(UserBase):
    """数据库用户 Schema"""
    id: int
    role_type: str

    class Config:
        from_attributes = True
