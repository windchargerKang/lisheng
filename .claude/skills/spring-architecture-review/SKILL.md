---

name: spring-architecture-review
description: 检查 Spring Boot 分层、依赖方向和业务逻辑放置是否合理

---

# Spring 架构审查

## 输入

`$ARGUMENTS` = 本次改动涉及的文件、目录或 change id

## 检查项

### 1. Controller 业务逻辑检查
- Controller 是否写入了业务逻辑
- 业务逻辑应仅在 Service/Domain 层

### 2. 跨层调用检查
- Controller 是否直接调用 Mapper / Repository
- 这是严重违规，应通过 Service 间接访问

### 3. Service 依赖检查
- Service 是否依赖了 Web 层对象（如 HttpServletRequest）
- Web 层对象不应渗透到业务层

### 4. DTO/VO 滥用检查
- DTO/VO 是否被直接当作实体持久化
- 应该有明确的 DO/Entity

### 5. 跨层耦合检查
- 是否存在明显的跨层耦合
- 依赖方向是否正确：Controller → Service → Repository

### 6. 逻辑归类检查
- 是否有可以归为 Domain/Service 的逻辑散落在其他层
- 比如工具类、转换逻辑等

## 输出格式

```markdown
## Spring 架构评审

### 严重问题（必须修复）
1. [文件:行号] 问题描述

### 警告问题（建议修复）
1. [文件:行号] 问题描述

### 建议项（可选）
1. 优化建议
```

## 规则

- 只读操作，不修改任何文件
- 严格按照 Spring Boot 标准分层
- 重点关注业务逻辑是否放对了层
