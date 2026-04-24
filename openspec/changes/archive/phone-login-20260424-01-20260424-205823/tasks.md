---
name: phone-login-20260424-01
status: planned
---

# 执行任务：手机号登录功能

## 任务列表

### Milestone 1：后端数据模型与接口
- [ ] Task 1.1：User 模型新增 phone_number 字段
- [ ] Task 1.2：创建数据库迁移脚本（添加 phone_number 列）
- [ ] Task 1.3：修改 LoginRequest Schema，支持手机号登录
- [ ] Task 1.4：修改登录接口，自动识别手机号/用户名
- [ ] Task 1.5：新增 UserCreatePhone Schema（手机号注册请求）
- [ ] Task 1.6：新增注册接口 POST /auth/register-by-phone

### Milestone 2：前端登录页面改造
- [ ] Task 2.1：改造 Login.vue，增加账号/手机 Tab 切换
- [ ] Task 2.2：实现手机号登录表单（手机号、密码、滑块验证）
- [ ] Task 2.3：实现协议勾选功能
- [ ] Task 2.4：增加忘记密码和注册入口
- [ ] Task 2.5：实现手机号格式校验

### Milestone 3：前端注册页面
- [ ] Task 3.1：新建 Register.vue 注册页面
- [ ] Task 3.2：实现注册表单（手机号、密码、确认密码、滑块验证、协议勾选）
- [ ] Task 3.3：实现密码一致性校验
- [ ] Task 3.4：调用注册 API，处理成功/失败
- [ ] Task 3.5：新增注册页面路由

### Milestone 4：测试与验证
- [ ] Task 4.1：编写手机号登录集成测试
- [ ] Task 4.2：编写手机号注册集成测试
- [ ] Task 4.3：前端手动验证（登录/注册全流程）
- [ ] Task 4.4：代码 Review 与修复

## 验收检查点
- [ ] 编译通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] Review 通过

## 下一步
执行 /harness-apply phone-login-20260424-01
