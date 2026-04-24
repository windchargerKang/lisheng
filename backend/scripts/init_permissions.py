"""
初始化角色和权限数据
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash


# 默认角色
DEFAULT_ROLES = [
    {"code": "admin", "name": "系统管理员", "description": "拥有所有权限"},
    {"code": "operator", "name": "运营人员", "description": "负责日常运营"},
    {"code": "agent", "name": "区代", "description": "区域代理"},
    {"code": "shop_agent", "name": "店铺代理", "description": "店铺代理"},
    {"code": "supplier", "name": "供应商", "description": "供应商"},
    {"code": "customer", "name": "客户", "description": "普通客户"},
]

# 默认权限
DEFAULT_PERMISSIONS = [
    # 用户管理
    {"code": "user:view", "name": "查看用户", "type": "MENU"},
    {"code": "user:create", "name": "创建用户", "type": "BUTTON"},
    {"code": "user:edit", "name": "编辑用户", "type": "BUTTON"},
    {"code": "user:delete", "name": "删除用户", "type": "BUTTON"},

    # 角色管理
    {"code": "role:view", "name": "查看角色", "type": "MENU"},
    {"code": "role:create", "name": "创建角色", "type": "BUTTON"},
    {"code": "role:edit", "name": "编辑角色", "type": "BUTTON"},
    {"code": "role:delete", "name": "删除角色", "type": "BUTTON"},

    # 日志管理
    {"code": "log:view", "name": "查看日志", "type": "MENU"},
    {"code": "log:export", "name": "导出日志", "type": "BUTTON"},

    # 业务权限
    {"code": "region:view", "name": "查看区域", "type": "MENU"},
    {"code": "shop:view", "name": "查看店铺", "type": "MENU"},
    {"code": "supplier:view", "name": "查看供应商", "type": "MENU"},
    {"code": "product:view", "name": "查看产品", "type": "MENU"},
    {"code": "order:view", "name": "查看订单", "type": "MENU"},
]


async def init_data():
    """初始化角色和权限数据"""
    # 使用 sync engine 执行 DDL
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # 将异步 URL 转换为同步 URL
    sync_url = str(settings.DATABASE_URL).replace("sqlite+aiosqlite", "sqlite").replace("postgresql+asyncpg", "postgresql")

    engine = create_engine(sync_url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 初始化角色
        for role_data in DEFAULT_ROLES:
            # 检查角色是否已存在
            result = session.execute(
                text("SELECT id FROM roles WHERE code = :code"),
                {"code": role_data["code"]}
            )
            if result.fetchone() is None:
                session.execute(
                    text("INSERT INTO roles (code, name, description) VALUES (:code, :name, :description)"),
                    role_data
                )
                print(f"创建角色：{role_data['name']} ({role_data['code']})")

        # 初始化权限
        for perm_data in DEFAULT_PERMISSIONS:
            # 检查权限是否已存在
            result = session.execute(
                text("SELECT id FROM permissions WHERE code = :code"),
                {"code": perm_data["code"]}
            )
            if result.fetchone() is None:
                session.execute(
                    text("INSERT INTO permissions (code, name, type) VALUES (:code, :name, :type)"),
                    perm_data
                )
                print(f"创建权限：{perm_data['name']} ({perm_data['code']})")

        # 为系统管理员角色绑定所有权限
        admin_result = session.execute(
            text("SELECT id FROM roles WHERE code = 'admin'")
        )
        admin_row = admin_result.fetchone()

        if admin_row:
            admin_role_id = admin_row[0]

            # 获取所有权限 ID
            perms_result = session.execute(
                text("SELECT id FROM permissions")
            )
            permission_ids = [row[0] for row in perms_result.fetchall()]

            # 为管理员绑定所有权限
            for perm_id in permission_ids:
                # 检查是否已存在
                exists = session.execute(
                    text("SELECT 1 FROM role_permissions WHERE role_id = :role_id AND permission_id = :perm_id"),
                    {"role_id": admin_role_id, "perm_id": perm_id}
                ).fetchone()

                if exists is None:
                    session.execute(
                        text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id)"),
                        {"role_id": admin_role_id, "perm_id": perm_id}
                    )

            print(f"为系统管理员绑定 {len(permission_ids)} 个权限")

        # 创建管理员账号
        admin_user_result = session.execute(
            text("SELECT id FROM users WHERE username = 'admin'")
        )
        if admin_user_result.fetchone() is None:
            session.execute(
                text("""INSERT INTO users (username, password_hash, role_type, status)
                        VALUES ('admin', :password_hash, 'admin', 'ACTIVE')"""),
                {"password_hash": get_password_hash("admin123")}
            )
            print("创建管理员账号：admin / admin123")

        session.commit()
        print("初始化完成！")

    except Exception as e:
        session.rollback()
        print(f"初始化失败：{e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    asyncio.run(init_data())
