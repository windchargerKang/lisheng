---
name: user-permission-20260417-03
status: designed
---

# 技术方案：用户权限管理

## 方案概述

基于 RBAC（角色 - 权限）模型构建轻量级权限管理系统，实现菜单级、按钮级权限控制，数据级权限（按角色过滤），以及用户账号统一管理。

**核心设计原则：**
- 轻量级：permission_code 字符串匹配，非完整 RBAC
- 统一用户管理：所有角色共用 Users 表
- 关键操作日志：记录登录、创建、删除、修改等审计事件

## 详细设计

### 数据模型变更

#### 新增表

**1. roles（角色表）**
```sql
CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,      -- 角色名称：系统管理员、运营人员、区代等
    code VARCHAR(50) NOT NULL UNIQUE,      -- 角色代码：admin, operator, agent
    description VARCHAR(200),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**2. permissions（权限表）**
```sql
CREATE TABLE permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,             -- 权限名称：用户查看、角色编辑
    code VARCHAR(100) NOT NULL UNIQUE,     -- 权限代码：user:view, role:edit
    type ENUM('MENU', 'BUTTON', 'DATA') NOT NULL,
    parent_id INT NULL,                    -- 父权限 ID（菜单层级）
    api_path VARCHAR(200),                 -- 对应的 API 路径
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**3. role_permissions（角色权限关联表）**
```sql
CREATE TABLE role_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_role_permission (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);
```

**4. operation_logs（操作日志表）**
```sql
CREATE TABLE operation_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,           -- 操作类型：LOGIN, CREATE, DELETE, UPDATE
    resource_type VARCHAR(50),             -- 资源类型：USER, ROLE, ORDER
    resource_id INT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    details JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_action (user_id, action),
    INDEX idx_created_at (created_at)
);
```

#### 修改表

**users 表扩展**
```sql
ALTER TABLE users ADD COLUMN role_id INT NULL AFTER role_type;
ALTER TABLE users ADD COLUMN status ENUM('ACTIVE', 'DISABLED') NOT NULL DEFAULT 'ACTIVE';
ALTER TABLE users ADD COLUMN last_login_at DATETIME NULL;
ALTER TABLE users ADD COLUMN last_login_ip VARCHAR(45) NULL;
ALTER TABLE users ADD INDEX idx_role_id (role_id);
ALTER TABLE users ADD INDEX idx_status (status);
```

**注意：** `role_type` 字段保留以兼容历史数据，新代码优先使用 `role_id`。

### 权限判断逻辑

```python
# 用户权限检查装饰器
async def check_permission(permission_code: str):
    async def wrapper(request, call_next):
        current_user = request.state.user
        if current_user.role_id is None:
            raise PermissionDenied("用户未分配角色")
        
        # 查询用户权限
        permissions = await get_user_permissions(current_user.role_id)
        permission_codes = [p.code for p in permissions]
        
        if permission_code not in permission_codes:
            raise PermissionDenied(f"缺少权限：{permission_code}")
        
        return await call_next(request)
    return wrapper

# 获取用户权限
async def get_user_permissions(role_id: int) -> list[Permission]:
    query = select(Permission).join(RolePermission).where(RolePermission.role_id == role_id)
    result = await db.execute(query)
    return result.scalars().all()
```

### API 设计

#### 角色管理

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /api/v1/roles | role:view | 角色列表 |
| POST | /api/v1/roles | role:create | 创建角色 |
| PUT | /api/v1/roles/{id} | role:edit | 编辑角色 |
| DELETE | /api/v1/roles/{id} | role:delete | 删除角色 |
| GET | /api/v1/roles/{id}/permissions | role:view | 获取角色权限 |
| PUT | /api/v1/roles/{id}/permissions | role:edit | 配置角色权限 |

#### 账号管理

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /api/v1/users | user:view | 用户列表（支持角色筛选） |
| POST | /api/v1/users | user:create | 创建用户 |
| PUT | /api/v1/users/{id} | user:edit | 编辑用户 |
| DELETE | /api/v1/users/{id} | user:delete | 删除用户 |
| POST | /api/v1/users/{id}/disable | user:edit | 禁用/启用用户 |
| POST | /api/v1/users/{id}/reset-password | user:edit | 重置密码 |

#### 操作日志

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /api/v1/operation-logs | log:view | 日志列表（支持筛选） |
| GET | /api/v1/operation-logs/export | log:export | 导出日志 |

