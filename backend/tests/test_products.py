"""
产品管理 API 测试 - 包含图片和详情功能
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.product import Product, PriceTier
from app.core.security import get_password_hash


@pytest.fixture
async def auth_headers(client: AsyncClient, admin_user: User):
    """获取认证头"""
    # 登录路由在 /auth/login (见 app/api/v1/api.py)
    response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    data = response.json()
    token = data.get("token") or data.get("access_token")
    if not token:
        # 如果登录失败，使用 create_access_token 直接生成 token
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_product_with_images(db_session: AsyncSession):
    """创建带图片的产品"""
    product = Product(
        name="测试产品",
        sku_code="TEST_IMG_001",
        image_url="https://example.com/image1.jpg",
        images=["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
        detail="<p>产品详情描述</p><p>规格：100g</p>",
        status="active"
    )
    db_session.add(product)
    await db_session.commit()

    # 创建价格层级
    price = PriceTier(product_id=product.id, tier_type="retail", price=99.0)
    db_session.add(price)
    await db_session.commit()

    return product


class TestProductImages:
    """产品图片功能测试"""

    @pytest.mark.asyncio
    async def test_create_product_with_images(self, client: AsyncClient, auth_headers: dict):
        """测试创建带图片的产品"""
        response = await client.post("/api/v1/products", json={
            "name": "新产品",
            "sku_code": "NEW001",
            "image_url": "https://example.com/main.jpg",
            "images": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
            "detail": "<p>产品详情</p>",
            "prices": [{"tier_type": "retail", "price": 99.9}]
        }, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新产品"
        assert data["sku_code"] == "NEW001"

    @pytest.mark.asyncio
    async def test_get_product_list_with_images(self, client: AsyncClient, auth_headers: dict, test_product_with_images: Product):
        """测试获取产品列表包含图片字段"""
        response = await client.get("/api/v1/products", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1

        # 验证图片字段存在
        item = data["items"][0]
        assert "image_url" in item
        assert "images" in item
        assert item["image_url"] == "https://example.com/image1.jpg"
        assert item["images"] == ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]

    @pytest.mark.asyncio
    async def test_get_product_detail_with_images(self, client: AsyncClient, auth_headers: dict, test_product_with_images: Product):
        """测试获取产品详情包含图片和详情字段"""
        response = await client.get(f"/api/v1/products/{test_product_with_images.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # 验证新增字段
        assert data["image_url"] == "https://example.com/image1.jpg"
        assert data["images"] == ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
        assert data["detail"] == "<p>产品详情描述</p><p>规格：100g</p>"

    @pytest.mark.asyncio
    async def test_update_product_images(self, client: AsyncClient, auth_headers: dict, test_product_with_images: Product):
        """测试更新产品图片"""
        response = await client.put(f"/api/v1/products/{test_product_with_images.id}", json={
            "image_url": "https://example.com/new_main.jpg",
            "images": ["https://example.com/new1.jpg", "https://example.com/new2.jpg", "https://example.com/new3.jpg"],
            "detail": "<p>更新后的详情</p>"
        }, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product_with_images.id

        # 验证更新后的值
        get_response = await client.get(f"/api/v1/products/{test_product_with_images.id}", headers=auth_headers)
        updated = get_response.json()
        assert updated["image_url"] == "https://example.com/new_main.jpg"
        assert updated["images"] == ["https://example.com/new1.jpg", "https://example.com/new2.jpg", "https://example.com/new3.jpg"]
        assert updated["detail"] == "<p>更新后的详情</p>"

    @pytest.mark.asyncio
    async def test_product_images_null_handling(self, client: AsyncClient, auth_headers: dict):
        """测试图片字段为空时的处理"""
        # 创建不带图片的产品
        response = await client.post("/api/v1/products", json={
            "name": "无图产品",
            "sku_code": "NO_IMG_001",
            "prices": [{"tier_type": "retail", "price": 50.0}]
        }, headers=auth_headers)

        assert response.status_code == 200

        # 验证 API 返回时 images 应为空数组而非 null
        product_id = response.json()["id"]
        get_response = await client.get(f"/api/v1/products/{product_id}", headers=auth_headers)
        data = get_response.json()
        assert data["image_url"] is None
        assert data["images"] == []

    @pytest.mark.asyncio
    async def test_xss_protection_in_detail(self, client: AsyncClient, auth_headers: dict):
        """测试 XSS 防护 - 危险 HTML 标签被过滤"""
        # 尝试注入恶意脚本
        malicious_detail = '<p>正常内容</p><script>alert("XSS")</script><p>更多内容</p>'

        response = await client.post("/api/v1/products", json={
            "name": "测试 XSS 防护",
            "sku_code": "XSS_TEST_001",
            "detail": malicious_detail,
            "prices": [{"tier_type": "retail", "price": 10.0}]
        }, headers=auth_headers)

        assert response.status_code == 200

        # 验证 script 标签被过滤
        product_id = response.json()["id"]
        get_response = await client.get(f"/api/v1/products/{product_id}", headers=auth_headers)
        data = get_response.json()

        # 危险标签应该被移除
        assert "<script>" not in data["detail"]
        assert "正常内容" in data["detail"]
