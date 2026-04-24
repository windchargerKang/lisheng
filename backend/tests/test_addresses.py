"""
用户地址管理 API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.address import UserAddress


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """创建测试用户"""
    user = User(username="testuser", password_hash="hashed", role_type="customer")
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def test_user2(db_session: AsyncSession):
    """创建另一个测试用户（用于权限测试）"""
    user = User(username="testuser2", password_hash="hashed", role_type="customer")
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def test_address(db_session: AsyncSession, test_user: User):
    """创建测试地址"""
    address = UserAddress(
        user_id=test_user.id,
        receiver_name="测试用户",
        receiver_phone="13800138000",
        receiver_address="北京市朝阳区测试路 1 号",
        province="北京市",
        city="北京市",
        district="朝阳区",
        detail_address="测试路 1 号",
        is_default=True,
    )
    db_session.add(address)
    await db_session.commit()
    return address


@pytest.fixture
async def auth_headers(test_user: User, client: AsyncClient):
    """获取认证头"""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_headers_user2(test_user2: User, client: AsyncClient):
    """获取用户 2 的认证头"""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(test_user2.id)})
    return {"Authorization": f"Bearer {token}"}


class TestAddressCreation:
    """地址创建测试"""

    @pytest.mark.asyncio
    async def test_create_address_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """测试创建地址成功"""
        response = await client.post(
            "/api/v1/addresses",
            headers=auth_headers,
            json={
                "receiver_name": "张三",
                "receiver_phone": "13800138000",
                "receiver_address": "北京市朝阳区测试路 1 号",
                "is_default": False,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["message"] == "地址添加成功"

    @pytest.mark.asyncio
    async def test_create_default_address(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """测试创建默认地址（应取消其他默认）"""
        # 先创建第一个默认地址
        response1 = await client.post(
            "/api/v1/addresses",
            headers=auth_headers,
            json={
                "receiver_name": "地址 1",
                "receiver_phone": "13800138000",
                "receiver_address": "地址 1",
                "is_default": True,
            }
        )
        assert response1.status_code == 200
        addr1_id = response1.json()["id"]

        # 创建第二个默认地址
        response2 = await client.post(
            "/api/v1/addresses",
            headers=auth_headers,
            json={
                "receiver_name": "李四",
                "receiver_phone": "13900139000",
                "receiver_address": "上海市浦东新区测试路 2 号",
                "is_default": True,
            }
        )
        assert response2.status_code == 200

        # 验证只有一个默认地址
        list_response = await client.get("/api/v1/addresses", headers=auth_headers)
        addresses = list_response.json()["items"]
        default_addrs = [a for a in addresses if a["is_default"]]
        assert len(default_addrs) == 1
        assert default_addrs[0]["receiver_name"] == "李四"

        # 验证第一个地址不再是默认
        addr1 = next((a for a in addresses if a["id"] == addr1_id), None)
        assert addr1 is not None
        assert addr1["is_default"] == False

    @pytest.mark.asyncio
    async def test_create_address_unauthorized(
        self,
        client: AsyncClient,
    ):
        """测试未授权访问"""
        response = await client.post(
            "/api/v1/addresses",
            json={
                "receiver_name": "张三",
                "receiver_phone": "13800138000",
                "receiver_address": "北京市朝阳区测试路 1 号",
            }
        )
        assert response.status_code == 401


class TestAddressList:
    """地址列表测试"""

    @pytest.mark.asyncio
    async def test_list_addresses(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_address: UserAddress,
    ):
        """测试获取地址列表"""
        response = await client.get("/api/v1/addresses", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_addresses_isolation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        auth_headers_user2: dict,
        test_address: UserAddress,
    ):
        """测试地址列表用户隔离"""
        # 用户 1 能看到自己的地址
        response1 = await client.get("/api/v1/addresses", headers=auth_headers)
        addresses1 = response1.json()["items"]
        assert len(addresses1) >= 1

        # 用户 2 看不到用户 1 的地址
        response2 = await client.get("/api/v1/addresses", headers=auth_headers_user2)
        addresses2 = response2.json()["items"]
        assert len(addresses2) == 0


class TestAddressGet:
    """地址详情测试"""

    @pytest.mark.asyncio
    async def test_get_address_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_address: UserAddress,
    ):
        """测试获取地址详情"""
        response = await client.get(
            f"/api/v1/addresses/{test_address.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_address.id
        assert data["receiver_name"] == test_address.receiver_name

    @pytest.mark.asyncio
    async def test_get_address_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """测试获取不存在的地址"""
        response = await client.get(
            "/api/v1/addresses/99999",
            headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_address_other_user(
        self,
        client: AsyncClient,
        auth_headers_user2: dict,
        test_address: UserAddress,
    ):
        """测试无法获取其他用户的地址"""
        response = await client.get(
            f"/api/v1/addresses/{test_address.id}",
            headers=auth_headers_user2
        )
        assert response.status_code == 404


class TestAddressUpdate:
    """地址更新测试"""

    @pytest.mark.asyncio
    async def test_update_address_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_address: UserAddress,
    ):
        """测试更新地址成功"""
        response = await client.put(
            f"/api/v1/addresses/{test_address.id}",
            headers=auth_headers,
            json={
                "receiver_name": "更新后的姓名",
            }
        )
        assert response.status_code == 200

        # 验证更新后的数据
        get_response = await client.get(
            f"/api/v1/addresses/{test_address.id}",
            headers=auth_headers
        )
        data = get_response.json()
        assert data["receiver_name"] == "更新后的姓名"

    @pytest.mark.asyncio
    async def test_update_set_default(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_address: UserAddress,
    ):
        """测试设置为默认地址"""
        # 先创建另一个地址
        await client.post(
            "/api/v1/addresses",
            headers=auth_headers,
            json={
                "receiver_name": "另一个地址",
                "receiver_phone": "13900139000",
                "receiver_address": "另一个地址",
                "is_default": False,
            }
        )

        # 设置原地址为默认
        response = await client.put(
            f"/api/v1/addresses/{test_address.id}",
            headers=auth_headers,
            json={"is_default": True}
        )
        assert response.status_code == 200

        # 验证只有一个默认地址
        list_response = await client.get("/api/v1/addresses", headers=auth_headers)
        addresses = list_response.json()["items"]
        default_addrs = [a for a in addresses if a["is_default"]]
        assert len(default_addrs) == 1
        assert default_addrs[0]["id"] == test_address.id

    @pytest.mark.asyncio
    async def test_update_other_user_address(
        self,
        client: AsyncClient,
        auth_headers_user2: dict,
        test_address: UserAddress,
    ):
        """测试无法更新其他用户的地址"""
        response = await client.put(
            f"/api/v1/addresses/{test_address.id}",
            headers=auth_headers_user2,
            json={"receiver_name": "非法更新"}
        )
        assert response.status_code == 404


class TestAddressDelete:
    """地址删除测试"""

    @pytest.mark.asyncio
    async def test_delete_address_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """测试软删除地址"""
        # 先创建地址
        create_response = await client.post(
            "/api/v1/addresses",
            headers=auth_headers,
            json={
                "receiver_name": "待删除地址",
                "receiver_phone": "13800138000",
                "receiver_address": "待删除地址",
            }
        )
        address_id = create_response.json()["id"]

        # 删除地址
        delete_response = await client.delete(
            f"/api/v1/addresses/{address_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200

        # 验证地址不在列表中
        list_response = await client.get("/api/v1/addresses", headers=auth_headers)
        addresses = list_response.json()["items"]
        deleted_addr = next((a for a in addresses if a["id"] == address_id), None)
        assert deleted_addr is None

    @pytest.mark.asyncio
    async def test_delete_other_user_address(
        self,
        client: AsyncClient,
        auth_headers_user2: dict,
        test_address: UserAddress,
    ):
        """测试无法删除其他用户的地址"""
        response = await client.delete(
            f"/api/v1/addresses/{test_address.id}",
            headers=auth_headers_user2
        )
        assert response.status_code == 404


class TestSetDefaultAddress:
    """设置默认地址测试"""

    @pytest.mark.asyncio
    async def test_set_default_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_address: UserAddress,
    ):
        """测试设置默认地址"""
        # 先创建另一个地址并设为默认
        create_response = await client.post(
            "/api/v1/addresses",
            headers=auth_headers,
            json={
                "receiver_name": "另一个地址",
                "receiver_phone": "13900139000",
                "receiver_address": "另一个地址",
                "is_default": True,
            }
        )
        new_address_id = create_response.json()["id"]

        # 设置原地址为默认
        response = await client.post(
            f"/api/v1/addresses/{test_address.id}/default",
            headers=auth_headers
        )
        assert response.status_code == 200

        # 验证只有一个默认地址
        list_response = await client.get("/api/v1/addresses", headers=auth_headers)
        addresses = list_response.json()["items"]
        default_addrs = [a for a in addresses if a["is_default"]]
        assert len(default_addrs) == 1
        assert default_addrs[0]["id"] == test_address.id

    @pytest.mark.asyncio
    async def test_set_default_other_user(
        self,
        client: AsyncClient,
        auth_headers_user2: dict,
        test_address: UserAddress,
    ):
        """测试无法设置其他用户的地址为默认"""
        response = await client.post(
            f"/api/v1/addresses/{test_address.id}/default",
            headers=auth_headers_user2
        )
        assert response.status_code == 404
