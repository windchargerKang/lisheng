---
name: h5-user-end-20260416-01
status: designed
---

# 技术方案：H5 用户端

## 方案概述

H5 用户端采用 Vue 3 + Vant 4 技术栈，与 Web 运营端同站点不同路径部署。实现用户登录、产品浏览、购物车、订单、收益、分享六大功能模块。

## 详细设计

### 架构变更

```
┌─────────────────────────────────────────────────────────────┐
│                      H5 用户端                               │
│              (Vue 3 + Vant 4 + Pinia)                        │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐        │
│  │ 用户模块 │ 产品模块 │ 购物车  │ 订单模块 │ 收益模块 │        │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘        │
│  ┌─────────┬─────────┐                                        │
│  │ 分享模块 │ 个人中心 │                                        │
│  └─────────┴─────────┘                                        │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ API (复用 + 扩展后端)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                   Python FastAPI 后端                        │
│  ┌─────────────┬─────────────┬─────────────┐                │
│  │ 订单模块    │ 购物车模块  │ 收益模块     │                │
│  │ 分享追踪    │ 产品扩展    │ 用户扩展     │                │
│  └─────────────┴─────────────┴─────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### 数据模型变更

#### Order (订单主表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_no | VARCHAR(32) | 订单号（唯一） |
| user_id | INTEGER | 用户 ID |
| total_amount | DECIMAL(10,2) | 订单总额 |
| status | VARCHAR(20) | pending/confirmed/shipped/completed/cancelled |
| created_at | DATETIME | 创建时间 |

#### OrderItem (订单明细表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_id | INTEGER | 订单 ID |
| product_id | INTEGER | 产品 ID |
| quantity | INTEGER | 数量 |
| unit_price | DECIMAL(10,2) | 单价 |
| subtotal | DECIMAL(10,2) | 小计 |

#### CartItem (购物车项表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户 ID |
| product_id | INTEGER | 产品 ID |
| quantity | INTEGER | 数量 |
| created_at | DATETIME | 添加时间 |

#### ProfitRecord (分润记录表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户 ID |
| order_id | INTEGER | 订单 ID |
| amount | DECIMAL(10,2) | 分润金额 |
| status | VARCHAR(20) | pending/paid/withdrawn |
| created_at | DATETIME | 创建时间 |

#### WithdrawalRequest (提现申请表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户 ID |
| amount | DECIMAL(10,2) | 提现金额 |
| status | VARCHAR(20) | pending/approved/rejected |
| created_at | DATETIME | 申请时间 |

#### Referral (分享追踪表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| referrer_id | INTEGER | 推荐人 ID |
| referee_id | INTEGER | 被推荐人 ID |
| referrer_type | VARCHAR(20) | customer/shop/agent |
| created_at | DATETIME | 绑定时间 |

### 接口设计

#### 购物车 API
- `GET /api/v1/cart` - 获取购物车列表
- `POST /api/v1/cart/items` - 添加到购物车
- `PUT /api/v1/cart/items/:id` - 修改数量
- `DELETE /api/v1/cart/items/:id` - 删除购物车项

#### 订单 API
- `GET /api/v1/orders` - 订单列表（分页、状态筛选）
- `POST /api/v1/orders` - 创建订单
- `GET /api/v1/orders/:id` - 订单详情
- `POST /api/v1/orders/:id/confirm` - 确认订单
- `POST /api/v1/orders/:id/cancel` - 取消订单

#### 收益 API
- `GET /api/v1/profit/summary` - 收益总览
- `GET /api/v1/profit/records` - 收益明细
- `POST /api/v1/withdrawals` - 提现申请
- `GET /api/v1/withdrawals` - 提现记录

#### 分享 API
- `GET /api/v1/referral/code` - 获取分享码/链接
- `GET /api/v1/referral/stats` - 分享统计
- `GET /api/v1/referral/list` - 下级列表

### 影响范围

- **受影响模块**：新增 H5 前端、订单/购物车/收益/分享后端模块
- **受保护路径变更**：无
- **向后兼容性**：复用第一阶段 API，新增 API 不影响现有功能

### 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 移动端适配问题 | 中 | 使用 Vant 组件库，真机测试 |
| 分润计算复杂 | 高 | 独立 Service 层，充分单元测试 |
| 分享链接微信拦截 | 中 | 提供二维码备选方案 |
| 购物车并发问题 | 中 | 使用数据库事务 |

### 事务与数据

- **事务边界**：订单创建、分润分配使用事务
- **数据迁移**：无历史数据迁移
- **回滚方案**：数据库变更使用 Alembic 管理

### 测试策略

1. **单元测试**：Service 层业务逻辑（分润计算、订单状态机）
2. **集成测试**：API 端点测试
3. **E2E 测试**：核心购物流程（浏览→加购→下单）
4. **移动端测试**：主流机型适配测试
