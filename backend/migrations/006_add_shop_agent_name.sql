-- 为 shops 和 agents 表添加 name 字段
ALTER TABLE shops ADD COLUMN name VARCHAR(100) NULL;
ALTER TABLE agents ADD COLUMN name VARCHAR(100) NULL;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_shops_name ON shops(name);
CREATE INDEX IF NOT EXISTS idx_agents_name ON agents(name);
