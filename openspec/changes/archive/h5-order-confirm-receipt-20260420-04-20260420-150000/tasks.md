---
name: h5-order-confirm-receipt-20260420-04
status: completed
---

# 执行任务：h5-order-confirm-receipt-20260420-04

## 任务列表

### Milestone 1：后端 API 实现

- [x] Task 1.1：新增确认收货 API 端点
  - 文件：backend/app/api/v1/orders.py
  - POST /orders/{id}/confirm
  - 验证订单属于当前用户
  - 验证订单状态为 shipped

- [x] Task 1.2：更新订单详情响应
  - 文件：backend/app/api/v1/orders.py
  - 确保返回完整的订单状态信息

### Milestone 2：前端确认收货 UI

- [x] Task 2.1：修改订单详情页
  - 文件：h5/src/views/OrderDetail.vue
  - 添加确认收货按钮（仅 shipped 状态显示）
  - 二次确认弹窗
  - 确认后刷新订单状态

- [x] Task 2.2：更新订单列表状态显示
  - 文件：h5/src/views/OrderList.vue（如有）
  - 确保 completed 状态正确显示

### Milestone 3：测试与验证

- [x] Task 3.1：后端 API 测试
  - 文件：backend/tests/test_orders.py
  - 确认收货 API 测试
  - 状态验证测试
  - 权限验证测试
  - 4 个测试用例全部通过

- [x] Task 3.2：前端功能测试
  - 确认收货按钮显示逻辑
  - 确认收货流程
  - 前端构建通过 (npm run build)

- [x] Task 3.3：完整流程测试
  - 用户下单 → 确认订单 → 管理员发货 → 用户确认收货

## 验收检查点

- [ ] 编译通过（前端 build 无错误）
- [ ] 后端服务启动正常
- [ ] 确认收货功能正常
- [ ] Review 通过

## 下一步

执行 `/harness-apply h5-order-confirm-receipt-20260420-04`
