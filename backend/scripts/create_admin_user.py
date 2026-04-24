"""
创建默认管理员账号
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserStatus
from app.models.role import Role


async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # 获取 admin 角色
        result = await conn.execute(
            select(Role).where(Role.code == "admin")
        )
        admin_role = result.scalar_one_or_none()

        if not admin_role:
            print("未找到 admin 角色，请先运行初始化脚本")
            return

        admin_role_id = admin_role.id if hasattr(admin_role, 'id') else admin_role

        # 检查 admin 用户是否存在
        result = await conn.execute(
            select(User).where(User.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("admin 用户已存在，将更新密码")
            existing_admin.password_hash = get_password_hash("admin123")
            await conn.commit()
            print("admin 密码已更新为：admin123")
        else:
            # 创建 admin 用户
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                role_id=admin_role_id,
                status=UserStatus.ACTIVE
            )
            conn.add(admin_user)
            await conn.commit()
            print("admin 用户创建成功")

        print("\n========================================")
        print("管理员账号信息：")
        print("  用户名：admin")
        print("  密码：admin123")
        print("========================================")


if __name__ == "__main__":
    asyncio.run(main())
