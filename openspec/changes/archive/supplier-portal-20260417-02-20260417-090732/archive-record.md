---
name: supplier-portal-20260417-02
archived: 2026-04-17
status: completed
---

# 归档记录：供应商门户

## 基本信息
- **change-id**: supplier-portal-20260417-02
- **创建时间**: 2026-04-17
- **完成时间**: 2026-04-17
- **归档时间**: 2026-04-17

## 需求摘要

供应商管理系统第一阶段已完成运营端内嵌的供应商档案、采购订单、入库和结算管理。但目前供应商无法自主查看订单、对账和收款信息，仍需通过人工沟通，导致：

1. 供应商无法实时查看采购订单状态
2. 对账需人工发送对账单，效率低
3. 供应商无法自主确认供货信息
4. 付款进度不透明，供应商频繁咨询

**核心目标**：
1. 建立供应商独立门户（Web 端）
2. 供应商可查看采购订单并确认/拒绝供货
3. 供应商可自主对账和查看结算进度
4. 供应商可维护企业资质和联系方式
5. 门户与运营端数据实时同步

## 技术方案摘要

在现有前端项目中内嵌供应商门户模块，通过路由区分（`/supplier-portal/`），供应商用户登录后自动进入门户。与运营端共享组件库和认证体系，后端新增供应商门户专用 API。

**数据模型变更**：
- Users 表扩展：supplier_id 字段
- PurchaseOrder 表扩展：supplier_confirm_status, supplier_confirmed_at
- 新增 PurchaseOrderAdjustment 表：订单调整申请

**接口设计**：
- 供应商门户 API：订单列表/详情/确认/申请修改、入库记录、结算记录、档案管理
- 运营端审批 API：修改申请列表/批准/拒绝

## 实现摘要

### 后端改动
- 新增 3 个 API 路由模块（supplier_portal, purchase_order_adjustments）
- 新增 1 个模型（PurchaseOrderAdjustment）
- 扩展 2 个模型（User, PurchaseOrder）
- 更新数据库初始化脚本

### 前端改动
- 新增 6 个 Vue 页面（Dashboard, Orders, OrderDetail, Inbounds, Settlements, Profile）
- 更新路由配置
- 更新主布局（供应商门户菜单）
- 更新登录逻辑（供应商自动跳转门户）

### 评审结论
- **通过** - 无严重问题
- 建议：数据库层面添加 CHECK 约束加强数据隔离
- 建议：批准修改申请后添加通知机制

## 变更文件清单

### 新增文件（9 个）
- `backend/app/models/purchase_order_adjustment.py`
- `backend/app/api/v1/supplier_portal.py`
- `backend/app/api/v1/purchase_order_adjustments.py`
- `frontend/src/views/supplier/Dashboard.vue`
- `frontend/src/views/supplier/Orders.vue`
- `frontend/src/views/supplier/OrderDetail.vue`
- `frontend/src/views/supplier/Inbounds.vue`
- `frontend/src/views/supplier/Settlements.vue`
- `frontend/src/views/supplier/Profile.vue`

### 修改文件（7 个）
- `backend/app/models/user.py`
- `backend/app/models/purchase_order.py`
- `backend/app/models/__init__.py`
- `backend/scripts/init_db.py`
- `backend/app/api/v1/api.py`
- `frontend/src/router/index.ts`
- `frontend/src/layouts/MainLayout.vue`
- `frontend/src/views/Login.vue`

## 验证结果
- 数据库初始化：通过（新表 purchase_order_adjustments 创建成功）
- 后端模块导入：通过
- 前端构建：通过（无错误）

## 评审知识捕获
1. [standards/database.md] 供应商数据隔离完全依赖应用层过滤，建议数据库层面添加 CHECK 约束
2. [implicit-contracts.md] 批准修改申请后订单状态重置为待确认，允许供应商重新确认
