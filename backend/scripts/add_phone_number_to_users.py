"""
为 users 表添加 phone_number 字段
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.config import settings


async def main():
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    print("开始添加 phone_number 字段...")
    async with engine.begin() as conn:
        # 添加 phone_number 字段
        try:
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) NULL"
            ))
            print("✓ phone_number 字段添加成功")
        except Exception as e:
            print(f"✗ phone_number 字段添加失败 - {e}")

        # 添加唯一索引
        try:
            await conn.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_phone_number ON users(phone_number)"
            ))
            print("✓ phone_number 唯一索引创建成功")
        except Exception as e:
            print(f"✗ phone_number 唯一索引创建失败 - {e}")

        # 添加普通索引
        try:
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_users_phone_number_lookup ON users(phone_number)"
            ))
            print("✓ phone_number 查询索引创建成功")
        except Exception as e:
            print(f"✗ phone_number 查询索引创建失败 - {e}")

    print("迁移完成！")


if __name__ == "__main__":
    asyncio.run(main())
