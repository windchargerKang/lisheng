---
name: supplier-management-20260417-01
status: designed
---

# 技术方案：供应商管理

## 方案概述

在现有 Web 运营端内嵌供应商管理模块，实现供应商档案、采购订单、入库、结算全流程管理。采用简单模式：采购订单→直接入库→增加库存→现款结算。

## 详细设计

### 架构变更

```
┌─────────────────────────────────────────────────────────────┐
│                   Web 运营端 (Element Plus)                   │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ 供应商管理  │ 采购订单    │ 入库管理    │ 结算管理    │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ API (新增后端模块)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                   Python FastAPI 后端                        │
│  ┌─────────────┬─────────────┬─────────────┐                │
│  │ 供应商 API  │ 采购订单 API │ 入库 API    │                │
│  │ 结算 API    │ 产品扩展     │             │                │
│  └─────────────┴─────────────┴─────────────┘                │
└─────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                     SQLite 数据库                            │
│  ┌──────────┬──────────┬──────────┬──────────┐              │
│  │suppliers │purchase_ │purchase_ │ settlement│              │
│  │          │orders    │inbounds  │          │              │
│  └──────────┴──────────┴──────────┴──────────┘              │
│  ┌──────────┬──────────┬──────────┬──────────┐              │
│  │purchase_ │          │          │          │              │
│  │items     │          │          │          │              │
│  └──────────┴──────────┴──────────┴──────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### 数据模型变更

#### Supplier (供应商表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 供应商名称 |
| credit_code | VARCHAR(50) | 统一社会信用代码 |
| contact_name | VARCHAR(50) | 联系人 |
| contact_phone | VARCHAR(20) | 联系电话 |
| address | VARCHAR(255) | 地址 |
| bank_name | VARCHAR(100) | 开户行 |
| bank_account | VARCHAR(50) | 银行账号 |
| settlement_type | VARCHAR(20) | 结算方式 (cash/credit) |
| status | VARCHAR(20) | 状态 (active/inactive) |
| created_at | DATETIME | 创建时间 |

#### PurchaseOrder (采购订单表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_no | VARCHAR(32) | 订单号（唯一） |
| supplier_id | INTEGER | 供应商 ID |
| purchaser_id | INTEGER | 采购员 ID |
| total_amount | DECIMAL(10,2) | 订单总额 |
| status | VARCHAR(20) | pending/confirmed/completed/cancelled |
| remark | VARCHAR(255) | 备注 |
| created_at | DATETIME | 创建时间 |
| confirmed_at | DATETIME | 确认时间 |

#### PurchaseOrderItem (采购明细表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_id | INTEGER | 订单 ID |
| product_id | INTEGER | 产品 ID |
| quantity | INTEGER | 采购数量 |
| cost_price | DECIMAL(10,2) | 采购单价 |
| subtotal | DECIMAL(10,2) | 小计 |

#### PurchaseInbound (入库记录表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_id | INTEGER | 订单 ID |
| warehouse_operator_id | INTEGER | 入库操作人 ID |
| total_quantity | INTEGER | 入库总数量 |
| status | VARCHAR(20) | completed |
| created_at | DATETIME | 入库时间 |

#### Settlement (结算记录表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| supplier_id | INTEGER | 供应商 ID |
| order_id | INTEGER | 关联订单 ID |
| amount | DECIMAL(10,2) | 结算金额 |
| type | VARCHAR(20) | cash (现款) |
| status | VARCHAR(20) | paid |
| paid_at | DATETIME | 付款时间 |
| created_at | DATETIME | 创建时间 |

### 产品模型扩展

Product 表增加字段：
- `supplier_id` INTEGER - 关联供应商 ID
- `cost_price` DECIMAL(10,2) - 采购成本价

### 接口设计

#### 供应商 API
- `GET /api/v1/suppliers` - 供应商列表
- `POST /api/v1/suppliers` - 创建供应商
- `GET /api/v1/suppliers/{id}` - 供应商详情
- `PUT /api/v1/suppliers/{id}` - 更新供应商
- `DELETE /api/v1/suppliers/{id}` - 删除供应商

#### 采购订单 API
- `GET /api/v1/purchase-orders` - 采购订单列表
- `POST /api/v1/purchase-orders` - 创建采购订单
- `GET /api/v1/purchase-orders/{id}` - 订单详情
- `PUT /api/v1/purchase-orders/{id}/confirm` - 确认订单
- `POST /api/v1/purchase-orders/{id}/cancel` - 取消订单

#### 入库 API
- `POST /api/v1/purchase-orders/{id}/inbound` - 采购入库
- `GET /api/v1/purchase-inbounds` - 入库记录列表

#### 结算 API
- `GET /api/v1/settlements` - 结算记录列表
- `POST /api/v1/settlements` - 创建结算（入库后自动）

## 影响范围

- **受影响模块**：
  - 后端：新增供应商、采购订单、入库、结算 API
  - 前端：Web 运营端新增 4 个管理页面
  - 数据模型：新增 5 个表，扩展 Product 模型

- **受保护路径变更**：无

- **向后兼容性**：
  - 新增 API 不影响现有渠道销售功能
  - Product 模型扩展字段为 nullable，不影响现有数据

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 库存并发更新 | 中 | 使用数据库事务 + 乐观锁 |
| 采购价与成本价不一致 | 低 | 明确 cost_price 为移动平均成本 |
| 结算重复付款 | 中 | 订单与结算一对一关联 |
| 删除供应商导致历史数据丢失 | 低 | 外键 RESTRICT，先检查关联 |

## 事务与数据

- **事务边界**：
  - 入库操作：更新库存 + 创建入库记录 + 创建结算记录
  - 创建采购订单：订单项 + 订单头

- **数据迁移**：
  - 现有 Product 数据无需迁移
  - supplier_id 和 cost_price 允许 NULL，逐步补充

- **回滚方案**：
  - 使用 Alembic 管理数据库变更
  - 删除操作前检查外键关联

## 测试策略

1. **单元测试**：
   - 入库时库存更新逻辑
   - 结算金额计算
   - 订单状态机转换

2. **集成测试**：
   - 供应商 CRUD API
   - 采购订单完整流程 API
   - 入库 API

3. **端到端测试**：
   - 创建供应商→创建订单→入库→结算完整流程
   - 运营端页面操作测试
