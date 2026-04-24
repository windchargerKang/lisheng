---
name: supplier-portal-20260417-02
status: designed
---

# 技术方案：供应商门户

## 方案概述

在现有前端项目中内嵌供应商门户模块，通过路由区分（`/supplier-portal/`），供应商用户登录后自动进入门户。与运营端共享组件库和认证体系，后端新增供应商门户专用 API。

## 详细设计

### 架构变更

```
┌─────────────────────────────────────────────────────────────┐
│                   前端 (Element Plus)                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  运营端 / 供应商门户 (同一项目，路由区分)               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │ 订单管理    │  │ 对账管理    │  │ 档案管理    │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ API (JWT 认证，角色区分)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                   Python FastAPI 后端                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  供应商门户 API (/api/v1/supplier-portal/)           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 数据模型变更

#### Users 表扩展
| 字段 | 类型 | 说明 |
|------|------|------|
| supplier_id | INTEGER | 关联供应商 ID（nullable，仅供应商角色需要） |

#### PurchaseOrder 表扩展
| 字段 | 类型 | 说明 |
|------|------|------|
| supplier_confirmed_at | DATETIME | 供应商确认时间 |
| supplier_status | VARCHAR(20) | 供应商确认状态（pending/confirmed/rejected） |

#### 新增 PurchaseOrderAdjustment 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_id | INTEGER | 订单 ID |
| supplier_id | INTEGER | 供应商 ID |
| reason | VARCHAR(500) | 修改原因 |
| adjustment_items | TEXT | 调整明细（JSON） |
| status | VARCHAR(20) | 状态（pending/approved/rejected） |
| created_at | DATETIME | 创建时间 |

### 接口设计

#### 供应商门户 API
- `GET /api/v1/supplier-portal/orders` - 我的订单列表
- `GET /api/v1/supplier-portal/orders/{id}` - 订单详情
- `POST /api/v1/supplier-portal/orders/{id}/confirm` - 确认供货
- `POST /api/v1/supplier-portal/orders/{id}/reject` - 申请修改
- `GET /api/v1/supplier-portal/inbounds` - 入库记录
- `GET /api/v1/supplier-portal/settlements` - 结算记录
- `GET /api/v1/supplier-portal/profile` - 供应商档案
- `PUT /api/v1/supplier-portal/profile` - 更新档案

#### 运营端 API 扩展
- `GET /api/v1/purchase-orders/{id}/adjustments` - 查看修改申请
- `POST /api/v1/purchase-orders/{id}/adjustments/approve` - 批准修改
- `POST /api/v1/purchase-orders/{id}/adjustments/reject` - 拒绝修改

### 前端页面

**供应商门户页面**（路由 `/supplier-portal/`）：
1. `Dashboard.vue` - 门户首页/仪表盘
2. `Orders.vue` - 订单列表
3. `OrderDetail.vue` - 订单详情/确认
4. `Inbounds.vue` - 入库记录
5. `Settlements.vue` - 结算记录
6. `Profile.vue` - 档案管理

## 影响范围

- **受影响模块**：
  - 后端：新增供应商门户 API 模块，扩展 PurchaseOrder 模型
  - 前端：新增供应商门户页面，扩展路由和认证逻辑
  - 数据模型：扩展 Users 和 PurchaseOrder 表，新增 Adjustment 表

- **受保护路径变更**：无

- **向后兼容性**：
  - 新增 API 不影响现有功能
  - Users 和 PurchaseOrder 扩展字段为 nullable，不影响现有数据

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 供应商数据隔离 | 中 | 严格过滤，确保供应商只能查看自己的数据 |
| 订单确认并发 | 低 | 使用事务，确认状态变更时检查当前状态 |
| 修改申请滥用 | 低 | 限制申请次数，需填写详细原因 |

## 事务与数据

- **事务边界**：
  - 订单确认：更新 supplier_status + supplier_confirmed_at
  - 申请修改：创建 Adjustment 记录 + 更新订单状态

- **数据迁移**：
  - 现有供应商账号需由管理员创建并关联 supplier_id
  - 历史订单的 supplier_status 默认为 null

- **回滚方案**：
  - 使用 Alembic 管理数据库变更
  - 供应商确认操作可撤销（需运营端权限）

## 测试策略

1. **单元测试**：
   - 供应商数据隔离逻辑
   - 订单确认状态机转换
   - 修改申请流程

2. **集成测试**：
   - 供应商门户 API 完整流程
   - 运营端审批修改申请

3. **端到端测试**：
   - 供应商登录→查看订单→确认/申请修改→查看结算
   - 运营端收到申请→审批→供应商查看结果
