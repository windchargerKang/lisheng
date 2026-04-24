---
name: user-permission-20260417-03
status: planned
---

# 执行任务：user-permission-20260417-03

## 任务列表

### Milestone 1：数据模型扩展

- [ ] Task 1.1：创建 SQLAlchemy 模型文件
  - `backend/app/models/permission.py` - Permission 模型
  - `backend/app/models/role.py` - Role 模型
  - `backend/app/models/role_permission.py` - RolePermission 关联模型
  - `backend/app/models/operation_log.py` - OperationLog 模型

- [ ] Task 1.2：扩展 User 模型
  - 添加 `role_id`, `status`, `last_login_at`, `last_login_ip` 字段
  - 添加 `role` 关系

- [ ] Task 1.3：创建数据库迁移脚本
  - 新增表：roles, permissions, role_permissions, operation_logs
  - 修改表：users 添加字段和索引
  - 初始化默认角色和权限数据

- [ ] Task 1.4：验证模型
  - 运行 Alembic 迁移
  - 验证表结构正确

### Milestone 2：权限管理 API

- [ ] Task 2.1：创建角色管理 API
  - `backend/app/api/v1/roles.py`
  - GET /api/v1/roles - 角色列表
  - POST /api/v1/roles - 创建角色
  - PUT /api/v1/roles/{id} - 编辑角色
  - DELETE /api/v1/roles/{id} - 删除角色

- [ ] Task 2.2：创建角色权限配置 API
  - GET /api/v1/roles/{id}/permissions - 获取角色权限
  - PUT /api/v1/roles/{id}/permissions - 配置角色权限

- [ ] Task 2.3：创建权限检查中间件
  - `backend/app/middleware/permission.py`
  - 权限检查装饰器
  - 获取当前用户权限 API：GET /api/v1/permissions/my

- [ ] Task 2.4：验证角色管理 API
  - 运行 pytest 测试角色 CRUD
  - 验证权限配置生效

### Milestone 3：账号管理 API

- [ ] Task 3.1：扩展用户管理 API
  - 修改 `backend/app/api/v1/users.py`
  - GET /api/v1/users - 支持 role_id 筛选
  - POST /api/v1/users - 支持分配角色
  - PUT /api/v1/users/{id} - 支持修改角色

- [ ] Task 3.2：新增用户管理功能
  - POST /api/v1/users/{id}/disable - 禁用/启用用户
  - POST /api/v1/users/{id}/reset-password - 重置密码

- [ ] Task 3.3：更新登录逻辑
  - 修改 `backend/app/api/v1/auth.py`
  - 记录 last_login_at, last_login_ip
  - 检查用户状态（DISABLED 不允许登录）
  - 返回用户权限列表

- [ ] Task 3.4：验证账号管理 API
  - 运行 pytest 测试用户 CRUD
  - 验证禁用用户无法登录
  - 验证密码重置功能

### Milestone 4：操作日志 API

- [ ] Task 4.1：创建操作日志记录器
  - `backend/app/utils/logger.py`
  - 记录登录、创建、删除、修改操作
  - 异步写入 operation_logs 表

- [ ] Task 4.2：创建操作日志 API
  - `backend/app/api/v1/operation_logs.py`
  - GET /api/v1/operation-logs - 日志列表（支持筛选）
  - GET /api/v1/operation-logs/export - 导出日志（CSV）

- [ ] Task 4.3：验证操作日志
  - 手动触发各类操作
  - 验证日志正确记录
  - 验证导出功能

### Milestone 5：前端角色管理页面

- [ ] Task 5.1：创建角色列表页面
  - `frontend/src/views/Roles.vue`
  - 角色列表表格
  - 创建/编辑/删除角色

- [ ] Task 5.2：创建角色权限配置页面
  - `frontend/src/views/RoleDetail.vue`
  - 权限树形结构
  - 勾选权限并保存

- [ ] Task 5.3：创建 API 客户端
  - `frontend/src/api/roles.ts`
  - `frontend/src/api/permissions.ts`

- [ ] Task 5.4：更新路由
  - `frontend/src/router/index.ts`
  - 添加角色管理路由

- [ ] Task 5.5：验证前端页面
  - 访问 /roles 页面
  - 测试创建、编辑、配置权限功能

### Milestone 6：前端用户管理页面

- [ ] Task 6.1：创建用户列表页面
  - `frontend/src/views/Users.vue`
  - 用户列表表格
  - 支持按角色筛选

- [ ] Task 6.2：创建用户编辑页面
  - `frontend/src/views/UserDetail.vue`
  - 编辑用户信息
  - 分配角色
  - 禁用/启用用户
  - 重置密码

- [ ] Task 6.3：创建 API 客户端
  - `frontend/src/api/users.ts`

- [ ] Task 6.4：更新路由
  - `frontend/src/router/index.ts`
  - 添加用户管理路由

- [ ] Task 6.5：验证前端页面
  - 访问 /users 页面
  - 测试创建、编辑、禁用、重置密码功能

### Milestone 7：前端操作日志页面

- [ ] Task 7.1：创建操作日志页面
  - `frontend/src/views/OperationLogs.vue`
  - 日志列表表格
  - 筛选条件（用户、操作类型、时间范围）
  - 导出按钮

- [ ] Task 7.2：创建 API 客户端
  - `frontend/src/api/logs.ts`

- [ ] Task 7.3：更新路由
  - `frontend/src/router/index.ts`
  - 添加操作日志路由

- [ ] Task 7.4：验证前端页面
  - 访问 /logs 页面
  - 测试筛选和导出功能

### Milestone 8：集成测试与清理

- [ ] Task 8.1：更新侧边栏菜单
  - `frontend/src/layouts/MainLayout.vue`
  - 添加角色管理、用户管理、操作日志菜单项
  - 根据权限显示/隐藏菜单

- [ ] Task 8.2：更新登录页面
  - `frontend/src/views/Login.vue`
  - 根据角色跳转到不同首页（保持现有逻辑）

- [ ] Task 8.3：运行完整测试
  - 后端 pytest 测试
  - 前端手动测试所有功能

- [ ] Task 8.4：代码审查
  - 检查代码规范
  - 检查测试覆盖率
  - 修复警告问题

## 验收检查点

- [ ] 编译通过（后端 + 前端）
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] Review 通过

## 下一步

执行 `/harness-apply user-permission-20260417-03`
