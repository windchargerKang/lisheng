# store-application-20260424-01 - 归档记录

## 基本信息
- **change-id**: store-application-20260424-01
- **创建时间**: 2026-04-24
- **完成时间**: 2026-04-24
- **归档时间**: 2026-04-24

## 需求摘要
在 H5 端增加"我想开店"功能，允许普通客户在线提交升级为店铺或区代的申请：
- 店铺申请：填写店铺名称、区域、对应区代（自动关联）、地图定位坐标
- 区代申请：填写区代名称、区域（重复性检验）、推荐区代（选填）
- 提交后等待管理员审核，审核通过自动升级角色，拒绝可重新申请
- 运营管理端提供审核功能：列表查看、通过/拒绝、填写拒绝理由

## 技术方案摘要
### 后端新增
- `backend/app/models/store_application.py` - 申请数据模型
- `backend/app/api/v1/store_applications.py` - 7 个 API 端点
- `backend/migrations/009_add_store_applications.py` - 数据库迁移

### 前端新增
- `h5/src/views/StoreApply.vue` - H5 申请页面
- `h5/src/views/StoreApplyRecords.vue` - H5 申请记录页面
- `frontend/src/views/StoreApplications.vue` - 运营管理端审核页面

### 路由变更
- H5 端：`/store-apply`、`/store-apply/records`
- 运营端：`/store-applications`（系统管理菜单下）

## 实现摘要
### 已完成功能
1. H5 端"我的"页面增加"我想开店"入口
2. 申请类型选择器（店铺/区代）
3. 区域级联选择器（省→市→区，三级自动确认）
4. 地图定位选点（高德地图 API）
5. 区代自动关联（根据区域自动填充）
6. 区代区域重复性校验（前端 + 后端双重校验）
7. 申请记录查看（待审核/已通过/已拒绝状态）
8. 运营管理端审核页面
9. 审核通过/拒绝功能（拒绝需填写理由）
10. 审核通过后自动升级用户角色

### 修复的问题
1. 区域选择器样式问题 → 使用自定义 type-option 样式
2. API 响应格式不匹配 → 调整为 `res.data.regions`
3. van-cascader 叶子节点识别 → 仅在有子节点时添加 children 属性
4. van-cascader finish 事件参数结构 → 从 `e.selectedOptions` 提取
5. 地图弹窗初始化时机 → 添加延迟和 mapInitialized 标志
6. 区域验证 API 422 错误 → 添加 Query 参数声明
7. 路由顺序冲突 → `/check-region` 移到 `/{application_id}` 之前

## 评审结论
### 严重问题
无

### 警告问题
无

### 建议项
1. 补充 API 集成测试
2. 前端组件测试验证

## 变更文件清单
### 后端新增
- `backend/app/models/store_application.py`
- `backend/app/api/v1/store_applications.py`
- `backend/migrations/009_add_store_applications.py`

### 后端修改
- `backend/app/models/__init__.py`
- `backend/app/api/v1/api.py`
- `backend/scripts/init_db.py`

### 前端新增
- `h5/src/views/StoreApply.vue`
- `h5/src/views/StoreApplyRecords.vue`
- `frontend/src/views/StoreApplications.vue`

### 前端修改
- `h5/src/views/Profile.vue`
- `h5/src/router/index.ts`
- `frontend/src/router/index.ts`
- `frontend/src/layouts/MainLayout.vue`

### 文档
- `openspec/changes/store-application-20260424-01/proposal.md`
- `openspec/changes/store-application-20260424-01/design.md`
- `openspec/changes/store-application-20260424-01/tasks.md`
- `openspec/changes/store-application-20260424-01/review-summary.md`
