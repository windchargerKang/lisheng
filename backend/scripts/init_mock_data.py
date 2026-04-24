"""
初始化模拟数据脚本
为每个模块生成一批测试数据
"""
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
import random

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserStatus
from app.models.role import Role
from app.models.region import Region
from app.models.shop import Shop
from app.models.agent import Agent
from app.models.product import Product, PriceTier
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus, SupplierConfirmStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import CartItem


# 创建数据库会话
engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ==================== 基础数据 ====================

# 区域数据（省市区）
REGIONS_DATA = [
    # 省级
    {"name": "广东省", "level": 1, "parent_id": None},
    {"name": "浙江省", "level": 1, "parent_id": None},
    {"name": "江苏省", "level": 1, "parent_id": None},
    {"name": "四川省", "level": 1, "parent_id": None},
    {"name": "湖北省", "level": 1, "parent_id": None},

    # 广东省市级
    {"name": "广州市", "level": 2, "parent_id": 1},
    {"name": "深圳市", "level": 2, "parent_id": 1},
    {"name": "佛山市", "level": 2, "parent_id": 1},
    {"name": "东莞市", "level": 2, "parent_id": 1},

    # 浙江市级
    {"name": "杭州市", "level": 2, "parent_id": 2},
    {"name": "宁波市", "level": 2, "parent_id": 2},
    {"name": "温州市", "level": 2, "parent_id": 2},

    # 江苏市级
    {"name": "南京市", "level": 2, "parent_id": 3},
    {"name": "苏州市", "level": 2, "parent_id": 3},

    # 四川市级
    {"name": "成都市", "level": 2, "parent_id": 4},
    {"name": "绵阳市", "level": 2, "parent_id": 4},

    # 湖北市级
    {"name": "武汉市", "level": 2, "parent_id": 5},
    {"name": "宜昌市", "level": 2, "parent_id": 5},

    # 广州市区
    {"name": "天河区", "level": 3, "parent_id": 6},
    {"name": "越秀区", "level": 3, "parent_id": 6},
    {"name": "海珠区", "level": 3, "parent_id": 6},

    # 深圳市区
    {"name": "南山区", "level": 3, "parent_id": 7},
    {"name": "福田区", "level": 3, "parent_id": 7},
    {"name": "宝安区", "level": 3, "parent_id": 7},
]

# 供应商数据
SUPPLIERS_DATA = [
    {"name": "广州食品有限公司", "credit_code": "91440101MA5CU1234X", "contact_name": "张三", "contact_phone": "13800138001", "address": "广州市天河区工业园路 1 号", "bank_name": "工商银行广州天河支行", "bank_account": "6222021234567890123", "settlement_type": "cash"},
    {"name": "深圳电子科技有限公司", "credit_code": "91440301MA5CU5678Y", "contact_name": "李四", "contact_phone": "13800138002", "address": "深圳市南山区科技园路 2 号", "bank_name": "建设银行深圳南山支行", "bank_account": "6222021234567890124", "settlement_type": "credit"},
    {"name": "杭州茶叶有限公司", "credit_code": "91330101MA5CU9012Z", "contact_name": "王五", "contact_phone": "13800138003", "address": "杭州市西湖区龙井路 3 号", "bank_name": "农业银行杭州西湖支行", "bank_account": "6222021234567890125", "settlement_type": "cash"},
    {"name": "苏州丝绸有限公司", "credit_code": "91320501MA5CU3456A", "contact_name": "赵六", "contact_phone": "13800138004", "address": "苏州市姑苏区丝绸路 4 号", "bank_name": "中国银行苏州姑苏支行", "bank_account": "6222021234567890126", "settlement_type": "credit"},
    {"name": "成都调味品有限公司", "credit_code": "91510101MA5CU7890B", "contact_name": "钱七", "contact_phone": "13800138005", "address": "成都市武侯区美食路 5 号", "bank_name": "邮储银行成都武侯支行", "bank_account": "6222021234567890127", "settlement_type": "cash"},
    {"name": "武汉粮油有限公司", "credit_code": "91420101MA5CU2345C", "contact_name": "孙八", "contact_phone": "13800138006", "address": "武汉市江汉区江汉路 6 号", "bank_name": "交通银行武汉江汉支行", "bank_account": "6222021234567890128", "settlement_type": "credit"},
]

