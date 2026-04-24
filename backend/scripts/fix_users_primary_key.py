"""
修复 users 表的主键问题
SQLite 不支持直接修改主键，需要重建表
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.config import settings


async def main():
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    print("开始修复 users 表主键...")
    async with engine.begin() as conn:
        # 1. 备份现有数据
        try:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users_backup AS SELECT * FROM users
            """))
            print("✓ 数据备份成功")
        except Exception as e:
            print(f"✗ 数据备份失败 - {e}")
            return

        # 2. 删除旧表
        try:
            await conn.execute(text("DROP TABLE users"))
            print("✓ 旧表删除成功")
        except Exception as e:
            print(f"✗ 旧表删除失败 - {e}")
            return

        # 3. 创建新表（正确的主键定义）
        try:
            await conn.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(20) NULL,
                    role_id INTEGER,
                    supplier_id INTEGER,
                    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
                    last_login_at DATETIME,
                    last_login_ip VARCHAR(45),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✓ 新表创建成功")
        except Exception as e:
            print(f"✗ 新表创建失败 - {e}")
            return

        # 4. 创建索引
        try:
            await conn.execute(text("CREATE UNIQUE INDEX idx_users_username ON users(username)"))
            await conn.execute(text("CREATE UNIQUE INDEX idx_users_phone_number ON users(phone_number)"))
            await conn.execute(text("CREATE INDEX idx_users_role_id ON users(role_id)"))
            await conn.execute(text("CREATE INDEX idx_users_status ON users(status)"))
            print("✓ 索引创建成功")
        except Exception as e:
            print(f"✗ 索引创建失败 - {e}")

        # 5. 恢复数据（如果有）
        try:
            await conn.execute(text("""
                INSERT INTO users (id, username, password_hash, phone_number, role_id, supplier_id, status, last_login_at, last_login_ip, created_at)
                SELECT id, username, password_hash, phone_number, role_id, supplier_id, status, last_login_at, last_login_ip, created_at FROM users_backup WHERE id IS NOT NULL
            """))
            print("✓ 数据恢复成功")
        except Exception as e:
            print(f"✗ 数据恢复失败 - {e}")

        # 6. 删除备份表
        try:
            await conn.execute(text("DROP TABLE users_backup"))
            print("✓ 备份表删除成功")
        except Exception as e:
            print(f"✗ 备份表删除失败 - {e}")

    print("迁移完成！")


if __name__ == "__main__":
    asyncio.run(main())
