-- Migration: 009_add_store_applications.sql
-- Description: 创建店铺/区代申请表
-- Date: 2026-04-24

-- 创建申请状态枚举
DO $$ BEGIN
    CREATE TYPE store_application_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 创建申请类型枚举
DO $$ BEGIN
    CREATE TYPE store_application_type AS ENUM ('SHOP', 'AGENT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 创建 store_applications 表
CREATE TABLE IF NOT EXISTS store_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    apply_type store_application_type NOT NULL,

    -- 店铺申请字段
    shop_name VARCHAR(100),
    shop_region_id INTEGER REFERENCES regions(id) ON DELETE RESTRICT,
    shop_agent_id INTEGER REFERENCES agents(id) ON DELETE SET NULL,
    shop_latitude NUMERIC(10, 8),
    shop_longitude NUMERIC(11, 8),

    -- 区代申请字段
    agent_name VARCHAR(100),
    agent_region_id INTEGER REFERENCES regions(id) ON DELETE RESTRICT,
    referrer_id INTEGER REFERENCES agents(id) ON DELETE SET NULL,

    -- 审核状态
    status store_application_status NOT NULL DEFAULT 'PENDING',
    reject_reason VARCHAR(500),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_store_applications_user_id ON store_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_store_applications_status ON store_applications(status);
CREATE INDEX IF NOT EXISTS idx_store_applications_apply_type ON store_applications(apply_type);
CREATE INDEX IF NOT EXISTS idx_store_applications_created_at ON store_applications(created_at DESC);

-- 创建触发器：更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_store_applications_updated_at ON store_applications;
CREATE TRIGGER update_store_applications_updated_at
    BEFORE UPDATE ON store_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
