"""
重置用户密码脚本
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.user import User
from app.core.security import get_password_hash


async def reset_password(username: str, new_password: str):
    """重置指定用户的密码"""
    async with async_session_maker() as db_session:
        try:
            result = await db_session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()

            if not user:
                print(f"用户 {username} 不存在")
                return False

            user.password_hash = get_password_hash(new_password)
            await db_session.commit()
            print(f"用户 {username} 密码已重置为：{new_password}")
            return True
        except Exception as e:
            print(f"重置密码失败：{e}")
            await db_session.rollback()
            return False


async def main():
    # 重置 agent_jinshui 的密码
    await reset_password("agent_jinshui", "123456")

    # 也可以重置其他测试账号密码
    await reset_password("shop_test", "123456")
    await reset_password("customer_test", "123456")
    await reset_password("agent_zhengzhou", "123456")


if __name__ == "__main__":
    asyncio.run(main())
