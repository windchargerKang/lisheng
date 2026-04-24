---
name: admin-order-shipment-20260420-03
status: completed
---

# 执行任务：admin-order-shipment-20260420-03

## 任务列表

### Milestone 1：数据库与后端模型

- [x] Task 1.1：创建数据库迁移脚本
  - 文件：backend/migrations/004_add_order_shipment.sql
  - 新增字段：courier_company, courier_no, shipped_at, shipper_id

- [x] Task 1.2：更新 Order 数据模型
  - 文件：backend/app/models/order.py
  - 新增物流相关字段定义

- [x] Task 1.3：新增订单 Schema 定义
  - 文件：backend/app/schemas/order.py
  - OrderShipRequest, OrderShipResponse, AdminOrderResponse

### Milestone 2：后端 API 实现

- [x] Task 2.1：创建管理端订单 API 路由
  - 文件：backend/app/api/v1/admin_orders.py
  - GET /admin/orders - 订单列表（支持状态筛选、分页）
  - GET /admin/orders/{id} - 订单详情
  - POST /admin/orders/{id}/ship - 发货操作

- [x] Task 2.2：注册 API 路由
  - 文件：backend/app/api/v1/api.py
  - 添加 admin_orders router

- [x] Task 2.3：权限初始化脚本
  - 文件：backend/scripts/init_permissions.py
  - 创建 order:view, order:ship 权限
  - 创建运营管理员角色

### Milestone 3：前端订单管理页面

- [x] Task 3.1：配置路由
  - 文件：frontend/src/router/index.ts
  - 新增 /orders/list 和 /orders/detail 路由

- [x] Task 3.2：创建订单列表页
  - 文件：frontend/src/views/orders/List.vue
  - 订单列表展示、状态筛选、分页

- [x] Task 3.3：创建订单详情页
  - 文件：frontend/src/views/orders/Detail.vue
  - 订单完整信息展示

- [x] Task 3.4：创建发货弹窗组件
  - 文件：frontend/src/views/orders/List.vue (内嵌)
  - 物流公司输入、运单号输入

- [x] Task 3.5：封装订单 API
  - 文件：frontend/src/api/order.ts (使用通用 apiClient)

### Milestone 4：测试与验证

- [x] Task 4.1：后端 API 测试
  - 文件：backend/tests/test_admin_orders.py
  - 订单列表、发货操作、权限验证 (11 个测试通过)

- [x] Task 4.2：前端功能测试
  - 订单列表筛选
  - 发货流程
  - 前端构建通过 (npm run build)

- [x] Task 4.3：完整流程测试
  - 用户下单 → 用户确认 → 管理员发货 → 用户确认收货

## 验收检查点

- [ ] 编译通过（前端 build 无错误）
- [ ] 后端服务启动正常
- [ ] 数据库迁移执行成功
- [ ] 订单列表和发货功能正常
- [ ] Review 通过

## 下一步

执行 `/harness-apply admin-order-shipment-20260420-03`
