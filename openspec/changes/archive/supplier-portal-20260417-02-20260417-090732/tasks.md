---
name: supplier-portal-20260417-02
status: planned
---

# 执行任务：供应商门户

## 任务列表

### Milestone 1：数据模型扩展

- [ ] Task 1.1：扩展 Users 模型（添加 supplier_id 字段）
- [ ] Task 1.2：扩展 PurchaseOrder 模型（添加 supplier_confirmed_at, supplier_status）
- [ ] Task 1.3：创建 PurchaseOrderAdjustment 模型
- [ ] Task 1.4：更新 models/__init__.py 导出
- [ ] Task 1.5：运行数据库迁移

### Milestone 2：供应商门户 API

- [ ] Task 2.1：实现订单列表 API（仅查看关联供应商的订单）
- [ ] Task 2.2：实现订单详情 API
- [ ] Task 2.3：实现确认供货 API
- [ ] Task 2.4：实现申请修改 API
- [ ] Task 2.5：实现入库记录查询 API
- [ ] Task 2.6：实现结算记录查询 API
- [ ] Task 2.7：实现供应商档案查询/更新 API

### Milestone 3：运营端审批 API

- [ ] Task 3.1：实现修改申请列表 API
- [ ] Task 3.2：实现批准修改 API
- [ ] Task 3.3：实现拒绝修改 API

### Milestone 4：供应商门户前端

- [ ] Task 4.1：创建门户首页/仪表盘
- [ ] Task 4.2：创建订单列表页面
- [ ] Task 4.3：创建订单详情/确认页面
- [ ] Task 4.4：创建入库记录页面
- [ ] Task 4.5：创建结算记录页面
- [ ] Task 4.6：创建档案管理页面
- [ ] Task 4.7：更新路由配置和认证逻辑

### Milestone 5：测试与验证

- [ ] Task 5.1：编写后端单元测试
- [ ] Task 5.2：编写 API 集成测试
- [ ] Task 5.3：前端功能验证
- [ ] Task 5.4：完整流程 E2E 测试

## 验收检查点

- [ ] 编译通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] Review 通过
- [ ] 供应商完整流程验证通过

## 下一步

执行 /harness-apply supplier-portal-20260417-02
