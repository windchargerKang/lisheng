---
name: user-wallet-20260421-01
status: designed
---

# 技术方案：用户钱包系统

## 方案概述

为系统所有用户创建钱包账户，支持管理员手动充值和用户提现申请功能。采用 DECIMAL(10,2) 存储余额（单位：元），流水号采用可读性好的格式（R/W+ 日期 + 序号），提现采用一级审核流程。

## 详细设计

### 架构变更

**新增模块：**
- `backend/app/models/wallet.py` - 钱包数据模型
- `backend/app/models/wallet_transaction.py` - 钱包流水数据模型
- `backend/app/api/v1/wallet.py` - 钱包 API 路由
- `backend/app/schemas/wallet.py` - 钱包请求/响应 Schema
- `backend/app/services/wallet_service.py` - 钱包业务逻辑层

**修改模块：**
- `backend/app/models/user.py` - 添加钱包关系
- `backend/app/models/__init__.py` - 导出新模型
- `backend/app/api/v1/api.py` - 注册钱包路由
- `backend/app/services/__init__.py` - 导出服务

### 数据模型变更

**Wallet 表：**
```sql
CREATE TABLE wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**WalletTransaction 表：**
```sql
CREATE TABLE wallet_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,  -- RECHARGE/WITHDRAW
    amount DECIMAL(10,2) NOT NULL,
    balance_after DECIMAL(10,2) NOT NULL,
    transaction_no VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL,  -- PENDING/APPROVED/REJECTED/COMPLETED
    withdraw_method VARCHAR(50),  -- 银行卡/支付宝/微信
    withdraw_account VARCHAR(100),
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wallet_id) REFERENCES wallets(id)
);
```

**索引：**
- `idx_wallets_user_id` - user_id 唯一索引
- `idx_transactions_wallet_id` - wallet_id 索引
- `idx_transactions_transaction_no` - transaction_no 唯一索引
- `idx_transactions_status` - status 索引

### 接口变更

| 接口 | 方法 | 权限 | 描述 |
|------|------|------|------|
| `/wallet` | GET | 登录用户 | 查询当前用户钱包余额 |
| `/wallet/recharge` | POST | 管理员 | 管理员手动充值 |
| `/wallet/withdraw` | POST | 登录用户 | 申请提现 |
| `/wallet/withdraw/{id}/approve` | POST | 管理员 | 审核提现申请 |
| `/wallet/transactions` | GET | 登录用户 | 查询用户流水记录 |
| `/admin/wallets` | GET | 管理员 | 查看所有用户钱包（分页） |
| `/admin/wallet-transactions` | GET | 管理员 | 查看所有流水记录（分页） |

### 流水号生成规则

格式：`{类型前缀}{YYYYMMDD}{4 位序号}`

- 充值：`R202604210001`
- 提现：`W202604210001`

序号按天重置，通过查询当日已有流水数 +1 生成。

## 影响范围

- 受影响模块：用户模块、新增钱包模块
- 受保护路径变更：无
- 向后兼容性：兼容 - 新增功能不影响现有接口

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 并发提现导致余额超扣 | 高 | 使用数据库行锁 + 事务，检查余额时加 FOR UPDATE |
| 流水号生成冲突 | 中 | 使用数据库唯一约束，冲突时重试 |
| 事务不一致（余额与流水不同步） | 高 | 所有操作在同一事务中完成 |
| 用户注册时钱包创建失败 | 中 | 使用 SQLAlchemy 事件或 Service 层统一处理，失败时回滚 |

## 事务与数据

- **事务边界**：充值、提现申请、审核操作均需在单事务中完成（钱包余额更新 + 流水记录）
- **数据迁移**：为现有用户批量初始化钱包（余额为 0）
- **回滚方案**：操作失败时事务自动回滚，无需额外处理

## 测试策略

1. **单元测试**：
   - WalletService 充值逻辑测试
   - WalletService 提现逻辑测试
   - WalletService 审核逻辑测试
   - 流水号生成测试

2. **集成测试**：
   - 充值 API 测试
   - 提现 API 测试
   - 审核 API 测试
   - 余额不足提现测试
   - 并发提现测试

3. **验证方式**：
   - 手动创建用户验证钱包自动创建
   - 手动调用 API 验证充值/提现流程
   - 检查数据库余额与流水记录一致性
