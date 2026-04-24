-- 添加钱包相关表
-- 步骤：
-- 1. 创建 wallets 表
-- 2. 创建 wallet_transactions 表
-- 3. 创建索引
-- 4. 为现有用户初始化钱包

-- 创建 wallets 表
CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建 wallet_transactions 表
CREATE TABLE IF NOT EXISTS wallet_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    balance_after DECIMAL(10, 2) NOT NULL,
    transaction_no VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL,
    withdraw_method VARCHAR(50),
    withdraw_account VARCHAR(100),
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wallet_id) REFERENCES wallets(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_wallets_user_id ON wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_wallet_id ON wallet_transactions(wallet_id);
CREATE INDEX IF NOT EXISTS idx_transactions_transaction_no ON wallet_transactions(transaction_no);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON wallet_transactions(status);

-- 为现有用户初始化钱包（余额为 0）
INSERT OR IGNORE INTO wallets (user_id, balance, created_at, updated_at)
SELECT id, 0.00, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM users
WHERE id NOT IN (SELECT user_id FROM wallets);
