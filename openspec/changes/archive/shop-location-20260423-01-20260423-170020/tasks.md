---
name: shop-location-20260423-01
status: planned
---

# 执行任务：店铺地图定位配置与查看

## 任务列表

### Milestone 1：数据库与后端 API 变更
- [ ] Task 1.1：修改 `backend/app/models/shop.py`，增加 `latitude`、`longitude` 字段
- [ ] Task 1.2：创建数据库迁移脚本（添加经纬度字段）
- [ ] Task 1.3：修改 `backend/app/api/v1/shops.py`，返回店铺列表时增加坐标字段
- [ ] Task 1.4：修改 `backend/app/api/v1/shops.py`，支持更新店铺坐标

### Milestone 2：运营端（B 端）地图选点功能
- [ ] Task 2.1：安装高德地图 JS API 依赖 `@amap/amap-jsapi-loader`
- [ ] Task 2.2：修改 `frontend/src/views/Shops.vue`，编辑弹窗增加地图选点组件
- [ ] Task 2.3：实现手动输入经纬度功能
- [ ] Task 2.4：实现地图点击选点功能（点击地图自动回填经纬度）

### Milestone 3：H5 端附近店铺功能
- [ ] Task 3.1：安装高德地图 JS API 依赖 `@amap/amap-jsapi-loader`
- [ ] Task 3.2：修改 `h5/src/views/Profile.vue`，增加"查看附近的店铺"菜单入口
- [ ] Task 3.3：创建 `h5/src/views/NearbyShops.vue` 地图页面组件
- [ ] Task 3.4：实现用户位置获取（含权限请求处理）
- [ ] Task 3.5：实现店铺列表前端距离计算与筛选（Haversine 公式）
- [ ] Task 3.6：实现半径选择功能（3km/5km/10km/20km）
- [ ] Task 3.7：实现高德地图展示与店铺标记
- [ ] Task 3.8：实现点击店铺标记显示详情弹窗

### Milestone 4：验证与修复
- [ ] Task 4.1：B 端店铺坐标配置功能端到端测试
- [ ] Task 4.2：H5 端地图功能端到端测试
- [ ] Task 4.3：修复测试中发现的问题

## 验收检查点
- [ ] 编译通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] Review 通过

## 下一步
执行 /harness-apply shop-location-20260423-01
