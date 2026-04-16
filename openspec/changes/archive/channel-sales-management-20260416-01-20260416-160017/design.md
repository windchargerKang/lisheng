---
name: channel-sales-management-20260416-01
status: designed
---

# 技术方案：渠道客户管理系统

## 方案概述

本系统采用模块化 Python FastAPI 后端 + Vue 3 双前端架构，分润引擎独立设计。

**第一阶段范围**：Web 运营端基础框架，包括用户认证、区域管理、店铺管理、区代管理、产品管理。

## 详细设计

### 架构变更

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                                │
├─────────────────────────┬───────────────────────────────────┤
│   H5 用户端             │      Web 运营端                   │
│   Vue 3 + Vant 4        │      Vue 3 + Element Plus         │
│   (后续阶段)            │      (第一阶段)                   │
└───────────┬─────────────┴─────────────────┬─────────────────┘
            │                               │
            └───────────┬───────────────────┘
                        │
            ┌───────────▼───────────────────┐
            │      Python FastAPI 后端      │
            │  ┌─────────┬─────────┬───────┤│
            │  │ 渠道模块 │ 产品模块 │用户  ││
            │  │ 订单模块 │ 分润引擎 │模块  ││
            │  └─────────┴─────────┴───────┘│
            └───────────────────────────────┘
                        │
            ┌───────────▼───────────────────┐
            │      MySQL / SQLite           │
            └───────────────────────────────┘
```

### 模块划分

| 模块 | 职责 | 第一阶段 |
|------|------|----------|
| 用户模块 | 认证、授权、角色管理 | ✓ |
| 渠道模块 | 客户/店铺/区代管理、区域树 | ✓ |
| 产品模块 | 产品管理、三级定价 | ✓ |
| 订单模块 | 订单创建、查询 | 后续 |
| 分润引擎 | 分润计算、分配、提现 | 后续 |

### 数据模型设计

#### User (用户表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名 |
| password_hash | VARCHAR(255) | 密码哈希 |
| role_type | VARCHAR(20) | customer/shop/agent/admin |
| created_at | DATETIME | 创建时间 |

#### Region (区域表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| parent_id | INTEGER | 父区域 ID（自关联） |
| name | VARCHAR(100) | 区域名称 |
| level | INTEGER | 层级（1=省，2=市，3=区，...） |
| path | VARCHAR(255) | 区域路径，如 "1/5/12" |

#### Shop (店铺表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 关联用户 ID |
| region_id | INTEGER | 所属区域 ID |
| referrer_id | INTEGER | 推荐店铺 ID |
| status | VARCHAR(20) | active/inactive |

#### Agent (区代表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 关联用户 ID |
| region_id | INTEGER | 管理的区域 ID（唯一） |
| referrer_id | INTEGER | 推荐区代 ID |
| status | VARCHAR(20) | active/inactive |

#### Product (产品表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 产品名称 |
| sku_code | VARCHAR(50) | SKU 编码 |
| status | VARCHAR(20) | active/inactive |

#### PriceTier (价格层级表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| product_id | INTEGER | 产品 ID |
| tier_type | VARCHAR(20) | retail/shop/agent |
| price | DECIMAL(10,2) | 价格 |
| updated_at | DATETIME | 更新时间 |

### 接口设计

#### 用户认证
- `POST /api/auth/login` - 登录
- `POST /api/auth/logout` - 登出
- `GET /api/auth/profile` - 获取当前用户信息

#### 区域管理
- `GET /api/regions` - 获取区域树
- `POST /api/regions` - 创建区域
- `PUT /api/regions/:id` - 更新区域
- `DELETE /api/regions/:id` - 删除区域

#### 店铺管理
- `GET /api/shops` - 店铺列表（分页、筛选）
- `POST /api/shops` - 创建店铺
- `PUT /api/shops/:id` - 更新店铺
- `GET /api/shops/:id` - 店铺详情

#### 区代管理
- `GET /api/agents` - 区代列表（分页、筛选）
- `POST /api/agents` - 创建区代
- `PUT /api/agents/:id` - 更新区代
- `GET /api/agents/:id` - 区代详情

#### 产品管理
- `GET /api/products` - 产品列表
- `POST /api/products` - 创建产品
- `PUT /api/products/:id` - 更新产品
- `POST /api/products/:id/prices` - 设置产品价格

## 影响范围

- **受影响模块**：新增用户、渠道、产品模块
- **受保护路径变更**：无（第一阶段不涉及配置修改）
- **向后兼容性**：N/A（新项目）

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 区域树设计过深影响性能 | 中 | 限制最大层级（如 5 级），使用 path 字段优化查询 |
| 渠道关系复杂导致数据不一致 | 中 | 使用事务，添加数据完整性校验 |
| 分润规则理解偏差 | 高 | 第一阶段不涉及，后续单独设计评审 |

## 事务与数据

- **事务边界**：每个 API 请求内的写操作使用事务
- **数据迁移**：第一阶段无历史数据迁移
- **回滚方案**：数据库变更使用 Alembic 管理，支持回滚

## 测试策略

1. **单元测试**：Service 层业务逻辑（分润计算除外）
2. **集成测试**：API 端点测试
3. **前端测试**：关键组件单元测试
4. **E2E 测试**：核心业务流程（后续阶段）
