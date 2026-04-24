---
name: shop-location-20260423-01
status: designed
---

# 技术方案：店铺地图定位配置与查看

## 方案概述

为店铺增加地图坐标属性，管理员可在运营端配置店铺坐标，H5 端用户可查看附近店铺。

## 详细设计

### 架构变更

| 模块 | 变更内容 |
|------|----------|
| `backend/app/models/shop.py` | 新增 `latitude`、`longitude` 字段 |
| `backend/app/api/v1/shops.py` | 返回店铺列表时增加坐标字段，支持更新坐标 |
| `frontend/src/views/Shops.vue` | 编辑弹窗增加地图选点组件 |
| `h5/src/views/Profile.vue` | 新增"查看附近的店铺"菜单 |
| `h5/src/views/NearbyShops.vue` | 新建地图页面组件 |

### 数据模型变更

```sql
ALTER TABLE shops 
ADD COLUMN latitude DECIMAL(10, 8) NULL COMMENT '店铺纬度',
ADD COLUMN longitude DECIMAL(11, 8) NULL COMMENT '店铺经度';
```

### 接口变更

- `GET /shops`：响应增加 `latitude`、`longitude` 字段
- `PUT /shops/{id}`：请求体增加 `latitude`、`longitude` 参数

### 前端依赖

- H5 端新增：`@amap/amap-jsapi-loader`（高德地图 JS API）
- B 端新增：`@amap/amap-jsapi-loader`（高德地图 JS API）

## 影响范围

- 受影响模块：店铺管理（B 端）、个人中心（H5 端）
- 受保护路径变更：无
- 向后兼容性：坐标字段为可空，不影响现有数据

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 用户拒绝位置权限 | 中 | 提示用户开启权限，提供手动输入城市选项 |
| 高德 API Key 配额限制 | 低 | 个人版 5 万次/天，测试足够，生产需升级 |
| 坐标数据缺失 | 低 | 字段允许为空，无坐标店铺不显示在地图上 |

## 事务与数据

- 事务边界：店铺坐标更新与店铺信息更新在同一事务中
- 数据迁移：无需迁移，现有店铺坐标为 NULL
- 回滚方案：直接回滚数据库变更即可

## 测试策略

1. B 端店铺坐标配置功能测试
2. H5 端位置权限请求测试
3. 距离计算准确性测试
4. 地图标记点击交互测试
