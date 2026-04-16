# 测试规范

## 测试层级

1. **单元测试**：测试独立函数/组件
2. **集成测试**：测试模块间交互
3. **端到端测试**：测试完整用户流程

## 测试要求

### 必须编写测试的场景

- [ ] 新增功能
- [ ] Bug 修复（regression test）
- [ ] 核心逻辑变更
- [ ] 边界条件处理

### 测试覆盖目标

| 文件类型 | 最低覆盖率 |
|----------|------------|
| 工具函数 | 90% |
| 服务层 | 80% |
| 组件 | 关键路径覆盖 |
| 页面 | 冒烟测试 |

## 测试命名规范

```
should_[预期结果]_when_[条件]_[可选：其他上下文]
```

示例：
- `should_return_user_data_when_api_success`
- `should_show_error_message_when_validation_fails`

## 测试结构

```typescript
describe('ComponentName', () => {
  describe('functionName', () => {
    it('should [预期行为] when [条件]', () => {
      // Given
      // When
      // Then
    });
  });
});
```

## 运行测试

```bash
# 安装依赖
npm install

# 运行所有测试
npm test

# 运行单个文件测试
npm test -- --testPathPattern=filename

# 生成覆盖率报告
npm test -- --coverage
```
