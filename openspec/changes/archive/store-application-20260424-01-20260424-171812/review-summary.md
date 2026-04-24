# 评审摘要：store-application-20260424-01

## 变更目标
在 H5 端增加"我想开店"功能，允许普通客户在线提交升级为店铺或区代的申请，运营管理端提供审核功能，审核通过后自动升级用户角色。

## 影响到的类和模块

### 后端新增
- `backend/app/models/store_application.py` - 申请数据模型
- `backend/app/api/v1/store_applications.py` - 申请管理 API（7 个端点）
- `backend/migrations/009_add_store_applications.py` - 数据库迁移脚本

### 后端修改
- `backend/app/models/__init__.py` - 导出新模型
- `backend/app/api/v1/api.py` - 注册新路由
- `backend/scripts/init_db.py` - 更新初始化脚本

### 前端新增
- `h5/src/views/StoreApply.vue` - 申请页面
- `h5/src/views/StoreApplyRecords.vue` - 申请记录页面

### 前端修改
- `h5/src/views/Profile.vue` - 增加"我想开店"入口
- `h5/src/router/index.ts` - 添加新路由

## 是否涉及
- [x] 接口（API）变更 - 新增 7 个申请管理 API
- [x] 数据库/SQL 变更 - 新增 store_applications 表及索引
- [x] 事务边界变化 - 审核通过时需保证原子性
- [ ] 配置变更
- [ ] 新增外部依赖

## 已运行测试
- [ ] 单元测试 - 未执行
- [ ] 集成测试 - 未执行
- [x] 数据库迁移验证 - 已执行成功

## 已知风险

1. **并发提交风险**（已缓解）
   - 风险：并发提交区代申请可能导致区域重复
   - 缓解：前后端双重校验 + 数据库唯一约束

2. **审核通过时角色升级失败**（已缓解）
   - 风险：创建 Shop/Agent 成功但更新角色失败
   - 缓解：使用事务保证原子性，失败时回滚

3. **地图选点失败**（已缓解）
   - 风险：高德地图 API 加载失败
   - 缓解：允许手动输入经纬度（前端表单支持）

## 仍未解决的问题

1. **缺少测试覆盖**
   - API 集成测试未编写
   - 前端组件测试未编写
   - 建议在合并前补充

## 已修复问题

1. ~~分页查询缺少稳定排序~~ - 已添加 `id` 作为次要排序条件
2. ~~审核 API 缺少幂等性~~ - 已添加状态检查，重复调用返回友好提示

## 下一步建议

1. 补充 API 集成测试
2. 前端功能测试验证
