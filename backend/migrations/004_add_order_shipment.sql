-- 迁移 004：订单发货相关字段
-- 创建时间：2026-04-20
-- 说明：为 orders 表添加物流相关字段

-- 新增物流字段
ALTER TABLE orders ADD COLUMN courier_company VARCHAR(100) NULL;
ALTER TABLE orders ADD COLUMN courier_no VARCHAR(50) NULL;
ALTER TABLE orders ADD COLUMN shipped_at DATETIME NULL;
ALTER TABLE orders ADD COLUMN shipper_id INTEGER NULL;

-- 创建索引（用于查询发货订单）
CREATE INDEX IF NOT EXISTS idx_orders_shipped_at ON orders(shipped_at);
CREATE INDEX IF NOT EXISTS idx_orders_shipper_id ON orders(shipper_id);
