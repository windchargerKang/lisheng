"""
权限管理服务
"""
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user import User


class PermissionService:
    """权限服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_grouped(self) -> Dict[str, List[Permission]]:
        """获取所有权限（按类型分组）"""
        result = await self.db.execute(
            select(Permission).order_by(Permission.type, Permission.code)
        )
        permissions = result.scalars().all()

        # 按类型分组
        permissions_by_type: Dict[str, List[Permission]] = {}
        for p in permissions:
            ptype = p.type.value
            if ptype not in permissions_by_type:
                permissions_by_type[ptype] = []
            permissions_by_type[ptype].append(p)

        return permissions_by_type

    async def get_user_permissions(self, user: User) -> List[Permission]:
        """获取用户权限列表"""
        if not user.role_id:
            return []

        result = await self.db.execute(
            select(Permission)
            .join(RolePermission)
            .where(RolePermission.role_id == user.role_id)
        )
        return result.scalars().all()

    async def get_user_permission_codes(self, user: User) -> List[str]:
        """获取用户权限代码列表"""
        permissions = await self.get_user_permissions(user)
        return [p.code for p in permissions]

    async def has_permission(self, user: User, permission_code: str) -> bool:
        """检查用户是否有指定权限"""
        permission_codes = await self.get_user_permission_codes(user)
        return permission_code in permission_codes
