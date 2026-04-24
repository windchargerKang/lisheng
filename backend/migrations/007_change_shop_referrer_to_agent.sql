-- 将 shops 表的 referrer_id 改为 agent_id（绑定区代）
-- 步骤：
-- 1. 添加新的 agent_id 列
-- 2. 迁移数据（如果有）
-- 3. 删除旧的 referrer_id 列
-- 4. 创建索引

-- 添加新的 agent_id 列
ALTER TABLE shops ADD COLUMN agent_id INTEGER NULL;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_shops_agent_id ON shops(agent_id);

-- 添加外键约束（SQLite 不直接支持 ALTER TABLE ADD CONSTRAINT，需要重建表）
-- 在应用层保证数据一致性
