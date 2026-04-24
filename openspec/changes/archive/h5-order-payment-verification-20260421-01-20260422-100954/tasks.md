---
name: h5-order-payment-verification-20260421-01
status: planned
---

# 执行任务：h5-order-payment-verification-20260421-01

## 任务列表

### Milestone 1：数据模型变更

- [ ] Task 1.1：修改 Order 模型，新增 `order_type`、`verification_code`、`verified_at` 字段
- [ ] Task 1.2：修改 OrderStatus 枚举，新增 `verified` 状态
- [ ] Task 1.3：创建 VerificationCode 模型（核销码表）
- [ ] Task 1.4：修改 TransactionType 枚举，新增 `ORDER_PAYMENT`、`SERVICE_FEE`、`AGENT_PROFIT`
- [ ] Task 1.5：创建分润配置文件 `backend/config.json`

### Milestone 2：后端服务层实现

- [ ] Task 2.1：创建 OrderService 服务类（下单、确认订单逻辑）
- [ ] Task 2.2：创建 ProfitService 服务类（分润计算和分发）
- [ ] Task 2.3：创建 VerificationCodeService 服务类（核销码生成和验证）
- [ ] Task 2.4：修改 WalletService 支持新交易类型

### Milestone 3：后端 API 实现

- [ ] Task 3.1：扩展 POST /orders/create 接口（支持 order_type 自动判断）
- [ ] Task 3.2：扩展 POST /orders/{order_id}/confirm 接口（钱包扣款）
- [ ] Task 3.3：新增 POST /verification/verify 接口（店铺核销）
- [ ] Task 3.4：新增 GET /verification/{code} 接口（核销码验证）

### Milestone 4：H5 前端实现

- [ ] Task 4.1：创建 H5 核销页面 `h5/src/views/Verification.vue`
- [ ] Task 4.2：在 H5 路由中添加核销页面路由（店铺角色可见）
- [ ] Task 4.3：修改 H5 订单确认页，区分核销模式/电商模式
- [ ] Task 4.4：H5 订单列表增加核销码显示（仅核销模式订单）

### Milestone 5：测试与验证

- [ ] Task 5.1：编写分润计算单元测试
- [ ] Task 5.2：编写核销码生成单元测试
- [ ] Task 5.3：执行消费者下单→确认→核销完整流程测试
- [ ] Task 5.4：执行店铺下单完整流程测试
- [ ] Task 5.5：验证钱包流水记录正确性

## 验收检查点

- [ ] 编译通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] Review 通过

## 下一步

执行 /harness-apply h5-order-payment-verification-20260421-01
