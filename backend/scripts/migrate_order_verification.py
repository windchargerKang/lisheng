"""
订单核销功能数据库迁移脚本

用途：
1. 为 orders 表添加 order_type 和 verified_at 列
2. 创建 verification_codes 表

使用方法：
    python scripts/migrate_order_verification.py
"""
import sqlite3
import os

def migrate():
    # 获取数据库路径
    script_dir = os.path.dirname(__file__)
    db_path = os.path.join(script_dir, '..', 'channel_sales.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"连接到数据库：{db_path}")

    # 检查 orders 表结构
    cursor.execute('PRAGMA table_info(orders)')
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"当前 orders 表列数：{len(columns)}")

    # 添加缺失的列
    if 'order_type' not in column_names:
        print('添加 order_type 列...')
        cursor.execute('ALTER TABLE orders ADD COLUMN order_type VARCHAR(20) DEFAULT "ecommerce"')
        print('  ✓ 已添加 order_type')
    else:
        print('  - order_type 列已存在')

    if 'verified_at' not in column_names:
        print('添加 verified_at 列...')
        cursor.execute('ALTER TABLE orders ADD COLUMN verified_at DATETIME')
        print('  ✓ 已添加 verified_at')
    else:
        print('  - verified_at 列已存在')

    # 检查 verification_codes 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='verification_codes'")
    if not cursor.fetchone():
        print('创建 verification_codes 表...')
        cursor.execute('''
            CREATE TABLE verification_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(12) NOT NULL UNIQUE,
                order_id INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'unused',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_at DATETIME,
                verified_by INTEGER,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (verified_by) REFERENCES users(id)
            )
        ''')
        print('  ✓ 已创建 verification_codes 表')

        # 创建索引
        cursor.execute('CREATE INDEX idx_verification_code ON verification_codes(code)')
        print('  ✓ 已创建 code 索引')

        cursor.execute('CREATE INDEX idx_verification_order_id ON verification_codes(order_id)')
        print('  ✓ 已创建 order_id 索引')
    else:
        print('  - verification_codes 表已存在')

    # 检查 wallet_transactions 表是否有新增的 transaction_type
    cursor.execute('PRAGMA table_info(wallet_transactions)')
    wt_columns = [col[1] for col in cursor.fetchall()]

    # 检查 wallet 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wallets'")
    if not cursor.fetchone():
        print('创建 wallets 表...')
        cursor.execute('''
            CREATE TABLE wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                balance NUMERIC(10, 2) DEFAULT 0.00,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print('  ✓ 已创建 wallets 表')
    else:
        print('  - wallets 表已存在')

    # 检查 wallet_transactions 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wallet_transactions'")
    if not cursor.fetchone():
        print('创建 wallet_transactions 表...')
        cursor.execute('''
            CREATE TABLE wallet_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_id INTEGER NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                balance_after NUMERIC(10, 2) NOT NULL,
                transaction_no VARCHAR(32) NOT NULL UNIQUE,
                status VARCHAR(20) NOT NULL DEFAULT 'completed',
                remark TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (wallet_id) REFERENCES wallets(id)
            )
        ''')
        print('  ✓ 已创建 wallet_transactions 表')

        cursor.execute('CREATE INDEX idx_wallet_transaction_wallet_id ON wallet_transactions(wallet_id)')
        print('  ✓ 已创建 wallet_id 索引')

        cursor.execute('CREATE INDEX idx_wallet_transaction_type ON wallet_transactions(transaction_type)')
        print('  ✓ 已创建 transaction_type 索引')
    else:
        print('  - wallet_transactions 表已存在')

    conn.commit()
    conn.close()
    print('\\n数据库迁移完成!')

if __name__ == '__main__':
    migrate()
