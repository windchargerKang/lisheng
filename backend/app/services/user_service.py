"""
用户管理服务
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.user import User, UserStatus
from app.models.role import Role
from app.core.security import get_password_hash, verify_password


class UserService:
    """用户服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        page: int = 1,
        page_size: int = 10,
        role_id: Optional[int] = None,
        status: Optional[str] = None,
        username: Optional[str] = None,
    ):
        """获取用户列表"""
        # 构建查询条件
        conditions = []
        if role_id:
            conditions.append(User.role_id == role_id)
        if status:
            conditions.append(User.status == status)
        if username:
            conditions.append(User.username.like(f"%{username}%"))

        # 查询总数
        count_query = select(func.count()).select_from(User)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # 查询用户列表
        query = (
            select(User)
            .options(selectinload(User.role))
            .order_by(User.created_at.desc(), User.id.desc())
        )
        if conditions:
            query = query.where(and_(*conditions))

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        users = result.scalars().all()

        return {
            "items": users,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """获取用户详情"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def create(
        self,
        username: str,
        password: str,
        role_id: Optional[int] = None,
    ) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        existing = await self.get_by_username(username)
        if existing:
            raise ValueError("用户名已存在")

        # 验证角色是否存在
        if role_id is not None:
            role_result = await self.db.execute(select(Role).where(Role.id == role_id))
            if not role_result.scalar():
                raise ValueError("角色不存在")

        user = User(
            username=username,
            password_hash=get_password_hash(password),
            role_id=role_id,
            status=UserStatus.ACTIVE,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(
        self,
        user_id: int,
        role_id: Optional[int] = None,
        password: Optional[str] = None,
    ) -> User:
        """更新用户"""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")

        # 更新角色
        if role_id is not None:
            if role_id:
                role_result = await self.db.execute(select(Role).where(Role.id == role_id))
                if not role_result.scalar():
                    raise ValueError("角色不存在")
            user.role_id = role_id

        # 更新密码
        if password:
            user.password_hash = get_password_hash(password)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int, current_user_id: int) -> bool:
        """删除用户（软删除：禁用账号并清除敏感信息）"""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")

        # 不允许删除自己
        if user.id == current_user_id:
            raise ValueError("不能删除自己的账号")

        # 软删除：禁用账号并清除敏感信息
        user.status = UserStatus.DISABLED
        user.password_hash = ""  # 清除密码
        user.last_login_ip = None
        user.last_login_at = None
        # 清除手机号等敏感信息（如果有）
        if hasattr(user, 'phone'):
            user.phone = None
        if hasattr(user, 'email'):
            user.email = None

        await self.db.commit()
        await self.db.refresh(user)
        return True

    async def toggle_status(self, user_id: int, current_user_id: int, disable: bool) -> User:
        """禁用/启用用户"""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")

        # 不允许禁用自己
        if user.id == current_user_id:
            raise ValueError("不能禁用/启用自己的账号")

        user.status = UserStatus.DISABLED if disable else UserStatus.ACTIVE
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def reset_password(self, user_id: int, new_password: str) -> bool:
        """重置密码"""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")

        if not new_password or len(new_password) < 6:
            raise ValueError("密码长度至少 6 位")

        user.password_hash = get_password_hash(new_password)
        await self.db.commit()
        return True

    async def login(self, username: str, password: str, client_ip: Optional[str] = None) -> User:
        """用户登录"""
        user = await self.get_by_username(username)
        if not user:
            raise ValueError("用户名或密码错误")

        # 检查用户状态
        if user.status == UserStatus.DISABLED:
            raise ValueError("账号已被禁用，请联系管理员")

        # 验证密码
        if not verify_password(password, user.password_hash):
            raise ValueError("用户名或密码错误")

        # 更新登录信息
        user.last_login_at = datetime.now()
        user.last_login_ip = client_ip
        await self.db.commit()
        await self.db.refresh(user)

        return user
