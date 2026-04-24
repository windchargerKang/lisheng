"""
权限管理数据库迁移脚本
运行此脚本创建 RBAC 相关表结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings

# 创建同步引擎用于迁移
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", "").replace("+aiosqlite", ""),
    echo=True,
    future=True
)


def create_tables():
    """创建新表"""
    print("创建 RBAC 相关表...")

    # 直接执行 SQL 创建表
    with sync_engine.connect() as conn:
        # 创建 roles 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                code VARCHAR(50) NOT NULL UNIQUE,
                description VARCHAR(200),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # 创建 permissions 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                code VARCHAR(100) NOT NULL UNIQUE,
                type VARCHAR(20) NOT NULL,
                parent_id INTEGER,
                api_path VARCHAR(200),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES permissions(id)
            )
        """))

        # 创建 role_permissions 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS role_permissions (
                id INTEGER PRIMARY KEY,
                role_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(role_id, permission_id),
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
            )
        """))

        # 创建 operation_logs 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                action VARCHAR(50) NOT NULL,
                resource_type VARCHAR(50),
                resource_id INTEGER,
                ip_address VARCHAR(45),
                user_agent VARCHAR(500),
                details JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """))

        # 创建索引
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_action ON operation_logs(user_id, action)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_created_at ON operation_logs(created_at)"))
        # 补充缺失的索引
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_permission_parent_id ON permissions(parent_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_role_permission_permission_id ON role_permissions(permission_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_operation_log_resource ON operation_logs(resource_type, resource_id)"))

        # 为 users 表添加新字段
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN role_id INTEGER"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_role_id ON users(role_id)"))
        except Exception as e:
            print(f"  注意：role_id 字段可能已存在 - {e}")

        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'ACTIVE'"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_status ON users(status)"))
        except Exception as e:
            print(f"  注意：status 字段可能已存在 - {e}")

        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_login_at DATETIME"))
        except Exception as e:
            print(f"  注意：last_login_at 字段可能已存在 - {e}")

        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_login_ip VARCHAR(45)"))
        except Exception as e:
            print(f"  注意：last_login_ip 字段可能已存在 - {e}")

        conn.commit()

    print("✓ 表创建完成")


def init_default_data():
    """初始化默认角色和权限"""
    print("初始化默认角色和权限...")

    with Session(sync_engine) as session:
        # 检查是否已存在数据
        result = session.execute(text("SELECT COUNT(*) FROM roles"))
        count = result.scalar()
        if count > 0:
            print("  默认数据已存在，跳过初始化")
            return

        # 创建默认角色
        default_roles = [
            ("admin", "系统管理员", "拥有所有权限"),
            ("operator", "运营人员", "业务运营角色"),
            ("agent", "区代", "区域代理"),
            ("shop_agent", "店铺代理", "店铺代理"),
            ("supplier", "供应商", "供应商角色"),
        ]

        role_ids = {}
        for code, name, desc in default_roles:
            session.execute(
                text("INSERT INTO roles (code, name, description) VALUES (:code, :name, :desc)"),
                {"code": code, "name": name, "desc": desc}
            )
            result = session.execute(text("SELECT id FROM roles WHERE code = :code"), {"code": code})
            role_ids[code] = result.scalar()

        # 创建默认权限
        default_permissions = [
            # 用户管理
            ("user:view", "查看用户", "MENU"),
            ("user:create", "创建用户", "BUTTON"),
            ("user:edit", "编辑用户", "BUTTON"),
            ("user:delete", "删除用户", "BUTTON"),
            # 角色管理
            ("role:view", "查看角色", "MENU"),
            ("role:create", "创建角色", "BUTTON"),
            ("role:edit", "编辑角色", "BUTTON"),
            ("role:delete", "删除角色", "BUTTON"),
            # 日志管理
            ("log:view", "查看日志", "MENU"),
            ("log:export", "导出日志", "BUTTON"),
            # 业务权限
            ("region:view", "查看区域", "MENU"),
            ("shop:view", "查看店铺", "MENU"),
            ("agent:view", "查看区代", "MENU"),
            ("product:view", "查看产品", "MENU"),
            ("order:view", "查看订单", "MENU"),
            ("supplier:view", "查看供应商", "MENU"),
            ("purchase:view", "查看采购", "MENU"),
            ("inbound:view", "查看入库", "MENU"),
            ("settlement:view", "查看结算", "MENU"),
        ]

        perm_ids = {}
        for code, name, ptype in default_permissions:
            session.execute(
                text("INSERT INTO permissions (code, name, type) VALUES (:code, :name, :type)"),
                {"code": code, "name": name, "type": ptype}
            )
            result = session.execute(text("SELECT id FROM permissions WHERE code = :code"), {"code": code})
            perm_ids[code] = result.scalar()

        # 管理员角色绑定所有权限
        admin_role_id = role_ids.get("admin")
        if admin_role_id:
            for perm_id in perm_ids.values():
                session.execute(
                    text("INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id)"),
                    {"role_id": admin_role_id, "perm_id": perm_id}
                )

        session.commit()

        print(f"✓ 创建 {len(default_roles)} 个角色")
        print(f"✓ 创建 {len(default_permissions)} 个权限")
        print(f"✓ 管理员角色已绑定所有权限")


def migrate_existing_users():
    """迁移现有用户到 RBAC 系统"""
    print("迁移现有用户...")

    with Session(sync_engine) as session:
        # 获取角色 ID
        result = session.execute(text("SELECT id, code FROM roles"))
        role_map = {row[1]: row[0] for row in result.fetchall()}

        if not role_map:
            print("  警告：角色未正确初始化，跳过用户迁移")
            return

        # 迁移现有用户
        result = session.execute(text("SELECT id, role_type FROM users WHERE role_id IS NULL"))
        users = result.fetchall()
        migrated_count = 0

        for user_id, role_type in users:
            # 根据 role_type 分配角色
            target_role = "operator"
            if role_type == "admin":
                target_role = "admin"
            elif role_type == "supplier":
                target_role = "supplier"

            role_id = role_map.get(target_role, role_map.get("operator"))
            if role_id:
                session.execute(
                    text("UPDATE users SET role_id = :role_id WHERE id = :user_id"),
                    {"role_id": role_id, "user_id": user_id}
                )
                migrated_count += 1

        if migrated_count > 0:
            session.commit()
            print(f"✓ 迁移 {migrated_count} 个现有用户到 RBAC 系统")
        else:
            print("  无需迁移用户")


def main():
    print("=" * 50)
    print("权限管理数据库迁移")
    print("=" * 50)

    try:
        # 1. 创建表
        create_tables()

        # 2. 初始化默认数据
        init_default_data()

        # 3. 迁移现有用户
        migrate_existing_users()

        print("=" * 50)
        print("✓ 迁移完成！")
        print("=" * 50)

    except Exception as e:
        print(f"✗ 迁移失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