#### 权限检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/permissions/my | 获取当前用户权限列表 |

### 前端页面

#### 1. 角色管理（/roles）
- 角色列表（表格）
- 创建角色按钮
- 编辑角色（弹窗）
- 删除角色（确认）
- 配置权限（跳转 RoleDetail）

#### 2. 角色权限配置（/roles/:id）
- 权限树形结构展示
- 勾选权限（菜单/按钮）
- 保存权限配置

#### 3. 用户管理（/users）
- 用户列表（表格，支持角色筛选）
- 创建用户按钮
- 编辑用户（弹窗）
- 禁用/启用用户
- 重置密码

#### 4. 操作日志（/logs）
- 日志列表（表格）
- 筛选条件（用户、操作类型、时间范围）
- 导出按钮

### 初始化数据

**默认角色：**
```python
DEFAULT_ROLES = [
    {"code": "admin", "name": "系统管理员"},
    {"code": "operator", "name": "运营人员"},
    {"code": "agent", "name": "区代"},
    {"code": "shop_agent", "name": "店铺代理"},
    {"code": "supplier", "name": "供应商"},
]
```

**默认权限：**
```python
DEFAULT_PERMISSIONS = [
    # 用户管理
    {"code": "user:view", "name": "查看用户", "type": "MENU"},
    {"code": "user:create", "name": "创建用户", "type": "BUTTON"},
    {"code": "user:edit", "name": "编辑用户", "type": "BUTTON"},
    {"code": "user:delete", "name": "删除用户", "type": "BUTTON"},
    
    # 角色管理
    {"code": "role:view", "name": "查看角色", "type": "MENU"},
    {"code": "role:create", "name": "创建角色", "type": "BUTTON"},
    {"code": "role:edit", "name": "编辑角色", "type": "BUTTON"},
    {"code": "role:delete", "name": "删除角色", "type": "BUTTON"},
    
    # 日志管理
    {"code": "log:view", "name": "查看日志", "type": "MENU"},
    {"code": "log:export", "name": "导出日志", "type": "BUTTON"},
    
    # 业务权限（示例）
    {"code": "region:view", "name": "查看区域", "type": "MENU"},
    {"code": "shop:view", "name": "查看店铺", "type": "MENU"},
    {"code": "supplier:view", "name": "查看供应商", "type": "MENU"},
]
```

**系统管理员角色绑定所有权限。**

## 影响范围

### 受影响模块
- 后端：models, api/v1, middleware/auth
- 前端：views, router, stores, api
- 数据库：新增 4 张表，修改 users 表

### 受保护路径变更
- 无（不涉及配置文件修改）

### 向后兼容性
- `role_type` 字段保留，旧代码可继续使用
- 新代码优先使用 `role_id` + RBAC 权限检查

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 历史用户无 role_id | 中 | 迁移脚本：根据 role_type 分配默认角色 |
| 权限检查性能 | 低 | 用户权限缓存到 token 或 Redis |
| 操作日志数据量大 | 低 | 定期归档（保留 6 个月） |

## 事务与数据

### 事务边界
- 创建角色 + 绑定权限：同一事务
- 创建用户 + 分配角色：同一事务
- 配置角色权限：先删除旧绑定，再插入新绑定（同一事务）

### 数据迁移
```sql
-- 迁移现有用户到默认角色
UPDATE users u
JOIN roles r ON r.code = CASE 
    WHEN u.role_type = 'admin' THEN 'admin'
    WHEN u.role_type = 'agent' THEN 'agent'
    WHEN u.role_type = 'supplier' THEN 'supplier'
    ELSE 'operator'
END
SET u.role_id = r.id
WHERE u.role_id IS NULL;
```

### 回滚方案
- 删除新增表：DROP TABLE IF EXISTS roles, permissions, role_permissions, operation_logs
- 恢复 users 表：ALTER TABLE users DROP COLUMN role_id, status, last_login_at, last_login_ip

## 测试策略

1. **单元测试**
   - 权限检查装饰器
   - 角色管理 Service
   - 用户管理 Service

2. **集成测试**
   - 角色 CRUD API
   - 用户 CRUD API
   - 权限配置 API
   - 操作日志记录

3. **验证点**
   - 无权限用户访问接口返回 403
   - 禁用用户无法登录
   - 操作日志正确记录
   - 角色权限配置生效
