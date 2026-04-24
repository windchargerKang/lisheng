---
name: h5-order-payment-verification-20260421-01
status: designed
---

# 技术方案：H5 端订单支付与核销流程

## 方案概述

实现两套订单资金流程：
1. **核销模式**：消费者下单 → 钱包支付 → 生成核销码 → 店铺核销 → 分润结算
2. **电商模式**：店铺/区代下单 → 钱包支付 → 订单正常流转 → 不涉及核销

## 详细设计

### 架构变更

| 模块 | 变更内容 |
|------|----------|
| `backend/app/models/order.py` | 新增 `order_type`、`verification_code`、`verified_at` 字段；OrderStatus 新增 `verified` |
| `backend/app/models/wallet_transaction.py` | TransactionType 新增 `ORDER_PAYMENT`、`SERVICE_FEE`、`AGENT_PROFIT` |
| `backend/app/models/verification_code.py` | **新增** 核销码模型 |
| `backend/app/services/order_service.py` | **新增** 订单服务（处理下单、支付、核销） |
| `backend/app/services/profit_service.py` | **新增** 分润服务（计算和分发分润） |
| `backend/app/api/v1/orders.py` | 扩展下单、确认订单接口；新增核销接口 |
| `backend/app/api/v1/verification.py` | **新增** 核销 API 路由 |
| `backend/config.json` | **新增** 分润比例配置 |
| `h5/src/views/Verification.vue` | **新增** H5 店铺核销页面 |
| `h5/src/router/index.ts` | 增加核销页面路由 |

### 数据模型变更

#### 1. Order 表变更

```python
class OrderType(str, enum.Enum):
    VERIFICATION = "verification"  # 核销模式
    ECOMMERCE = "ecommerce"        # 电商模式

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    VERIFIED = "verified"      # 新增：已核销
    CANCELLED = "cancelled"
    PAID = "paid"

class Order(Base):
    # 新增字段
    order_type = Column(String(20), nullable=False, default="ecommerce")
    verified_at = Column(DateTime(timezone=True), nullable=True)  # 核销时间

    # 关联：verification_code (通过 VerificationCode 表关联)
```

#### 2. WalletTransaction 枚举变更

```python
class TransactionType(str, enum.Enum):
    RECHARGE = "RECHARGE"
    WITHDRAW = "WITHDRAW"
    ORDER_PAYMENT = "ORDER_PAYMENT"      # 新增：订单支付
    SERVICE_FEE = "SERVICE_FEE"          # 新增：服务费返还
    AGENT_PROFIT = "AGENT_PROFIT"        # 新增：区代利润
```

#### 3. 新增 VerificationCode 表

```python
class VerificationCodeStatus(str, enum.Enum):
    UNUSED = "unused"
    USED = "used"

class VerificationCode(Base):
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(12), unique=True, index=True, nullable=False)  # 12 位核销码
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    status = Column(Enum(VerificationCodeStatus), nullable=False, default=VerificationCodeStatus.UNUSED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 核销店铺 user_id
    
    # 关联
    order = relationship("Order", backref="verification_code")
    verifier = relationship("User", foreign_keys=[verified_by])
```

### 接口变更

#### 1. POST /orders/create (扩展)

**请求**：
```json
{
  "cart_item_ids": [1, 2, 3],
  "receiver_name": "张三",
  "receiver_phone": "13800138000",
  "receiver_address": "xxx"
}
```

**变更**：
- 根据当前用户 `role_type` 自动设置 `order_type`
- `customer` → `verification`（生成核销码）
- `shop`/`agent` → `ecommerce`（不生成核销码）

#### 2. POST /orders/{order_id}/confirm (扩展)

**功能**：用户确认订单，触发钱包扣款

**流程**：
1. 检查订单状态为 `pending`
2. 检查用户钱包余额充足
3. 用户钱包 `-订单金额`（ORDER_PAYMENT）
4. lisheng 钱包 `+订单金额`（ORDER_PAYMENT）
5. 订单状态 → `completed`
6. 如果是核销模式订单，生成核销码

#### 3. POST /verification/verify (新增)

**请求**：
```json
{
  "verification_code": "123456789012"
}
```

**响应**：
```json
{
  "message": "核销成功",
  "order_id": 123,
  "service_fee": 30.00,
  "agent_profit": 10.00
}
```

**流程**：
1. 验证核销码有效且未使用
2. 获取订单和店铺信息
3. 计算分润（服务费 30%，区代利润 10%）
4. lisheng 钱包 `-服务费` → 店铺钱包 `+ 服务费`（SERVICE_FEE）
5. lisheng 钱包 `-区代利润` → 区代钱包 `+ 区代利润`（AGENT_PROFIT）
6. 订单状态 → `verified`
7. 核销码状态 → `used`

### 分润配置

**backend/config.json**（新建）：
```json
{
  "profit": {
    "service_fee_rate": 0.30,
    "agent_profit_rate": 0.10
  },
  "system_account": {
    "username": "lisheng"
  }
}
```

## 影响范围

- 受影响模块：订单、钱包、核销、分润
- 受保护路径变更：无
- 向后兼容性：现有订单接口保持兼容，新增字段有默认值

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 并发核销导致重复分润 | 高 | 核销码表加唯一索引，事务中检查状态 |
| lisheng 账号余额不足导致分润失败 | 中 | 核销前检查余额，不足时提示并暂停核销 |
| 核销码生成冲突 | 低 | 12 位随机数字 + 唯一索引，冲突时重试 |
| 分润计算精度问题 | 中 | 使用 Decimal 类型，四舍五入到分 |

## 事务与数据

### 事务边界

1. **下单事务**：创建订单 + 订单项（核销码在支付完成后生成）
2. **确认订单事务**：钱包扣款 + 订单状态更新 + 核销码生成（仅核销模式）
3. **核销事务**：分润转账 + 订单状态更新 + 核销码状态更新

### 数据迁移

- 历史订单 `order_type` 默认为 `ecommerce`
- 历史订单 `verification_code` 为 `NULL`
- 无需迁移历史数据

### 回滚方案

- 核销失败时，事务自动回滚
- 分润失败时，保持订单状态为 `completed`，支持手动重试

## 测试策略

1. **单元测试**：
   - 分润计算逻辑
   - 核销码生成逻辑
   - 订单状态机转换

2. **集成测试**：
   - 消费者下单 → 确认 → 核销完整流程
   - 店铺下单 → 确认 → 发货 → 完成流程
   - 并发核销场景

3. **验证方式**：
   - H5 端手动测试消费者下单和核销
   - 检查钱包流水记录
   - 检查订单状态变化
