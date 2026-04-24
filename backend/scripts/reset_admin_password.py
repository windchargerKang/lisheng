"""
重置 admin 密码为 admin123
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.security import get_password_hash


async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    # 生成 admin123 的密码哈希
    pwd_hash = get_password_hash("admin123")

    async with engine.begin() as conn:
        # 检查 admin 用户是否存在
        result = await conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
        admin = result.fetchone()

        if admin:
            # 更新密码
            await conn.execute(
                text("UPDATE users SET password_hash = :pwd_hash WHERE username = 'admin'"),
                {"pwd_hash": pwd_hash}
            )
            print("admin 密码已重置为：admin123")
        else:
            # 获取 admin 角色 ID
            result = await conn.execute(text("SELECT id FROM roles WHERE code = 'admin'"))
            admin_role = result.fetchone()
            if admin_role:
                await conn.execute(
                    text("""
                        INSERT INTO users (username, password_hash, role_id, status)
                        VALUES ('admin', :pwd_hash, :role_id, 'ACTIVE')
                    """),
                    {"pwd_hash": pwd_hash, "role_id": admin_role[0]}
                )
                print("admin 用户已创建，密码：admin123")
            else:
                print("错误：未找到 admin 角色")
                return

        await conn.commit()

    print("\n========================================")
    print("管理员账号信息：")
    print("  用户名：admin")
    print("  密码：admin123")
    print("========================================")


if __name__ == "__main__":
    asyncio.run(main())
