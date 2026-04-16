"""
创建初始管理员用户脚本
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User


async def main():
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        # 检查是否已存在管理员
        result = await session.execute(select(User).where(User.username == "admin"))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("管理员用户已存在！")
            return

        # 创建管理员用户
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            role_type="admin"
        )

        session.add(admin_user)
        await session.commit()

        print("管理员用户创建成功！")
        print("用户名：admin")
        print("密码：admin123")
        print("")
        print("⚠️  请在生产环境中修改默认密码！")


if __name__ == "__main__":
    asyncio.run(main())
