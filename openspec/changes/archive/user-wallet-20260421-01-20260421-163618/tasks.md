---
name: user-wallet-20260421-01
status: planned
---

# 执行任务：用户钱包系统

## 任务列表

### Milestone 1：数据模型与迁移
- [ ] Task 1.1：创建 Wallet 数据模型（backend/app/models/wallet.py）
- [ ] Task 1.2：创建 WalletTransaction 数据模型（backend/app/models/wallet_transaction.py）
- [ ] Task 1.3：更新 models/__init__.py 导出新模型
- [ ] Task 1.4：创建数据库迁移脚本（backend/migrations/008_add_wallet_tables.sql）
- [ ] Task 1.5：执行迁移并验证表结构

### Milestone 2：Service 层业务逻辑
- [ ] Task 2.1：创建 WalletService 服务类（backend/app/services/wallet_service.py）
- [ ] Task 2.2：实现 get_wallet_by_user_id 方法
- [ ] Task 2.3：实现 create_wallet 方法（用户注册时自动创建）
- [ ] Task 2.4：实现 recharge 方法（充值，含事务）
- [ ] Task 2.5：实现 withdraw 方法（提现申请，含事务）
- [ ] Task 2.6：实现 approve_withdraw 方法（审核提现，含事务）
- [ ] Task 2.7：实现 get_transactions 方法（查询流水）
- [ ] Task 2.8：实现 generate_transaction_no 方法（流水号生成）

### Milestone 3：Schema 定义
- [ ] Task 3.1：创建钱包 Schema（backend/app/schemas/wallet.py）
- [ ] Task 3.2：定义 WalletResponse、WalletTransactionResponse
- [ ] Task 3.3：定义 RechargeRequest、WithdrawRequest、ApproveWithdrawRequest

### Milestone 4：API 路由实现
- [ ] Task 4.1：创建钱包 API 路由（backend/app/api/v1/wallet.py）
- [ ] Task 4.2：实现 GET /wallet - 查询当前用户钱包
- [ ] Task 4.3：实现 POST /wallet/recharge - 管理员充值
- [ ] Task 4.4：实现 POST /wallet/withdraw - 用户提现申请
- [ ] Task 4.5：实现 POST /wallet/withdraw/{id}/approve - 管理员审核提现
- [ ] Task 4.6：实现 GET /wallet/transactions - 查询用户流水
- [ ] Task 4.7：实现 GET /admin/wallets - 管理员查看所有钱包
- [ ] Task 4.8：实现 GET /admin/wallet-transactions - 管理员查看所有流水
- [ ] Task 4.9：注册路由到 api.py

### Milestone 5：用户注册自动创建钱包
- [ ] Task 5.1：修改用户注册接口，调用 WalletService.create_wallet
- [ ] Task 5.2：为现有用户批量初始化钱包（数据迁移脚本）

### Milestone 6：测试与验证
- [ ] Task 6.1：编写 WalletService 单元测试
- [ ] Task 6.2：编写钱包 API 集成测试
- [ ] Task 6.3：手动验证完整流程（注册→充值→提现→审核）
- [ ] Task 6.4：验证并发提现场景（余额检查）

## 验收检查点
- [ ] 编译通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] Review 通过

## 下一步
执行 /harness-apply user-wallet-20260421-01
