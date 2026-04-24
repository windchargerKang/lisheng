---
name: product-image-detail-20260420-05
status: designed
created: 2026-04-20
---

# 技术方案：产品图片和详情功能

## 方案概述

为产品管理模块添加产品图片和详情描述功能，包括数据模型扩展、后端 API 支持、管理端图片上传和详情编辑、H5 端展示。

## 详细设计

### 架构变更

**后端新增/修改模块：**
| 模块 | 说明 |
|------|------|
| backend/app/models/product.py | Product 模型新增 image_url, detail 字段 |
| backend/app/api/v1/products.py | 产品 API 支持图片和详情 |
| backend/migrations/005_add_product_image_detail.sql | 数据库迁移 |

**前端管理端修改：**
| 页面 | 说明 |
|------|------|
| frontend/src/views/Products.vue | 列表显示缩略图 |
| frontend/src/views/ProductDetail.vue | 新增/编辑页支持图片上传和详情编辑 |

**前端 H5 端修改：**
| 页面 | 说明 |
|------|------|
| h5/src/views/Products.vue | 列表显示缩略图 |
| h5/src/views/ProductDetail.vue | 显示产品图片和详情 |

### 数据模型变更

**products 表新增字段：**
```sql
ALTER TABLE products ADD COLUMN image_url VARCHAR(500) NULL;  -- 主图 URL
ALTER TABLE products ADD COLUMN images JSON NULL;             -- 多图 JSON 数组
ALTER TABLE products ADD COLUMN detail TEXT NULL;             -- 详情描述（HTML）
```

**Product 模型扩展：**
```python
class Product(Base):
    # ... 现有字段 ...
    image_url = Column(String(500), nullable=True)  # 主图
    images = Column(JSON, nullable=True)            # 多图 ["url1", "url2", ...]
    detail = Column(Text, nullable=True)            # 详情 HTML
```

### 接口设计

**现有 API 扩展：**

| 方法 | 路径 | 变更说明 |
|------|------|----------|
| GET | /products | 响应增加 image_url, images 字段 |
| GET | /products/{id} | 响应增加 image_url, images, detail 字段 |
| POST | /products | 请求支持 image_url, images, detail 字段 |
| PUT | /products/{id} | 请求支持 image_url, images, detail 字段 |

**响应示例：**
```json
{
  "id": 1,
  "name": "产品名",
  "image_url": "https://example.com/image1.jpg",
  "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
  "detail": "<p>产品详情描述...</p>",
  ...
}
```

### 前端实现设计

#### 管理端产品编辑页

```vue
<el-upload
  :file-list="fileList"
  :on-change="handleFileChange"
  :limit="9"
  multiple
>
  <el-button>上传图片</el-button>
</el-upload>

<el-input
  v-model="form.detail"
  type="textarea"
  :rows="10"
  placeholder="产品详情（支持 HTML）"
/>
```

#### H5 端产品详情页

```vue
<!-- 图片轮播 -->
<van-swipe :autoplay="3000">
  <van-swipe-item v-for="img in images" :key="img">
    <img :src="img" style="width: 100%" />
  </van-swipe-item>
</van-swipe>

<!-- 详情 -->
<div class="detail-content" v-html="product.detail"></div>
```

## 影响范围

### 受影响模块
- 后端：Product 模型、products API
- 管理端：产品列表、产品编辑页
- H5 端：产品列表、产品详情页

### 受保护路径变更
- 无

### 向后兼容性
- 新增字段为 nullable，不影响现有数据
- API 响应扩展字段，不影响现有客户端

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 图片存储路径 | 中 | 使用相对路径或配置 CDN 域名 |
| 富文本 XSS | 中 | 后端过滤危险 HTML 标签 |
| 图片大小限制 | 低 | 前端限制上传大小（如 5MB） |

## 事务与数据

### 事务边界
- 产品创建/更新：单表操作，无需事务

### 数据迁移
```sql
-- 执行 migrations/005_add_product_image_detail.sql
ALTER TABLE products ADD COLUMN image_url VARCHAR(500) NULL;
ALTER TABLE products ADD COLUMN images JSON NULL;
ALTER TABLE products ADD COLUMN detail TEXT NULL;
```

### 回滚方案
- 删除新增的 3 个字段

## 测试策略

1. **后端测试**
   - 产品创建 API 测试（包含图片和详情）
   - 产品详情 API 测试
   - 图片字段验证

2. **前端测试**
   - 管理端图片上传
   - 详情编辑
   - H5 端图片和详情展示
