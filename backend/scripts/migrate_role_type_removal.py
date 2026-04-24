"""
role_type 字段移除迁移脚本

用途：
1. 确保所有用户的 role_id 正确设置（基于原有的 role_type）
2. 可选：删除 users 表的 role_type 列（因为现在是计算属性）

使用方法：
    python scripts/migrate_role_type_removal.py
"""
import sqlite3
import os

def get_role_id_by_code(cursor, code: str) -> int:
    """根据角色 code 获取角色 ID"""
    cursor.execute('SELECT id FROM roles WHERE code = ?', (code,))
    result = cursor.fetchone()
    return result[0] if result else None


def migrate():
    # 获取数据库路径
    script_dir = os.path.dirname(__file__)
    db_path = os.path.join(script_dir, '..', 'channel_sales.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"连接到数据库：{db_path}")

    # 检查 users 表结构
    cursor.execute('PRAGMA table_info(users)')
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"当前 users 表列：{column_names}")

    # 检查是否有 role_type 和 role_id 列
    has_role_type = 'role_type' in column_names
    has_role_id = 'role_id' in column_names

    if not has_role_id:
        print("错误：role_id 列不存在，无法执行迁移")
        return

    # 获取所有角色映射
    roles_map = {}
    cursor.execute('SELECT id, code FROM roles')
    for row in cursor.fetchall():
        roles_map[row[1]] = row[0]

    print(f"角色映射：{roles_map}")

    # 第一步：确保所有用户的 role_id 正确设置
    print("\n第一步：检查并修复用户的 role_id...")

    cursor.execute('SELECT id, username, role_type, role_id FROM users')
    users = cursor.fetchall()

    updated_count = 0
    for user_id, username, role_type, role_id in users:
        # 如果 role_id 为空，尝试从 role_type 推断
        if role_id is None and role_type:
            target_role_id = roles_map.get(role_type)
            if target_role_id:
                cursor.execute(
                    'UPDATE users SET role_id = ? WHERE id = ?',
                    (target_role_id, user_id)
                )
                print(f"  修复用户 {username}: role_type={role_type} -> role_id={target_role_id}")
                updated_count += 1
        # 如果 role_type 为空，尝试从 role_id 推断（反向同步）
        elif role_type is None and role_id:
            cursor.execute('SELECT code FROM roles WHERE id = ?', (role_id,))
            role_result = cursor.fetchone()
            if role_result:
                print(f"  用户 {username}: role_id={role_id}, role_code={role_result[0]}")

    print(f"共修复 {updated_count} 个用户的 role_id")

    # 第二步：验证数据一致性
    print("\n第二步：验证 role_type 和 role_id 的一致性...")

    cursor.execute('''
        SELECT u.id, u.username, u.role_type, u.role_id, r.code as role_code
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
    ''')

    inconsistencies = []
    for row in cursor.fetchall():
        user_id, username, role_type, role_id, role_code = row
        if role_type and role_code and role_type != role_code:
            inconsistencies.append((user_id, username, role_type, role_code))
            print(f"  ⚠️  不一致：用户 {username} - role_type={role_type}, role_code={role_code}")

    if not inconsistencies:
        print("  ✓ 所有用户的 role_type 和 role_id 一致")

    # 第三步：删除 role_type 列
    print("\n第三步：删除 role_type 列...")

    if has_role_type:
        print("  执行表重建...")

        # 备份原表
        cursor.execute('DROP TABLE IF EXISTS users_backup')
        cursor.execute('CREATE TABLE users_backup AS SELECT * FROM users')
        print("  ✓ 已创建备份表 users_backup")

        # 创建新表（不含 role_type）
        cursor.execute('''
            CREATE TABLE users_new AS
            SELECT id, username, password_hash, role_id, supplier_id, status,
                   last_login_at, last_login_ip, created_at
            FROM users
        ''')
        print("  ✓ 已创建新表 users_new")

        # 删除原表
        cursor.execute('DROP TABLE users')
        print("  ✓ 已删除原表 users")

        # 重命名新表
        cursor.execute('ALTER TABLE users_new RENAME TO users')
        print("  ✓ 已重命名 users_new → users")

        # 重新创建索引
        cursor.execute('CREATE INDEX idx_users_id ON users(id)')
        cursor.execute('CREATE INDEX idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX idx_role_id ON users(role_id)')
        cursor.execute('CREATE INDEX idx_status ON users(status)')
        print("  ✓ 已重新创建索引")

        conn.commit()
        print("\n  role_type 列已删除!")
    else:
        print("  - role_type 列已不存在，跳过")

    conn.close()

    print("\n迁移完成!")
    print("\n验证：")
    print("  sqlite3 channel_sales.db \"PRAGMA table_info(users);\"")


if __name__ == '__main__':
    migrate()
