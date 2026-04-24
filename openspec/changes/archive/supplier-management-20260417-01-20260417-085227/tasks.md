---
name: supplier-management-20260417-01
status: planned
---

# 执行任务：供应商管理

## 任务列表

### Milestone 1：数据模型与后端框架

- [ ] Task 1.1：创建 Supplier 数据模型
- [ ] Task 1.2：创建 PurchaseOrder 和 PurchaseOrderItem 数据模型
- [ ] Task 1.3：创建 PurchaseInbound 和 Settlement 数据模型
- [ ] Task 1.4：扩展 Product 模型（添加 supplier_id 和 cost_price）
- [ ] Task 1.5：更新 models/__init__.py 导出

### Milestone 2：供应商管理 API

- [ ] Task 2.1：实现供应商列表 API（分页、筛选）
- [ ] Task 2.2：实现创建供应商 API
- [ ] Task 2.3：实现供应商详情 API
- [ ] Task 2.4：实现更新供应商 API
- [ ] Task 2.5：实现删除供应商 API

### Milestone 3：采购订单 API

- [ ] Task 3.1：实现采购订单列表 API（分页、状态筛选）
- [ ] Task 3.2：实现创建采购订单 API
- [ ] Task 3.3：实现订单详情 API
- [ ] Task 3.4：实现确认订单 API
- [ ] Task 3.5：实现取消订单 API

### Milestone 4：入库与结算 API

- [ ] Task 4.1：实现采购入库 API（增加库存）
- [ ] Task 4.2：实现入库记录列表 API
- [ ] Task 4.3：实现结算记录 API
- [ ] Task 4.4：实现现款结算自动创建逻辑

### Milestone 5：运营端前端页面

- [ ] Task 5.1：创建供应商管理页面（列表、新增、编辑）
- [ ] Task 5.2：创建采购订单列表页面
- [ ] Task 5.3：创建采购订单详情/创建页面
- [ ] Task 5.4：创建入库管理页面
- [ ] Task 5.5：创建结算管理页面

### Milestone 6：测试与验证

- [ ] Task 6.1：编写后端单元测试
- [ ] Task 6.2：编写 API 集成测试
- [ ] Task 6.3：前端功能验证
- [ ] Task 6.4：完整流程 E2E 测试

## 验收检查点

- [ ] 编译通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] Review 通过
- [ ] 完整采购流程验证通过

## 下一步

执行 `/harness-apply supplier-management-20260417-01`
