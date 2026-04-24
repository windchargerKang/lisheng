"""
数据库初始化脚本
"""
import asyncio
from app.core.database import init_db

# 必须导入所有模型，否则表不会被创建
from app.models import (
    User, Region, Shop, Agent, Product, PriceTier,
    Order, OrderItem, CartItem,
    ProfitRecord, WithdrawalRequest,
    Referral,
    # 供应商管理
    Supplier, PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus, SupplierConfirmStatus,
    PurchaseInbound, InboundStatus, Settlement, SettlementType, SettlementStatus,
    # 订单调整
    PurchaseOrderAdjustment, AdjustmentStatus,
    # 店铺/区代申请
    StoreApplication,
)


async def main():
    print("正在初始化数据库...")
    await init_db()
    print("数据库初始化完成！")


if __name__ == "__main__":
    asyncio.run(main())