# 产品数据
PRODUCTS_DATA = [
    {"name": "精选大米 5kg", "sku_code": "RICE-001", "description": "东北优质大米，颗粒饱满", "stock": 1000, "is_new": 1, "prices": {"retail": 59.90, "shop": 49.90, "agent": 39.90}},
    {"name": "花生油 5L", "sku_code": "OIL-001", "description": "压榨一级花生油", "stock": 500, "is_new": 0, "prices": {"retail": 129.90, "shop": 109.90, "agent": 89.90}},
    {"name": "西湖龙井茶 250g", "sku_code": "TEA-001", "description": "明前特级龙井茶", "stock": 200, "is_new": 1, "prices": {"retail": 399.00, "shop": 329.00, "agent": 269.00}},
    {"name": "四川花椒 500g", "sku_code": "SPICE-001", "description": "汉源大红袍花椒", "stock": 800, "is_new": 0, "prices": {"retail": 89.00, "shop": 69.00, "agent": 49.00}},
    {"name": "苏式月饼礼盒", "sku_code": "CAKE-001", "description": "传统苏式月饼 8 枚装", "stock": 300, "is_new": 0, "prices": {"retail": 168.00, "shop": 138.00, "agent": 108.00}},
    {"name": "武汉热干面 5 包装", "sku_code": "NOODLE-001", "description": "正宗武汉热干面", "stock": 1500, "is_new": 1, "prices": {"retail": 29.90, "shop": 24.90, "agent": 19.90}},
    {"name": "广东腊肠 500g", "sku_code": "MEAT-001", "description": "广式甜味腊肠", "stock": 600, "is_new": 0, "prices": {"retail": 79.00, "shop": 65.00, "agent": 51.00}},
    {"name": "有机木耳 250g", "sku_code": "FUNGUS-001", "description": "东北有机黑木耳", "stock": 400, "is_new": 0, "prices": {"retail": 68.00, "shop": 55.00, "agent": 42.00}},
    {"name": "红枣 500g", "sku_code": "FRUIT-001", "description": "新疆若羌红枣", "stock": 700, "is_new": 0, "prices": {"retail": 49.00, "shop": 39.00, "agent": 29.00}},
    {"name": "蜂蜜 500g", "sku_code": "HONEY-001", "description": "天然成熟蜂蜜", "stock": 350, "is_new": 1, "prices": {"retail": 88.00, "shop": 72.00, "agent": 56.00}},
]


async def init_regions():
    """初始化区域数据"""
    async with async_session_maker() as session:
        # 检查是否已有数据
        result = await session.execute(select(Region))
        if result.scalars().first():
            print("  ⚠️  区域数据已存在，跳过")
            return

        print("  正在创建区域数据...")
        for region_data in REGIONS_DATA:
            region = Region(**region_data)
            # 生成路径
            if region_data["parent_id"]:
                parent_result = await session.execute(select(Region).where(Region.id == region_data["parent_id"]))
                parent = parent_result.scalar_one()
                region.path = f"{parent.path}/{region_data['name']}"
            else:
                region.path = region_data["name"]
            session.add(region)

        await session.commit()
        print(f"  ✓ 创建 {len(REGIONS_DATA)} 个区域")


async def init_suppliers():
    """初始化供应商数据"""
    async with async_session_maker() as session:
        result = await session.execute(select(Supplier))
        if result.scalars().first():
            print("  ⚠️  供应商数据已存在，跳过")
            return

        print("  正在创建供应商数据...")
        for supplier_data in SUPPLIERS_DATA:
            supplier = Supplier(**supplier_data)
            session.add(supplier)

        await session.commit()
        print(f"  ✓ 创建 {len(SUPPLIERS_DATA)} 个供应商")


async def init_users_and_roles():
    """初始化用户和角色数据"""
    async with async_session_maker() as session:
        # 检查是否已有管理员
        result = await session.execute(select(User).where(User.username == "admin"))
        if not result.scalar_one_or_none():
            print("  正在创建管理员账号...")
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                role_type="admin",
                status=UserStatus.ACTIVE
            )
            session.add(admin_user)
            await session.commit()
            print("  ✓ 创建管理员账号 (admin/admin123)")

        # 创建测试用户
        test_users = [
            {"username": "operator01", "password": "test123", "role_type": "operator"},
            {"username": "agent01", "password": "test123", "role_type": "agent"},
            {"username": "shop01", "password": "test123", "role_type": "shop"},
            {"username": "supplier01", "password": "test123", "role_type": "supplier"},
            {"username": "customer01", "password": "test123", "role_type": "customer"},
        ]

        for user_data in test_users:
            result = await session.execute(select(User).where(User.username == user_data["username"]))
            if not result.scalar_one_or_none():
                user = User(
                    username=user_data["username"],
                    password_hash=get_password_hash(user_data["password"]),
                    role_type=user_data["role_type"],
                    status=UserStatus.ACTIVE
                )
                session.add(user)

        await session.commit()
        print("  ✓ 创建 5 个测试用户")


