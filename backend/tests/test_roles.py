"""
角色管理模块测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_list_roles(client, admin_user):
    """测试获取角色列表"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    response = await client.get(
        "/api/v1/roles",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_role(client, admin_user):
    """测试创建角色"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    response = await client.post(
        "/api/v1/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "测试角色", "code": "test_role", "description": "测试描述"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试角色"
    assert data["code"] == "test_role"


@pytest.mark.asyncio
async def test_create_role_duplicate_code(client, admin_user):
    """测试创建重复角色代码"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 创建第一个角色
    await client.post(
        "/api/v1/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "测试角色 1", "code": "test_dup", "description": ""}
    )

    # 尝试创建重复代码的角色
    response = await client.post(
        "/api/v1/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "测试角色 2", "code": "test_dup", "description": ""}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_role(client, admin_user):
    """测试获取角色详情"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 创建角色
    create_response = await client.post(
        "/api/v1/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "测试详情角色", "code": "test_detail", "description": ""}
    )
    role_id = create_response.json()["id"]

    # 获取角色详情
    response = await client.get(
        f"/api/v1/roles/{role_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == role_id
    assert data["name"] == "测试详情角色"


@pytest.mark.asyncio
async def test_update_role(client, admin_user):
    """测试更新角色"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 创建角色
    create_response = await client.post(
        "/api/v1/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "测试更新角色", "code": "test_update", "description": "原描述"}
    )
    role_id = create_response.json()["id"]

    # 更新角色
    response = await client.put(
        f"/api/v1/roles/{role_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "已更新角色", "description": "新描述"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "已更新角色"
    assert data["description"] == "新描述"


@pytest.mark.asyncio
async def test_delete_role(client, admin_user):
    """测试删除角色"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 创建角色
    create_response = await client.post(
        "/api/v1/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "测试删除角色", "code": "test_delete", "description": ""}
    )
    role_id = create_response.json()["id"]

    # 删除角色
    response = await client.delete(
        f"/api/v1/roles/{role_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # 验证角色已删除
    get_response = await client.get(
        f"/api/v1/roles/{role_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_role_in_use(client, admin_user, db_session):
    """测试删除被用户使用的角色"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 创建角色
    role = Role(name="被使用角色", code="test_in_use", description="")
    db_session.add(role)
    await db_session.commit()
    role_id = role.id

    # 将管理员用户关联到该角色
    admin_user.role_id = role_id
    await db_session.commit()

    # 尝试删除角色
    response = await client.delete(
        f"/api/v1/roles/{role_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "已被用户使用" in response.json()["detail"]
