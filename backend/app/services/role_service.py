"""
角色管理服务
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user import User


class RoleService:
    """角色服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self, page: int = 1, page_size: int = 10):
        """获取角色列表"""
        # 查询总数
        count_result = await self.db.execute(select(func.count()).select_from(Role))
        total = count_result.scalar()

        # 查询角色列表
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Role)
            .offset(offset)
            .limit(page_size)
            .order_by(Role.created_at.desc(), Role.id.desc())
        )
        roles = result.scalars().all()

        return {
            "items": roles,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        """获取角色详情"""
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        return result.scalars().first()

    async def create(self, name: str, code: str, description: Optional[str] = None) -> Role:
        """创建角色"""
        # 检查角色代码是否已存在
        result = await self.db.execute(select(Role).where(Role.code == code))
        if result.scalar():
            raise ValueError("角色代码已存在")

        role = Role(name=name, code=code, description=description)
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def update(self, role_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Role:
        """更新角色"""
        role = await self.get_by_id(role_id)
        if not role:
            raise ValueError("角色不存在")

        if name is not None:
            role.name = name
        if description is not None:
            role.description = description

        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def delete(self, role_id: int) -> bool:
        """删除角色"""
        role = await self.get_by_id(role_id)
        if not role:
            raise ValueError("角色不存在")

        # 检查是否有用户使用该角色
        user_result = await self.db.execute(select(User).where(User.role_id == role_id))
        if user_result.scalars().first():
            raise ValueError("该角色已被用户使用，无法删除")

        await self.db.delete(role)
        await self.db.commit()
        return True

    async def get_permissions(self, role_id: int) -> List[Permission]:
        """获取角色权限"""
        role = await self.get_by_id(role_id)
        if not role:
            raise ValueError("角色不存在")
        return role.permissions

    async def update_permissions(self, role_id: int, permission_ids: List[int]) -> bool:
        """配置角色权限"""
        role = await self.get_by_id(role_id)
        if not role:
            raise ValueError("角色不存在")

        # 验证权限 ID 是否存在
        perm_result = await self.db.execute(
            select(Permission).where(Permission.id.in_(permission_ids))
        )
        permissions = perm_result.scalars().all()

        if len(permissions) != len(permission_ids):
            raise ValueError("存在无效的权限 ID")

        # 使用事务：先删除旧权限，再插入新权限
        async with self.db.begin():
            # 删除旧权限
            await self.db.execute(
                RolePermission.__table__.delete()
                .where(RolePermission.__table__.c.role_id == role_id)
            )

            # 批量插入新权限
            await self.db.bulk_insert_mappings(
                RolePermission,
                [{"role_id": role_id, "permission_id": pid} for pid in permission_ids]
            )

        return True