async def init_shops_and_agents():
    """初始化店铺和区代数据"""
    async with async_session_maker() as session:
        # 获取区域
        result = await session.execute(select(Region).where(Region.level == 3))
        regions = result.scalars().all()

        if not regions:
            print("  ⚠️  没有可用区域，先初始化区域数据")
            return

        # 获取用户
        result = await session.execute(select(User).where(User.role_type.in_(["shop", "agent"])))
        users = result.scalars().all()

        # 创建店铺
        shop_users = [u for u in users if u.role_type == "shop"]
        result = await session.execute(select(Shop))
        if not result.scalars().first() and shop_users:
            print("  正在创建店铺数据...")
            for i, user in enumerate(shop_users[:len(regions)]):
                shop = Shop(
                    user_id=user.id,
                    region_id=regions[i % len(regions)].id,
                    status="active"
                )
                session.add(shop)
            await session.commit()
            print(f"  ✓ 创建 {len(shop_users[:len(regions)])} 个店铺")

        # 创建区代
        agent_users = [u for u in users if u.role_type == "agent"]
        result = await session.execute(select(Agent))
        if not result.scalars().first() and agent_users:
            print("  正在创建区代数据...")
            for i, user in enumerate(agent_users[:len(regions)]):
                agent = Agent(
                    user_id=user.id,
                    region_id=regions[i % len(regions)].id,
                    status="active"
                )
                session.add(agent)
            await session.commit()
            print(f"  ✓ 创建 {len(agent_users[:len(regions)])} 个区代")


async def init_products():
    """初始化产品数据"""
    async with async_session_maker() as session:
        result = await session.execute(select(Product))
        if result.scalars().first():
            print("  ⚠️  产品数据已存在，跳过")
            return

        # 获取供应商
        result = await session.execute(select(Supplier))
        suppliers = result.scalars().all()

        if not suppliers:
            print("  ⚠️  没有可用供应商，先初始化供应商数据")
            return

        print("  正在创建产品数据...")
        for i, product_data in enumerate(PRODUCTS_DATA):
            prices = product_data.pop("prices")
            supplier = suppliers[i % len(suppliers)]

            product = Product(
                name=product_data["name"],
                sku_code=product_data["sku_code"],
                description=product_data["description"],
                stock=product_data["stock"],
                is_new=product_data["is_new"],
                supplier_id=supplier.id,
                cost_price=Decimal(str(prices["agent"]))  # 采购价按区代价
            )
            session.add(product)
            await session.flush()  # 获取 product.id

            # 创建价格层级
            for tier_type, price in prices.items():
                price_tier = PriceTier(
                    product_id=product.id,
                    tier_type=tier_type,
                    price=Decimal(str(price))
                )
                session.add(price_tier)

        await session.commit()
        print(f"  ✓ 创建 {len(PRODUCTS_DATA)} 个产品")


async def init_purchase_orders():
    """初始化采购订单数据"""
    async with async_session_maker() as session:
        # 检查是否已有数据
        result = await session.execute(select(PurchaseOrder))
        if result.scalars().first():
            print("  ⚠️  采购订单数据已存在，跳过")
            return

        # 获取供应商
        result = await session.execute(select(Supplier))
        suppliers = result.scalars().all()

        # 获取产品
        result = await session.execute(select(Product))
        products = result.scalars().all()

        # 获取采购员
        result = await session.execute(select(User).where(User.role_type == "operator"))
        purchasers = result.scalars().all()

        if not all([suppliers, products, purchasers]):
            print("  ⚠️  缺少必要数据，无法创建采购订单")
            return

        print("  正在创建采购订单数据...")

        # 创建 10 个采购订单
        order_count = 10
        statuses = [PurchaseOrderStatus.PENDING, PurchaseOrderStatus.CONFIRMED,
                   PurchaseOrderStatus.COMPLETED, PurchaseOrderStatus.CANCELLED]
        confirm_statuses = [SupplierConfirmStatus.PENDING, SupplierConfirmStatus.CONFIRMED,
                          SupplierConfirmStatus.REJECTED]

        for i in range(order_count):
            supplier = suppliers[i % len(suppliers)]
            purchaser = purchasers[i % len(purchasers)]

            # 生成订单号
            order_no = f"PO{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(4)}"

            # 随机状态
            status = random.choice(statuses)
            confirm_status = random.choice(confirm_statuses)

            order = PurchaseOrder(
                order_no=order_no,
                supplier_id=supplier.id,
                purchaser_id=purchaser.id,
                total_amount=Decimal("0"),
                status=status,
                supplier_confirm_status=confirm_status,
                remark=f"测试订单 {i+1}",
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            session.add(order)
            await session.flush()

            # 创建订单明细（2-5 个商品）
            order_items = random.sample(products, random.randint(2, min(5, len(products))))
            total_amount = Decimal("0")

            for product in order_items:
                quantity = random.randint(10, 100)
                cost_price = product.cost_price or Decimal("10.00")
                subtotal = quantity * cost_price
                total_amount += subtotal

                item = PurchaseOrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    cost_price=cost_price,
                    subtotal=subtotal
                )
                session.add(item)

            # 更新订单总额
            order.total_amount = total_amount
            await session.flush()

        await session.commit()
        print(f"  ✓ 创建 {order_count} 个采购订单")


