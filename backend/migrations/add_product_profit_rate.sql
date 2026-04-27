-- 产品分润比例迁移脚本
-- 执行时间：2026-04-25

-- 新增服务费比例字段 (0.3000 = 30%)
ALTER TABLE products ADD COLUMN service_fee_rate NUMERIC(5, 4);

-- 新增区代利润比例字段 (0.1000 = 10%)
ALTER TABLE products ADD COLUMN agent_profit_rate NUMERIC(5, 4);

-- 添加注释（SQLite 不支持 COMMENT，仅记录）
-- service_fee_rate: 服务费比例，范围 0-1，nullable（为空时使用全局默认值）
-- agent_profit_rate: 区代利润比例，范围 0-1，nullable（为空时使用全局默认值）

-- 验证查询
SELECT id, name, service_fee_rate, agent_profit_rate
FROM products
LIMIT 5;
