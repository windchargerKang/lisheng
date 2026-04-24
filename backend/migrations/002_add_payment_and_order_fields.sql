-- 迁移：订单表扩展字段 + 支付记录表
-- 日期：2026-04-20
-- 说明：移动端购物全流程打通 - 数据库迁移

-- 1. 订单表新增字段
ALTER TABLE orders ADD COLUMN receiver_name VARCHAR(100);
ALTER TABLE orders ADD COLUMN receiver_phone VARCHAR(20);
ALTER TABLE orders ADD COLUMN receiver_address TEXT;
ALTER TABLE orders ADD COLUMN remark TEXT;
ALTER TABLE orders ADD COLUMN paid_at DATETIME;

-- 2. 创建支付记录表
CREATE TABLE IF NOT EXISTS payment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    payment_method VARCHAR(20) NOT NULL,  -- wechat/alipay/bank
    transaction_id VARCHAR(64) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'success',  -- success/failed/pending
    paid_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_payment_order_id ON payment_records(order_id);
CREATE INDEX IF NOT EXISTS idx_payment_status ON payment_records(status);
