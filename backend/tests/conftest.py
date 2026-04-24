"""
测试配置和共享 fixture
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from app.main import app
from app.core.database import get_db, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role


# 测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_channel_sales.db"


@pytest.fixture
async def db_session():
    """创建测试数据库会话"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session):
    """创建测试客户端"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_user(db_session):
    """创建测试管理员用户"""
    # 获取 admin 角色
    from app.models.role import Role
    result = await db_session.execute(select(Role).where(Role.code == "admin"))
    admin_role = result.scalar_one_or_none()

    if not admin_role:
        admin_role = Role(code="admin", name="管理员", description="管理员角色")
        db_session.add(admin_role)
        await db_session.flush()

    user = User(
        username="testadmin",
        password_hash=get_password_hash("test123"),
        role_id=admin_role.id
    )
    db_session.add(user)
    await db_session.commit()
    return user
