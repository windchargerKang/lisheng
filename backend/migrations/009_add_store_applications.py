"""
数据库迁移脚本：009_add_store_applications
创建店铺/区代申请表
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.config import settings


async def main():
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    print("开始创建 store_applications 表...")
    async with engine.begin() as conn:
        # 创建表
        await conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS store_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                apply_type TEXT NOT NULL CHECK(apply_type IN ('SHOP', 'AGENT')),

                -- 店铺申请字段
                shop_name TEXT,
                shop_region_id INTEGER REFERENCES regions(id),
                shop_agent_id INTEGER REFERENCES agents(id),
                shop_latitude REAL,
                shop_longitude REAL,

                -- 区代申请字段
                agent_name TEXT,
                agent_region_id INTEGER REFERENCES regions(id),
                referrer_id INTEGER REFERENCES agents(id),

                -- 审核状态
                status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'APPROVED', 'REJECTED')),
                reject_reason TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
            """
        ))
        print("✓ store_applications 表创建成功")

        # 创建索引
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_store_applications_user_id ON store_applications(user_id)"
        ))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_store_applications_status ON store_applications(status)"
        ))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_store_applications_apply_type ON store_applications(apply_type)"
        ))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_store_applications_created_at ON store_applications(created_at DESC)"
        ))
        print("✓ 索引创建成功")

    print("迁移完成！")


if __name__ == "__main__":
    asyncio.run(main())
