# 数据库规范

## 数据源

*待补充 - 说明项目使用的前后端数据交互方式*

## API 规范

### RESTful 设计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/resource | 获取资源列表 |
| GET | /api/resource/:id | 获取单个资源 |
| POST | /api/resource | 创建资源 |
| PUT | /api/resource/:id | 更新资源 |
| DELETE | /api/resource/:id | 删除资源 |

### 响应格式

```typescript
// 成功响应
{
  "data": { ... },
  "message": "success"
}

// 错误响应
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

## 状态管理

### 数据缓存策略

- 列表数据：考虑分页和缓存
- 详情数据：根据更新频率决定缓存策略
- 表单数据：提交前本地缓存，防止丢失

## 错误处理

- 网络错误：显示友好提示，支持重试
- 业务错误：展示后端返回的错误信息
- 系统错误：记录日志，引导用户联系支持
