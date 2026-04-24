# shop-location-20260423-01 - 归档记录

## 基本信息
- change-id: shop-location-20260423-01
- 创建时间：2026-04-23
- 完成时间：2026-04-23
- 归档时间：2026-04-23 17:00:20

## 需求摘要
为店铺增加地图坐标属性，实现以下功能：
1. 管理员可在运营管理端配置店铺的地图坐标（经纬度）
2. H5 端"我的"页面增加"附近店铺"菜单
3. 用户可查看自己附近的店铺（支持 3km/5km/10km/20km 范围筛选）
4. 在地图上显示店铺位置，支持点击查看详情和导航

## 技术方案摘要
- **数据模型**：shops 表新增 latitude(DECIMAL 10,8)、longitude(DECIMAL 11,8) 字段
- **后端 API**：GET/PUT /shops 增加坐标字段返回和更新
- **前端地图**：使用高德地图 JS API v2.0
- **距离计算**：前端 Haversine 公式计算用户与店铺距离

## 实现摘要
### 后端变更
- backend/app/models/shop.py - 新增经纬度字段
- backend/app/api/v1/shops.py - API 返回和更新坐标
- backend/scripts/add_shop_location_columns.py - 数据库迁移脚本

### B 端前端变更
- frontend/src/views/Shops.vue - 地图选点功能
- frontend/package.json - @amap/amap-jsapi-loader 依赖

### H5 端变更
- h5/src/views/Profile.vue - 菜单入口
- h5/src/views/NearbyShops.vue - 地图页面组件
- h5/package.json - @amap/amap-jsapi-loader 依赖

## 评审结论
**有条件通过**
- 待修复：分页查询建议添加 ORDER BY 稳定排序
- 待补充：数据库回滚脚本

## 变更文件清单
1. backend/app/models/shop.py
2. backend/app/api/v1/shops.py
3. backend/scripts/add_shop_location_columns.py (新增)
4. frontend/src/views/Shops.vue
5. frontend/package.json
6. h5/src/views/Profile.vue
7. h5/src/views/NearbyShops.vue (新增)
8. h5/package.json
9. h5/src/router/index.ts

## 配置信息
- 高德地图 Key: aa44b61446e611d6aa60fdd137973e31
- 安全密钥：a4ffb9efc6af3053bd6ca94633d2fa40
- 服务平台：Web 端 (JS API)
