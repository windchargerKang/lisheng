---
name: channel-sales-management-20260416-01
status: planned
---

# 执行任务：渠道客户管理系统

## 任务列表

### Milestone 1：项目框架搭建

- [ ] Task 1.1：创建 Python FastAPI 后端项目结构
- [ ] Task 1.2：创建 Vue 3 Web 运营端项目结构
- [ ] Task 1.3：配置数据库连接和 SQLAlchemy
- [ ] Task 1.4：配置 JWT 认证中间件

### Milestone 2：用户认证模块

- [ ] Task 2.1：实现 User 数据模型
- [ ] Task 2.2：实现登录 API（POST /api/auth/login）
- [ ] Task 2.3：实现获取用户信息 API（GET /api/auth/profile）
- [ ] Task 2.4：实现前端登录页面和路由守卫

### Milestone 3：区域管理模块

- [ ] Task 3.1：实现 Region 数据模型（支持树形结构）
- [ ] Task 3.2：实现区域树查询 API（GET /api/regions）
- [ ] Task 3.3：实现区域 CRUD API（创建/更新/删除）
- [ ] Task 3.4：实现前端区域管理页面（树形控件）

### Milestone 4：店铺管理模块

- [ ] Task 4.1：实现 Shop 数据模型（含推荐关系）
- [ ] Task 4.2：实现店铺列表 API（分页、筛选）
- [ ] Task 4.3：实现店铺 CRUD API
- [ ] Task 4.4：实现前端店铺管理页面

### Milestone 5：区代管理模块

- [ ] Task 5.1：实现 Agent 数据模型（区域绑定唯一）
- [ ] Task 5.2：实现区代列表 API（分页、筛选）
- [ ] Task 5.3：实现区代 CRUD API
- [ ] Task 5.4：实现前端区代管理页面

### Milestone 6：产品管理模块

- [ ] Task 6.1：实现 Product 和 PriceTier 数据模型
- [ ] Task 6.2：实现产品列表 API
- [ ] Task 6.3：实现产品 CRUD API
- [ ] Task 6.4：实现产品价格设置 API（三级定价）
- [ ] Task 6.5：实现前端产品管理页面

## 验收检查点

- [ ] 编译通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] Review 通过

## 下一步

执行 `/harness-apply channel-sales-management-20260416-01`
