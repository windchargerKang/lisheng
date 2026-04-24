---
name: admin-order-shipment-20260420-03
status: completed
created: 2026-04-20
---

# 技术方案：运营管理端订单发货功能

## 方案概述

在现有运营管理端（frontend）实现订单发货功能，包括订单列表查看、订单详情和发货操作。通过扩展订单数据模型新增物流字段，实现从"待发货"到"已发货"的状态流转。

## 详细设计

### 架构变更

**后端新增/修改模块：**
| 模块 | 说明 |
|------|------|
| app/models/order.py | Order 模型新增物流字段 |
| app/api/v1/admin_orders.py | 管理端订单 API 路由 |
| app/schemas/order.py | 新增订单 Schema 定义 |
| app/api/v1/api.py | 注册 admin_orders router |

**前端新增页面（frontend）：**
| 页面 | 路径 | 说明 |
|------|------|------|
| OrderList.vue | /orders/list | 订单列表页（支持状态筛选） |
| OrderDetail.vue | /orders/detail | 订单详情页 |
| ShipDialog.vue | 组件 | 发货弹窗（物流公司 + 运单号） |

### 数据模型变更

**orders 表新增字段：**
```sql
ALTER TABLE orders ADD COLUMN courier_company VARCHAR(100) NULL;  -- 物流公司名称
ALTER TABLE orders ADD COLUMN courier_no VARCHAR(50) NULL;        -- 物流单号
ALTER TABLE orders ADD COLUMN shipped_at DATETIME NULL;           -- 发货时间
ALTER TABLE orders ADD COLUMN shipper_id INTEGER NULL;            -- 发货操作人 ID
```

**Order 模型扩展：**
```python
class Order(Base):
    # ... 现有字段 ...
    courier_company = Column(String(100), nullable=True)
    courier_no = Column(String(50), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    shipper_id = Column(Integer, ForeignKey("users.id"), nullable=True)
```

### 接口设计

**新增管理端 API 端点：**

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /api/v1/admin/orders | `order:view` | 订单列表（支持状态筛选、分页） |
| GET | /api/v1/admin/orders/{id} | `order:view` | 订单详情 |
| POST | /api/v1/admin/orders/{id}/ship | `order:ship` | 发货操作 |

**发货 API 请求体：**
```json
{
  "courier_company": "顺丰速运",
  "courier_no": "SF1234567890"
}
```

**发货 API 响应：**
```json
{
  "id": 123,
  "order_no": "ORD20260420123456",
  "status": "shipped",
  "courier_company": "顺丰速运",
  "courier_no": "SF1234567890",
  "shipped_at": "2026-04-20T10:30:00Z"
}
```

### 前端路由配置

```typescript
{
  path: '/orders',
  name: 'Orders',
  redirect: '/orders/list',
  children: [
    {
      path: 'list',
      name: 'OrderList',
      component: () => import('@/views/orders/List.vue'),
      meta: { title: '订单管理', requiresAuth: true }
    },
    {
      path: 'detail/:id',
      name: 'OrderDetail',
      component: () => import('@/views/orders/Detail.vue'),
      meta: { title: '订单详情', requiresAuth: true }
    }
  ]
}
```

## 影响范围

### 受影响模块
- 后端：Order 模型扩展、新增 admin_orders 路由
- 前端：新增订单管理页面和组件
- 数据库：orders 表结构变更

### 受保护路径变更
- 无（不涉及配置文件、部署脚本等）

### 向后兼容性
- 新增字段为 nullable，不影响现有数据
- 新增 API 端点不影响现有 H5 端接口

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 物流字段长度不足 | 低 | courier_company 设为 100，courier_no 设为 50 |
| 并发发货操作 | 低 | 订单状态机控制，只有 confirmed 状态可发货 |
| 权限配置遗漏 | 中 | 初始化脚本自动创建权限和角色 |

## 事务与数据

### 事务边界
- 发货操作：更新订单状态 + 物流信息 + 发货时间 + 操作人（同一事务）

### 数据迁移
```sql
-- 执行 migrations/004_add_order_shipment.sql
ALTER TABLE orders ADD COLUMN courier_company VARCHAR(100) NULL;
ALTER TABLE orders ADD COLUMN courier_no VARCHAR(50) NULL;
ALTER TABLE orders ADD COLUMN shipped_at DATETIME NULL;
ALTER TABLE orders ADD COLUMN shipper_id INTEGER NULL;
```

### 回滚方案
- 删除新增的 4 个字段（需先备份数据）

## 测试策略

1. **后端测试**
   - 订单列表 API 测试（分页、筛选）
   - 发货 API 测试（状态转换验证）
   - 权限验证（只有管理员可发货）

2. **前端测试**
   - 订单列表渲染和筛选
   - 发货弹窗交互
   - 发货后列表刷新

3. **集成测试**
   - 完整流程：用户下单 → 用户确认 → 管理员发货 → 用户确认收货