async def init_customer_orders():
    """初始化客户订单数据"""
    async with async_session_maker() as session:
        # 检查是否已有数据
        result = await session.execute(select(Order))
        if result.scalars().first():
            print("  ⚠️  客户订单数据已存在，跳过")
            return

        # 获取用户
        result = await session.execute(select(User).where(User.role_type == "customer"))
        customers = result.scalars().all()

        # 获取产品
        result = await session.execute(select(Product))
        products = result.scalars().all()

        if not all([customers, products]):
            # 创建测试客户
            if not customers:
                print("  创建测试客户...")
                for i in range(5):
                    customer = User(
                        username=f"customer0{i+2}",
                        password_hash=get_password_hash("test123"),
                        role_type="customer",
                        status=UserStatus.ACTIVE
                    )
                    session.add(customer)
                await session.commit()
                result = await session.execute(select(User).where(User.role_type == "customer"))
                customers = result.scalars().all()

        print("  正在创建客户订单数据...")

        # 创建 20 个客户订单
        order_count = 20
        statuses = [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED,
                   OrderStatus.COMPLETED, OrderStatus.CANCELLED]

        for i in range(order_count):
            customer = customers[i % len(customers)]

            # 生成订单号
            order_no = f"SO{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(4)}"

            # 随机状态
            status = random.choice(statuses)

            order = Order(
                order_no=order_no,
                user_id=customer.id,
                total_amount=Decimal("0"),
                status=status,
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            session.add(order)
            await session.flush()

            # 创建订单明细（1-3 个商品）
            order_items = random.sample(products, random.randint(1, min(3, len(products))))
            total_amount = Decimal("0")

            for product in order_items:
                quantity = random.randint(1, 5)
                # 获取零售价格
                price_result = await session.execute(
                    select(PriceTier).where(
                        PriceTier.product_id == product.id,
                        PriceTier.tier_type == "retail"
                    )
                )
                price_tier = price_result.scalar_one_or_none()
                price = price_tier.price if price_tier else Decimal("50.00")
                subtotal = quantity * price
                total_amount += subtotal

                item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=price,
                    subtotal=subtotal
                )
                session.add(item)

            # 更新订单总额
            order.total_amount = total_amount
            await session.flush()

        await session.commit()
        print(f"  ✓ 创建 {order_count} 个客户订单")


async def main():
    """主函数"""
    print("=" * 50)
    print("  渠道销售管理系统 - 模拟数据初始化")
    print("=" * 50)
    print()

    try:
        # 按依赖顺序初始化
        print("【1/8】初始化区域数据...")
        await init_regions()

        print("\n【2/8】初始化供应商数据...")
        await init_suppliers()

        print("\n【3/8】初始化用户和角色...")
        await init_users_and_roles()

        print("\n【4/8】初始化店铺和区代...")
        await init_shops_and_agents()

        print("\n【5/8】初始化产品数据...")
        await init_products()

        print("\n【6/8】初始化采购订单...")
        await init_purchase_orders()

        print("\n【7/8】初始化客户订单...")
        await init_customer_orders()

        print("\n" + "=" * 50)
        print("  模拟数据初始化完成！")
        print("=" * 50)
        print()
        print("测试账号汇总：")
        print("  - 管理员：admin / admin123")
        print("  - 运营：operator01 / test123")
        print("  - 区代：agent01 / test123")
        print("  - 店铺：shop01 / test123")
        print("  - 供应商：supplier01 / test123")
        print("  - 客户：customer01 / test123")
        print()

    except Exception as e:
        print(f"\n❌ 初始化失败：{e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
