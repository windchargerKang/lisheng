"""
操作日志模块测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operation_log import OperationLog
from app.models.user import User
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_list_operation_logs(client, admin_user, db_session):
    """测试获取操作日志列表"""
    # 先登录获取 token（会创建一条登录日志）
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    response = await client.get(
        "/api/v1/operation-logs",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1  # 至少有一条登录日志


@pytest.mark.asyncio
async def test_operation_logs_filter_by_user(client, admin_user, db_session):
    """测试按用户筛选操作日志"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 按用户 ID 筛选
    response = await client.get(
        f"/api/v1/operation-logs?user_id={admin_user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    # 所有日志都应该是该用户的
    for log in data["items"]:
        assert log["user_id"] == admin_user.id


@pytest.mark.asyncio
async def test_operation_logs_filter_by_action(client, admin_user, db_session):
    """测试按操作类型筛选操作日志"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 按操作类型筛选
    response = await client.get(
        "/api/v1/operation-logs?action=LOGIN",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    # 所有日志的操作类型都应该是 LOGIN
    for log in data["items"]:
        assert log["action"] == "LOGIN"


@pytest.mark.asyncio
async def test_operation_logs_export(client, admin_user, db_session):
    """测试导出操作日志"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    response = await client.get(
        "/api/v1/operation-logs/export",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_operation_log_created_by_login(client, admin_user, db_session):
    """测试登录操作会自动记录日志"""
    # 记录登录前的日志数量
    result = await db_session.execute(
        OperationLog.__table__.select().where(OperationLog.__table__.c.user_id == admin_user.id)
    )
    before_count = len(result.fetchall())

    # 登录
    await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })

    # 记录登录后的日志数量
    result = await db_session.execute(
        OperationLog.__table__.select().where(OperationLog.__table__.c.user_id == admin_user.id)
    )
    after_count = len(result.fetchall())

    # 应该新增了一条日志
    assert after_count == before_count + 1


@pytest.mark.asyncio
async def test_operation_logs_pagination(client, admin_user, db_session):
    """测试操作日志分页"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 第一页
    response = await client.get(
        "/api/v1/operation-logs?page=1&page_size=10",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) <= 10


@pytest.mark.asyncio
async def test_operation_logs_unauthorized(client):
    """测试未认证用户无法访问操作日志"""
    response = await client.get("/api/v1/operation-logs")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_operation_logs_export_unauthorized(client):
    """测试未认证用户无法导出操作日志"""
    response = await client.get("/api/v1/operation-logs/export")
    assert response.status_code == 401
