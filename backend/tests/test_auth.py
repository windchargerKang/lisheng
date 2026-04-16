"""
认证模块测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.main import app
from app.core.database import get_db, Base
from app.core.security import get_password_hash
from app.models.user import User


# 测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_channel_sales.db"


@pytest.fixture
async def db_session():
    """创建测试数据库会话"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session):
    """创建测试客户端"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_user(db_session):
    """创建测试管理员用户"""
    user = User(
        username="testadmin",
        password_hash=get_password_hash("test123"),
        role_type="admin"
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.mark.asyncio
async def test_login_success(client, admin_user):
    """测试登录成功"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["username"] == "testadmin"


@pytest.mark.asyncio
async def test_login_wrong_password(client, admin_user):
    """测试密码错误"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_user_not_found(client):
    """测试用户不存在"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "nonexistent",
        "password": "test123"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile(client, admin_user):
    """测试获取用户信息"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 获取用户信息
    response = await client.get(
        "/api/v1/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testadmin"
    assert data["role_type"] == "admin"


@pytest.mark.asyncio
async def test_get_profile_unauthorized(client):
    """测试未认证访问用户信息"""
    response = await client.get("/api/v1/auth/profile")
    assert response.status_code == 401
