---
name: store-application-20260424-01
status: planned
---

# 执行任务：store-application-20260424-01

## 任务列表

### Milestone 1：后端数据模型与 API 实现
- [ ] Task 1.1：创建 `backend/app/models/store_application.py` 数据模型
- [ ] Task 1.2：创建 `backend/app/api/v1/store_applications.py` API 路由
- [ ] Task 1.3：在 `backend/app/api/v1/api.py` 中注册新路由
- [ ] Task 1.4：在 `backend/app/models/__init__.py` 中导出新模型
- [ ] Task 1.5：编写 API 集成测试

### Milestone 2：H5 端申请页面实现
- [ ] Task 2.1：创建 `h5/src/views/StoreApply.vue` 申请页面
- [ ] Task 2.2：实现申请表单（店铺/区代两种类型）
- [ ] Task 2.3：实现地图选点弹窗组件
- [ ] Task 2.4：实现区域重复性校验逻辑
- [ ] Task 2.5：创建 `h5/src/views/StoreApplyRecords.vue` 申请记录页面

### Milestone 3：H5 端入口集成
- [ ] Task 3.1：修改 `h5/src/views/Profile.vue` 增加"我想开店"入口
- [ ] Task 3.2：在 Profile 页面右上角增加"我的申请"入口

### Milestone 4：后端审核功能实现
- [ ] Task 4.1：实现审核通过 API（创建 Shop/Agent + 更新用户角色）
- [ ] Task 4.2：实现审核拒绝 API（记录拒绝理由）
- [ ] Task 4.3：实现申请列表 API（管理端）
- [ ] Task 4.4：编写审核流程集成测试

### Milestone 5：数据库迁移
- [ ] Task 5.1：创建数据库迁移脚本（store_applications 表）
- [ ] Task 5.2：执行迁移并验证

## 验收检查点
- [ ] 编译通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] Review 通过

## 下一步
执行 /harness-apply store-application-20260424-01
