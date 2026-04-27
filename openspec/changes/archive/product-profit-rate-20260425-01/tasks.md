---
name: product-profit-rate-20260425-01
status: planned
---

# 执行任务：product-profit-rate-20260425-01

## 任务列表

### Milestone 1：数据库迁移
- [ ] Task 1.1：创建 Alembic 迁移脚本，添加 service_fee_rate 和 agent_profit_rate 字段
- [ ] Task 1.2：在测试环境执行迁移并验证

### Milestone 2：后端模型和 Schema 修改
- [ ] Task 2.1：修改 Product 模型，新增分润比例字段
- [ ] Task 2.2：修改 ProductSchema，支持分润比例参数
- [ ] Task 2.3：修改 products.py API，处理分润比例参数

### Milestone 3：分润计算逻辑修改
- [ ] Task 3.1：修改 ProfitService._calculate_profit() 方法，支持产品级配置
- [ ] Task 3.2：编写单元测试验证分润计算逻辑

### Milestone 4：前端 UI 修改
- [ ] Task 4.1：修改 Products.vue，在定价对话框新增分润配置表单
- [ ] Task 4.2：添加分润比例输入校验（0-100%，精度 0.01%）
- [ ] Task 4.3：在产品列表中显示分润比例配置状态

### Milestone 5：验证和部署
- [ ] Task 5.1：本地测试完整流程
- [ ] Task 5.2：部署到远程服务器
- [ ] Task 5.3：远程验证分润计算正确性

## 验收检查点
- [ ] 编译通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] Review 通过

## 下一步
执行 /harness-apply product-profit-rate-20260425-01
