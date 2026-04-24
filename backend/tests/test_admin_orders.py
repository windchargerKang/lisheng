"""
运营管理端订单 API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.product import Product, PriceTier
from app.models.cart import CartItem


@pytest.fixture
async def test_admin_user(db_session: AsyncSession):
    """创建测试管理员用户"""
    user = User(username="admin", password_hash="hashed", role_type="admin")
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def test_operator_user(db_session: AsyncSession):
    """创建测试运营用户"""
    user = User(username="operator", password_hash="hashed", role_type="operator")
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def test_customer_user(db_session: AsyncSession):
    """创建测试普通用户"""
    user = User(username="customer", password_hash="hashed", role_type="customer")
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def test_order(db_session: AsyncSession, test_customer_user: User):
    """创建测试订单（待发货状态）"""
    order = Order(
        order_no="ORD_TEST_001",
        user_id=test_customer_user.id,
        total_amount=198.0,
        status=OrderStatus.CONFIRMED,  # 待发货状态
        receiver_name="测试用户",
        receiver_phone="13800138000",
        receiver_address="测试地址",
    )
    db_session.add(order)
    await db_session.commit()
    return order


@pytest.fixture
async def test_shipped_order(db_session: AsyncSession, test_customer_user: User):
    """创建测试订单（已发货状态）"""
    order = Order(
        order_no="ORD_TEST_002",
        user_id=test_customer_user.id,
        total_amount=298.0,
        status=OrderStatus.SHIPPED,  # 已发货状态
        receiver_name="测试用户",
        receiver_phone="13800138000",
        receiver_address="测试地址",
        courier_company="顺丰速运",
        courier_no="SF1234567890",
    )
    db_session.add(order)
    await db_session.commit()
    return order


@pytest.fixture
async def admin_auth_headers(test_admin_user: User, client: AsyncClient):
    """获取管理员认证头"""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(test_admin_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def operator_auth_headers(test_operator_user: User, client: AsyncClient):
    """获取运营员认证头"""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(test_operator_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def customer_auth_headers(test_customer_user: User, client: AsyncClient):
    """获取普通用户认证头"""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(test_customer_user.id)})
    return {"Authorization": f"Bearer {token}"}


class TestAdminOrderList:
    """管理端订单列表测试"""

    @pytest.mark.asyncio
    async def test_admin_list_orders(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_order: Order,
    ):
        """测试管理员查看订单列表"""
        response = await client.get(
            "/api/v1/admin/orders",
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_operator_list_orders(
        self,
        client: AsyncClient,
        operator_auth_headers: dict,
        test_order: Order,
    ):
        """测试运营员查看订单列表"""
        response = await client.get(
            "/api/v1/admin/orders",
            headers=operator_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_customer_cannot_list_orders(
        self,
        client: AsyncClient,
        customer_auth_headers: dict,
        test_order: Order,
    ):
        """测试普通用户无法访问管理端订单列表"""
        response = await client.get(
            "/api/v1/admin/orders",
            headers=customer_auth_headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_orders_filter_by_status(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_order: Order,
        test_shipped_order: Order,
    ):
        """测试按订单状态筛选"""
        # 筛选待发货订单
        response = await client.get(
            "/api/v1/admin/orders?status=confirmed",
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # 应该只返回 confirmed 状态的订单
        for item in data["items"]:
            assert item["status"] == "confirmed"


class TestAdminOrderDetail:
    """管理端订单详情测试"""

    @pytest.mark.asyncio
    async def test_admin_get_order_detail(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_order: Order,
    ):
        """测试管理员查看订单详情"""
        response = await client.get(
            f"/api/v1/admin/orders/{test_order.id}",
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_order.id
        assert data["order_no"] == test_order.order_no

    @pytest.mark.asyncio
    async def test_customer_cannot_view_admin_order_detail(
        self,
        client: AsyncClient,
        customer_auth_headers: dict,
        test_order: Order,
    ):
        """测试普通用户无法访问管理端订单详情"""
        response = await client.get(
            f"/api/v1/admin/orders/{test_order.id}",
            headers=customer_auth_headers
        )
        assert response.status_code == 403


class TestAdminShipOrder:
    """管理端发货操作测试"""

    @pytest.mark.asyncio
    async def test_admin_ship_order(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_order: Order,
    ):
        """测试管理员执行发货操作"""
        response = await client.post(
            f"/api/v1/admin/orders/{test_order.id}/ship",
            headers=admin_auth_headers,
            json={
                "courier_company": "顺丰速运",
                "courier_no": "SF1234567890",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "shipped"
        assert data["courier_company"] == "顺丰速运"
        assert data["courier_no"] == "SF1234567890"

    @pytest.mark.asyncio
    async def test_operator_ship_order(
        self,
        client: AsyncClient,
        operator_auth_headers: dict,
        test_order: Order,
    ):
        """测试运营员执行发货操作"""
        response = await client.post(
            f"/api/v1/admin/orders/{test_order.id}/ship",
            headers=operator_auth_headers,
            json={
                "courier_company": "中通快递",
                "courier_no": "ZT1234567890",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "shipped"

    @pytest.mark.asyncio
    async def test_customer_cannot_ship_order(
        self,
        client: AsyncClient,
        customer_auth_headers: dict,
        test_order: Order,
    ):
        """测试普通用户无法执行发货操作"""
        response = await client.post(
            f"/api/v1/admin/orders/{test_order.id}/ship",
            headers=customer_auth_headers,
            json={
                "courier_company": "测试快递",
                "courier_no": "TEST123",
            }
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_ship_order_not_confirmed_status(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_shipped_order: Order,
    ):
        """测试不能对已发货订单重复发货"""
        response = await client.post(
            f"/api/v1/admin/orders/{test_shipped_order.id}/ship",
            headers=admin_auth_headers,
            json={
                "courier_company": "顺丰速运",
                "courier_no": "SF1234567890",
            }
        )
        assert response.status_code == 400
        assert "只有待发货订单" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_ship_order_missing_fields(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_order: Order,
    ):
        """测试发货操作缺少必填字段"""
        # 缺少 courier_company
        response = await client.post(
            f"/api/v1/admin/orders/{test_order.id}/ship",
            headers=admin_auth_headers,
            json={
                "courier_no": "SF1234567890",
            }
        )
        assert response.status_code == 422

        # 缺少 courier_no
        response = await client.post(
            f"/api/v1/admin/orders/{test_order.id}/ship",
            headers=admin_auth_headers,
            json={
                "courier_company": "顺丰速运",
            }
        )
        assert response.status_code == 422
