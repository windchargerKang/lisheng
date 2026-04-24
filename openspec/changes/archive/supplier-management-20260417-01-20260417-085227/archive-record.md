---
name: supplier-management-20260417-01
archived: 2026-04-17
status: completed
---

# 归档记录：供应商管理系统

## 基本信息
- **change-id**: supplier-management-20260417-01
- **创建时间**: 2026-04-17
- **完成时间**: 2026-04-17
- **归档时间**: 2026-04-17

## 需求摘要

随着业务规模扩大，公司需要管理多个供应商的采购、入库、结算等业务。目前系统缺少对上游供应商的管理能力，导致采购订单无法追踪、入库与库存数据不同步、供应商结算周期长等问题。

**核心目标**：
1. 建立供应商档案管理系统
2. 实现采购订单全流程管理（创建→入库→结算）
3. 与库存系统打通，自动更新库存
4. 提供供应商对账和结算功能

## 技术方案摘要

在现有 Web 运营端内嵌供应商管理模块，采用简单模式：采购订单→直接入库→增加库存→现款结算。

**数据模型**：
- Supplier (供应商表)
- PurchaseOrder + PurchaseOrderItem (采购订单表 + 明细表)
- PurchaseInbound (入库记录表)
- Settlement (结算记录表)

**接口设计**：
- 供应商 API: CRUD + 状态管理
- 采购订单 API: 列表/详情/创建/确认/取消
- 入库 API: 采购入库（自动增加库存 + 创建结算）
- 结算 API: 结算记录列表

## 实现摘要

### 后端改动
- 新增 6 个模型文件
- 新增 3 个 API 路由模块
- 扩展 Product 模型（supplier_id, cost_price）
- 更新数据库初始化脚本

### 前端改动
- 新增 5 个 Vue 页面（供应商/订单/详情/入库/结算）
- 更新路由配置
- 更新主布局菜单

### 评审结论
- **浮点数精度修复**: 入库成本计算从 `float` 改为 `Decimal`
- **入库回滚**: 确认不需要此功能

## 变更文件清单

### 新增文件（13 个）
- `backend/app/models/supplier.py`
- `backend/app/models/purchase_order.py`
- `backend/app/models/purchase_inbound.py`
- `backend/app/api/v1/suppliers.py`
- `backend/app/api/v1/purchase_orders.py`
- `backend/app/api/v1/purchase_inbounds.py`
- `backend/app/models/cart.py`
- `backend/app/models/order.py`
- `backend/app/models/profit.py`
- `backend/app/models/referral.py`
- `backend/app/api/v1/cart.py`
- `backend/app/api/v1/orders.py`
- `backend/app/api/v1/profit.py`
- `backend/app/api/v1/referral.py`
- `frontend/src/views/Suppliers.vue`
- `frontend/src/views/PurchaseOrders.vue`
- `frontend/src/views/PurchaseOrderDetail.vue`
- `frontend/src/views/Inbounds.vue`
- `frontend/src/views/Settlements.vue`

### 修改文件（11 个）
- `backend/app/models/__init__.py`
- `backend/app/models/product.py`
- `backend/app/api/v1/api.py`
- `backend/app/api/v1/__init__.py`
- `backend/app/api/v1/regions.py`
- `backend/app/api/v1/shops.py`
- `backend/app/api/v1/agents.py`
- `backend/app/api/v1/auth.py`
- `backend/app/schemas/auth.py`
- `backend/scripts/init_db.py`
- `frontend/src/router/index.ts`
- `frontend/src/layouts/MainLayout.vue`
- `frontend/package.json`

## 验证结果
- 数据库初始化：通过（5 张新表创建成功）
- 后端模块导入：通过
- 前端构建：通过（1688 模块，无错误）
