---
name: product-image-detail-20260420-05
status: planned
---

# 执行任务：product-image-detail-20260420-05

## 任务列表

### Milestone 1：数据库与后端模型

- [ ] Task 1.1：创建数据库迁移脚本
  - 文件：backend/migrations/005_add_product_image_detail.sql
  - 新增字段：image_url, images, detail

- [ ] Task 1.2：更新 Product 数据模型
  - 文件：backend/app/models/product.py
  - 新增图片和详情字段

### Milestone 2：后端 API 扩展

- [ ] Task 2.1：更新产品 API
  - 文件：backend/app/api/v1/products.py
  - 响应增加 image_url, images, detail 字段

- [ ] Task 2.2：后端 API 测试
  - 文件：backend/tests/test_products.py
  - 图片和详情字段测试

### Milestone 3：管理端图片上传和详情编辑

- [ ] Task 3.1：修改产品列表页
  - 文件：frontend/src/views/Products.vue
  - 显示产品缩略图

- [ ] Task 3.2：修改产品编辑页
  - 文件：frontend/src/views/ProductDetail.vue
  - 图片上传组件
  - 详情编辑器

### Milestone 4：H5 端产品展示

- [ ] Task 4.1：修改 H5 产品列表页
  - 文件：h5/src/views/Products.vue
  - 显示产品缩略图

- [ ] Task 4.2：修改 H5 产品详情页
  - 文件：h5/src/views/ProductDetail.vue
  - 图片轮播
  - 详情展示

## 验收检查点

- [ ] 编译通过（前端 build 无错误）
- [ ] 后端服务启动正常
- [ ] 图片上传和详情编辑功能正常
- [ ] H5 端展示正常
- [ ] Review 通过

## 下一步

执行 `/harness-apply product-image-detail-20260420-05`
