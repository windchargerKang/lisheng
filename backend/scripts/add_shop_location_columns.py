"""
为 shops 表添加经纬度字段
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.config import settings


async def main():
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    print("开始添加经纬度字段...")
    async with engine.begin() as conn:
        # 添加 latitude 字段
        try:
            await conn.execute(text(
                "ALTER TABLE shops ADD COLUMN latitude DECIMAL(10, 8) NULL"
            ))
            print("✓ latitude 字段添加成功")
        except Exception as e:
            print(f"✗ latitude 字段添加失败 - {e}")

        # 添加 longitude 字段
        try:
            await conn.execute(text(
                "ALTER TABLE shops ADD COLUMN longitude DECIMAL(11, 8) NULL"
            ))
            print("✓ longitude 字段添加成功")
        except Exception as e:
            print(f"✗ longitude 字段添加失败 - {e}")

    print("迁移完成！")


if __name__ == "__main__":
    asyncio.run(main())
