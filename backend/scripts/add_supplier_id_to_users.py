"""
添加 users.supplier_id 列的迁移脚本
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.core.config import settings


async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # 检查列是否存在
        result = await conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]

        if "supplier_id" in columns:
            print("supplier_id 列已存在，无需迁移")
            return

        print("正在添加 supplier_id 列...")
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN supplier_id INTEGER"
        ))
        await conn.execute(text(
            "CREATE INDEX idx_supplier_id ON users(supplier_id)"
        ))
        print("supplier_id 列添加成功！")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
