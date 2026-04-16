"""
创建索引脚本
用于在现有数据库上创建必要的索引
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.config import settings


# 需要创建的索引
INDEXES = [
    # regions 表：加速树形查询
    "CREATE INDEX IF NOT EXISTS idx_regions_parent_id ON regions(parent_id)",

    # shops 表：加速用户和区域查询
    "CREATE INDEX IF NOT EXISTS idx_shops_user_id ON shops(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_shops_region_id ON shops(region_id)",

    # agents 表：加速用户和区域查询
    "CREATE INDEX IF NOT EXISTS idx_agents_user_id ON agents(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_agents_region_id ON agents(region_id)",

    # price_tiers 表：加速产品定价查询
    "CREATE INDEX IF NOT EXISTS idx_price_tiers_product_id ON price_tiers(product_id)",
]


async def main():
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    print("开始创建索引...")
    async with engine.begin() as conn:
        for sql in INDEXES:
            try:
                await conn.execute(text(sql))
                print(f"✓ {sql}")
            except Exception as e:
                print(f"✗ {sql} - {e}")

    print("索引创建完成！")


if __name__ == "__main__":
    asyncio.run(main())
