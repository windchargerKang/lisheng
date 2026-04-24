"""
河南省模拟数据初始化脚本
生成以河南省为核心的完整区域、渠道、订单和分润数据
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
from app.models.region import Region
from app.models.shop import Shop
from app.models.agent import Agent
from app.models.product import Product, PriceTier
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.models.profit import ProfitRecord, ProfitStatus
from app.models.supplier import Supplier

# 创建数据库会话
engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ==================== 河南省区域数据 ====================

# 河南省地级市及县级区数据（含拼音用于生成用户名）
HENAN_CITIES = [
    {"name": "郑州市", "pinyin": "zhengzhou", "districts": [
        "中原区", "二七区", "管城回族区", "金水区", "上街区", "惠济区",
        "巩义市", "荥阳市", "新密市", "新郑市", "登封市", "中牟县"
    ]},
    {"name": "开封市", "pinyin": "kaifeng", "districts": [
        "龙亭区", "顺河回族区", "鼓楼区", "禹王台区", "祥符区",
        "杞县", "通许县", "尉氏县", "兰考县"
    ]},
    {"name": "洛阳市", "pinyin": "luoyang", "districts": [
        "老城区", "西工区", "瀍河回族区", "涧西区", "吉利区", "洛龙区",
        "偃师市", "孟津县", "新安县", "栾川县", "嵩县", "汝阳县", "宜阳县", "洛宁县", "伊川县"
    ]},
    {"name": "平顶山市", "pinyin": "pingdingshan", "districts": [
        "新华区", "卫东区", "石龙区", "湛河区",
        "舞钢市", "汝州市", "宝丰县", "叶县", "鲁山县", "郏县"
    ]},
    {"name": "安阳市", "pinyin": "anyang", "districts": [
        "文峰区", "北关区", "殷都区", "龙安区",
        "林州市", "安阳县", "汤阴县", "滑县", "内黄县"
    ]},
    {"name": "鹤壁市", "pinyin": "hebi", "districts": [
        "鹤山区", "山城区", "淇滨区",
        "浚县", "淇县"
    ]},
    {"name": "新乡市", "pinyin": "xinxiang", "districts": [
        "红旗区", "卫滨区", "凤泉区", "牧野区",
        "卫辉市", "辉县市", "新乡县", "获嘉县", "原阳县", "延津县", "封丘县", "长垣县"
    ]},
    {"name": "焦作市", "pinyin": "jiaozuo", "districts": [
        "解放区", "中站区", "马村区", "山阳区",
        "沁阳市", "孟州市", "修武县", "博爱县", "武陟县", "温县"
    ]},
    {"name": "濮阳市", "pinyin": "puyang", "districts": [
        "华龙区",
        "清丰县", "南乐县", "范县", "台前县", "濮阳县"
    ]},
    {"name": "许昌市", "pinyin": "xuchang", "districts": [
        "魏都区", "建安区",
        "禹州市", "长葛市", "鄢陵县", "襄城县"
    ]},
    {"name": "漯河市", "pinyin": "luohe", "districts": [
        "源汇区", "郾城区", "召陵区",
        "舞阳县", "临颍县"
    ]},
    {"name": "三门峡市", "pinyin": "sanmenxia", "districts": [
        "湖滨区", "陕州区",
        "义马市", "灵宝市", "渑池县", "卢氏县"
    ]},
    {"name": "南阳市", "pinyin": "nanyang", "districts": [
        "宛城区", "卧龙区",
        "邓州市", "南召县", "方城县", "西峡县", "镇平县", "内乡县", "淅川县", "社旗县", "唐河县", "新野县", "桐柏县"
    ]},
    {"name": "商丘市", "pinyin": "shangqiu", "districts": [
        "梁园区", "睢阳区",
        "永城市", "民权县", "睢县", "宁陵县", "柘城县", "虞城县", "夏邑县"
    ]},
    {"name": "信阳市", "pinyin": "xinyang", "districts": [
        "浉河区", "平桥区",
        "罗山县", "光山县", "新县", "商城县", "固始县", "潢川县", "淮滨县", "息县"
    ]},
    {"name": "周口市", "pinyin": "zhoukou", "districts": [
        "川汇区",
        "项城市", "扶沟县", "西华县", "商水县", "沈丘县", "郸城县", "淮阳县", "太康县", "鹿邑县"
    ]},
    {"name": "驻马店市", "pinyin": "zhumadian", "districts": [
        "驿城区",
        "西平县", "上蔡县", "平舆县", "正阳县", "确山县", "泌阳县", "汝南县", "遂平县", "新蔡县"
    ]},
    {"name": "济源市", "pinyin": "jiyuan", "districts": [
        "济源市"
    ]},
]


# ==================== 河南省特色商品数据 ====================

# 河南省特色商品数据（3 个核心产品）
# 价格结构：{"retail": 零售价，"shop": 店铺价，"agent": 区代价}
HENAN_PRODUCTS = [
    # 核心产品 - 药包和喷剂
    {"name": "药包", "category": "核心产品", "sku": "HN-CORE-001",
     "prices": {"retail": 90.00, "shop": 60.00, "agent": 50.00},
     "description": "力生服务核心产品，传统配方"},
    {"name": "喷剂 1", "category": "核心产品", "sku": "HN-CORE-002",
     "prices": {"retail": 180.00, "shop": 130.00, "agent": 120.00},
     "description": "力生服务核心产品，外用喷剂"},
    {"name": "喷剂 2", "category": "核心产品", "sku": "HN-CORE-003",
     "prices": {"retail": 180.00, "shop": 130.00, "agent": 120.00},
     "description": "力生服务核心产品，外用喷剂升级版"},
]


async def init_henan_products():
    """初始化河南省特色商品数据"""
    async with async_session_maker() as session:
        # 检查是否已有商品
        result = await session.execute(select(Product).where(Product.sku_code.like("HN-%")))
        if result.scalars().first():
            print("  ⚠️  河南省特色商品数据已存在，跳过")
            return

        # 获取或创建河南省供应商
        result = await session.execute(select(Supplier).where(Supplier.name.like("河南%")))
        supplier = result.scalar_one_or_none()

        if not supplier:
            # 创建河南省供应商
            supplier = Supplier(
                name="河南特产供应链有限公司",
                credit_code="91410100MA1234567X",
                contact_name="李河南",
                contact_phone="13900139000",
                address="河南省郑州市郑东新区商务内环路 1 号",
                bank_name="中原银行郑州分行",
                bank_account="6217001234567890000",
                settlement_type="cash"
            )
            session.add(supplier)
            await session.flush()

        print("  正在创建河南省特色商品...")

        for product_data in HENAN_PRODUCTS:
            # 检查 SKU 是否已存在
            result = await session.execute(select(Product).where(Product.sku_code == product_data["sku"]))
            if result.scalar_one_or_none():
                continue

            prices = product_data["prices"]
            retail_price = Decimal(str(prices["retail"]))
            cost_price = retail_price * Decimal(str(0.55))  # 成本价约为零售价的 55%

            product = Product(
                name=product_data["name"],
                sku_code=product_data["sku"],
                status="active",
                description=product_data["description"],
                stock=random.randint(100, 500),
                is_new=random.choice([0, 0, 0, 1]),  # 30% 概率为新品
                supplier_id=supplier.id,
                cost_price=cost_price.quantize(Decimal("0.01"))
            )
            session.add(product)
            await session.flush()

            # 创建三级价格（使用指定价格）
            for tier_type, price in prices.items():
                price_tier = PriceTier(
                    product_id=product.id,
                    tier_type=tier_type,
                    price=Decimal(str(price)).quantize(Decimal("0.01"))
                )
                session.add(price_tier)

        await session.commit()
        print(f"  ✓ 创建 {len(HENAN_PRODUCTS)} 个河南省特色商品")


async def init_henan_regions():
    """初始化河南省区域数据"""
    async with async_session_maker() as session:
        # 检查河南省是否已存在
        result = await session.execute(select(Region).where(Region.name == "河南省"))
        if result.scalar_one_or_none():
            print("  ⚠️  河南省区域数据已存在，跳过")
            return {}

        print("  正在创建河南省区域数据...")

        # 创建省级
        henan_province = Region(name="河南省", level=1, parent_id=None, path="河南省")
        session.add(henan_province)
        await session.flush()

        region_map = {"河南省": henan_province.id}

        # 创建地级市和县级区
        for city_data in HENAN_CITIES:
            city_name = city_data["name"]
            # 创建市级
            city = Region(name=city_name, level=2, parent_id=henan_province.id, path=f"河南省/{city_name}")
            session.add(city)
            await session.flush()
            region_map[city_name] = city.id

            # 创建县级区
            for district_name in city_data["districts"]:
                district = Region(name=district_name, level=3, parent_id=city.id, path=f"河南省/{city_name}/{district_name}")
                session.add(district)
                region_map[district_name] = district.id

        await session.commit()
        total_regions = 1 + len(HENAN_CITIES) + sum(len(c["districts"]) for c in HENAN_CITIES)
        print(f"  ✓ 创建 {total_regions} 个区域 (1 省 + {len(HENAN_CITIES)} 市 + {sum(len(c['districts']) for c in HENAN_CITIES)} 县区)")

        return region_map


async def init_henan_users(region_map):
    """初始化河南省用户数据"""
    async with async_session_maker() as session:
        # 获取所有县级区
        result = await session.execute(select(Region).where(Region.level == 3))
        county_regions = result.scalars().all()

        if not county_regions:
            print("  ⚠️  没有可用的县级区域")
            return

        # ==================== 创建区代（18 个） ====================
        print("  正在创建区代用户...")
        agent_count = 0
        for city_data in HENAN_CITIES:
            city_name = city_data["name"]
            city_pinyin = city_data["pinyin"]
            city_id = region_map.get(city_name)
            if not city_id:
                continue

            username = f"agent_{city_pinyin}"

            # 检查是否已存在
            result = await session.execute(select(User).where(User.username == username))
            if result.scalar_one_or_none():
                continue

            user = User(
                username=username,
                password_hash=get_password_hash("test123"),
                role_type="agent",
                status=UserStatus.ACTIVE
            )
            session.add(user)
            await session.flush()

            # 创建区代关联
            agent = Agent(user_id=user.id, region_id=city_id, status="active")
            session.add(agent)
            agent_count += 1

        await session.commit()
        print(f"  ✓ 创建 {agent_count} 个区代用户")

        # ==================== 创建店铺（50 个） ====================
        print("  正在创建店铺用户...")
        shop_count = 0
        shop_distribution = {
            "郑州市": 8, "洛阳市": 6, "南阳市": 4, "商丘市": 4, "周口市": 4,
            "信阳市": 4, "驻马店市": 4, "开封市": 3, "安阳市": 3, "新乡市": 3,
            "许昌市": 3, "平顶山市": 2, "焦作市": 2, "漯河市": 2, "三门峡市": 2,
            "鹤壁市": 1, "濮阳市": 1, "济源市": 1
        }

        for city_data in HENAN_CITIES:
            city_name = city_data["name"]
            city_pinyin = city_data["pinyin"]
            city_id = region_map.get(city_name)
            if not city_id:
                continue

            count = shop_distribution.get(city_name, 2)

            for i in range(count):
                username = f"shop_{city_pinyin}_{str(i+1).zfill(2)}"

                result = await session.execute(select(User).where(User.username == username))
                if result.scalar_one_or_none():
                    continue

                user = User(
                    username=username,
                    password_hash=get_password_hash("test123"),
                    role_type="shop",
                    status=UserStatus.ACTIVE
                )
                session.add(user)
                await session.flush()

                # 创建店铺关联（分配到县级区）
                district_index = i % len(county_regions)
                shop = Shop(user_id=user.id, region_id=county_regions[district_index].id, status="active")
                session.add(shop)
                shop_count += 1

        await session.commit()
        print(f"  ✓ 创建 {shop_count} 个店铺用户")

        # ==================== 创建客户（100 个） ====================
        print("  正在创建客户用户...")
        customer_count = 0

        for i in range(100):
            username = f"customer_hn_{str(i+1).zfill(3)}"

            result = await session.execute(select(User).where(User.username == username))
            if result.scalar_one_or_none():
                continue

            user = User(
                username=username,
                password_hash=get_password_hash("test123"),
                role_type="customer",
                status=UserStatus.ACTIVE
            )
            session.add(user)
            customer_count += 1

        await session.commit()
        print(f"  ✓ 创建 {customer_count} 个客户用户")

        return {"agents": agent_count, "shops": shop_count, "customers": customer_count}


async def init_henan_orders():
    """初始化河南省订单数据"""
    async with async_session_maker() as session:
        # 检查是否已有订单
        result = await session.execute(select(Order).where(Order.order_no.like("SO%")))
        if result.scalars().first():
            print("  ⚠️  客户订单数据已存在，跳过")
            return

        # 获取客户
        result = await session.execute(select(User).where(User.role_type == "customer"))
        customers = result.scalars().all()

        # 获取产品
        result = await session.execute(select(Product))
        products = result.scalars().all()

        if not customers or not products:
            print("  ⚠️  缺少客户或产品数据")
            return

        # ==================== 创建客户订单（30 笔） ====================
        print("  正在创建客户订单...")
        order_count = 30
        statuses = [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED,
                   OrderStatus.COMPLETED, OrderStatus.CANCELLED]

        for i in range(order_count):
            customer = customers[i % len(customers)]
            order_no = f"SO{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(4)}"
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

            # 创建订单明细
            order_items = random.sample(products, random.randint(1, min(3, len(products))))
            total_amount = Decimal("0")

            for product in order_items:
                quantity = random.randint(1, 5)
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

            order.total_amount = total_amount
            await session.flush()

        await session.commit()
        print(f"  ✓ 创建 {order_count} 笔客户订单")


async def init_henan_profits():
    """初始化河南省分润数据"""
    async with async_session_maker() as session:
        # 获取用户
        result = await session.execute(select(User))
        all_users = result.scalars().all()

        customers = [u for u in all_users if u.role_type == "customer"]
        shops = [u for u in all_users if u.role_type == "shop"]
        agents = [u for u in all_users if u.role_type == "agent"]

        if not all_users:
            print("  ⚠️  缺少用户数据")
            return

        print("  正在创建分润记录...")

        # 客户分享提成（10 条）
        customer_profit_count = 0
        if customers:
            for i in range(10):
                customer = random.choice(customers)
                profit = ProfitRecord(
                    user_id=customer.id,
                    order_id=random.randint(1, 30),
                    amount=Decimal(str(random.uniform(5, 50))),
                    status=ProfitStatus.PENDING,
                    remark=f"客户分享提成 {i+1}"
                )
                session.add(profit)
                customer_profit_count += 1

        # 店铺销售利润（20 条）
        shop_profit_count = 0
        if shops:
            for i in range(20):
                shop = random.choice(shops)
                profit = ProfitRecord(
                    user_id=shop.id,
                    order_id=random.randint(1, 30),
                    amount=Decimal(str(random.uniform(20, 200))),
                    status=ProfitStatus.PENDING,
                    remark=f"店铺销售利润 {i+1}"
                )
                session.add(profit)
                shop_profit_count += 1

        # 区代区域补贴（15 条）
        agent_profit_count = 0
        if agents:
            for i in range(15):
                agent = random.choice(agents)
                profit = ProfitRecord(
                    user_id=agent.id,
                    order_id=random.randint(1, 30),
                    amount=Decimal(str(random.uniform(30, 300))),
                    status=ProfitStatus.PENDING,
                    remark=f"区代区域补贴 {i+1}"
                )
                session.add(profit)
                agent_profit_count += 1

        # 主播提成（5 条）
        streamer_profit_count = 5
        for i in range(streamer_profit_count):
            user = random.choice(customers) if customers else None
            if user:
                profit = ProfitRecord(
                    user_id=user.id,
                    order_id=random.randint(1, 30),
                    amount=Decimal(str(random.uniform(50, 500))),
                    status=ProfitStatus.PENDING,
                    remark=f"主播提成 {i+1}"
                )
                session.add(profit)

        await session.commit()
        total_profits = customer_profit_count + shop_profit_count + agent_profit_count + streamer_profit_count
        print(f"  ✓ 创建 {total_profits} 条分润记录 (客户:{customer_profit_count} 店铺:{shop_profit_count} 区代:{agent_profit_count} 主播:{streamer_profit_count})")


async def main():
    """主函数"""
    print("=" * 50)
    print("  河南省模拟数据初始化")
    print("=" * 50)
    print()

    try:
        print("【1/5】初始化河南省区域数据...")
        region_map = await init_henan_regions()

        print("\n【2/5】初始化河南省商品数据...")
        await init_henan_products()

        print("\n【3/5】初始化河南省用户数据...")
        user_stats = await init_henan_users(region_map)

        print("\n【4/5】初始化河南省订单数据...")
        await init_henan_orders()

        print("\n【5/5】初始化河南省分润数据...")
        await init_henan_profits()

        print("\n" + "=" * 50)
        print("  河南省模拟数据初始化完成！")
        print("=" * 50)
        print()
        print("数据汇总：")
        print(f"  - 区域：1 个省 + {len(HENAN_CITIES)} 个市 + {sum(len(c['districts']) for c in HENAN_CITIES)} 个县区")
        print(f"  - 特色商品：{len(HENAN_PRODUCTS)} 个")
        if user_stats:
            print(f"  - 区代：{user_stats.get('agents', 0)} 个")
            print(f"  - 店铺：{user_stats.get('shops', 0)} 个")
            print(f"  - 客户：{user_stats.get('customers', 0)} 个")
        print(f"  - 客户订单：30 笔")
        print(f"  - 分润记录：50 条")
        print()
        print("测试账号示例：")
        print(f"  - 区代：agent_zhengzhou / test123")
        print(f"  - 店铺：shop_zhengzhou_01 / test123")
        print(f"  - 客户：customer_hn_001 / test123")
        print()

    except Exception as e:
        print(f"\n❌ 初始化失败：{e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
