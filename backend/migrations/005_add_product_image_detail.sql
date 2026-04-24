-- 迁移 005：产品图片和详情相关字段
-- 创建时间：2026-04-20
-- 说明：为 products 表添加图片和详情相关字段

-- 新增图片和详情字段
ALTER TABLE products ADD COLUMN image_url VARCHAR(500) NULL;
ALTER TABLE products ADD COLUMN images JSON NULL;
ALTER TABLE products ADD COLUMN detail TEXT NULL;

-- 创建索引（用于图片搜索）
CREATE INDEX IF NOT EXISTS idx_products_image_url ON products(image_url);
