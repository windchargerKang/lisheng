"""
认证相关的 Pydantic Schemas
"""
from pydantic import BaseModel
from typing import Optional, List


class LoginRequest(BaseModel):
    """登录请求"""
    username: str  # 支持用户名或手机号登录
    password: str


class LoginByPhoneRequest(BaseModel):
    """手机号登录请求（可选，保留兼容性）"""
    phone_number: str
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


class UserCreatePhone(BaseModel):
    """手机号注册请求"""
    phone_number: str
    password: str
    confirm_password: str

    def validate(self) -> None:
        """验证密码一致性"""
        if self.password != self.confirm_password:
            raise ValueError("两次输入的密码不一致")

        # 验证手机号格式（11 位数字）
        import re
        if not re.match(r"^1\d{10}$", self.phone_number):
            raise ValueError("手机号格式不正确")


class UserInDB(UserBase):
    """数据库用户 Schema"""
    id: int
    phone_number: Optional[str] = None
    role_id: Optional[int] = None
    role_code: Optional[str] = None  # 从 role.code 获取

    class Config:
        from_attributes = True


class UserRoleInfo(BaseModel):
    """用户角色信息"""
    id: int
    role_code: str  # role.code: customer/shop/agent/admin
    role_name: str
    is_active: bool = True

    class Config:
        from_attributes = True


class UserRoleListResponse(BaseModel):
    """用户角色列表响应"""
    roles: List[UserRoleInfo]
    current_role_id: Optional[int] = None
