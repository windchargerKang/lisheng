"""
用户管理模块测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserStatus
from app.models.role import Role
from app.core.security import get_password_hash, verify_password


@pytest.mark.asyncio
async def test_list_users(client, admin_user):
    """测试获取用户列表"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_user(client, admin_user):
    """测试创建用户"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "newuser", "password": "password123", "role_id": None}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"


@pytest.mark.asyncio
async def test_create_user_duplicate_username(client, admin_user):
    """测试创建重复用户名的用户"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 创建第一个用户
    await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "dupuser", "password": "password123", "role_id": None}
    )

    # 尝试创建重复用户名的用户
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "dupuser", "password": "password123", "role_id": None}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_user(client, admin_user):
    """测试获取用户详情"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    response = await client.get(
        f"/api/v1/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testadmin"


@pytest.mark.asyncio
async def test_update_user(client, admin_user, db_session):
    """测试更新用户"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 创建角色
    role = Role(name="测试角色", code="test_update_role", description="")
    db_session.add(role)
    await db_session.commit()

    # 更新用户角色
    response = await client.put(
        f"/api/v1/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"role_id": role.id}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_disable_user(client, admin_user, db_session):
    """测试禁用用户"""
    # 创建普通用户
    user = User(
        username="disabletest",
        password_hash=get_password_hash("password123"),
        role_type="operator"
    )
    db_session.add(user)
    await db_session.commit()
    user_id = user.id

    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 禁用用户
    response = await client.post(
        f"/api/v1/users/{user_id}/disable",
        headers={"Authorization": f"Bearer {token}"},
        json={"disable": True}
    )
    assert response.status_code == 200

    # 验证用户状态
    await db_session.refresh(user)
    assert user.status == UserStatus.DISABLED


@pytest.mark.asyncio
async def test_disabled_user_login(client, admin_user, db_session):
    """测试禁用用户无法登录"""
    # 创建并禁用用户
    user = User(
        username="disabledlogin",
        password_hash=get_password_hash("password123"),
        role_type="operator",
        status=UserStatus.DISABLED
    )
    db_session.add(user)
    await db_session.commit()

    # 尝试登录
    response = await client.post("/api/v1/auth/login", json={
        "username": "disabledlogin",
        "password": "password123"
    })
    assert response.status_code == 403
    assert "禁用" in response.json()["detail"]


@pytest.mark.asyncio
async def test_reset_password(client, admin_user, db_session):
    """测试重置密码"""
    # 创建用户
    user = User(
        username="resetpwdtest",
        password_hash=get_password_hash("oldpassword"),
        role_type="operator"
    )
    db_session.add(user)
    await db_session.commit()
    user_id = user.id

    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 重置密码
    response = await client.post(
        f"/api/v1/users/{user_id}/reset-password",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": "newpassword123"}
    )
    assert response.status_code == 200

    # 验证新密码可以登录
    await db_session.refresh(user)
    assert verify_password("newpassword123", user.password_hash)


@pytest.mark.asyncio
async def test_delete_user(client, admin_user, db_session):
    """测试删除用户"""
    # 创建用户
    user = User(
        username="deletetest",
        password_hash=get_password_hash("password123"),
        role_type="operator"
    )
    db_session.add(user)
    await db_session.commit()
    user_id = user.id

    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 删除用户
    response = await client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_self(client, admin_user):
    """测试不能删除自己的账号"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 尝试删除自己
    response = await client.delete(
        f"/api/v1/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "不能删除自己的账号" in response.json()["detail"]


@pytest.mark.asyncio
async def test_disable_self(client, admin_user):
    """测试不能禁用/启用自己的账号"""
    # 先登录获取 token
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "test123"
    })
    token = login_response.json()["token"]

    # 尝试禁用自己
    response = await client.post(
        f"/api/v1/users/{admin_user.id}/disable",
        headers={"Authorization": f"Bearer {token}"},
        json={"disable": True}
    )
    assert response.status_code == 400
    assert "不能禁用" in response.json()["detail"]
