# 数据库规范

## 数据源

*待补充 - 说明项目使用的前后端数据交互方式*

## HTML 富文本字段规范

### 背景
产品详情等字段需要支持富文本描述，但直接存储和渲染用户提交的 HTML 存在 XSS 攻击风险。

### 规范
1. **后端必须过滤 HTML 内容** - 使用 `bleach.clean()` 过滤危险标签
2. **白名单机制** - 仅允许安全的 HTML 标签（p, br, strong, em, ul, ol, li, img, a 等）
3. **移除危险属性** - 不允许 `style` 属性，防止 CSS 注入
4. **允许的标签列表**：
   - 文本：p, br, strong, em, b, i, u
   - 列表：ul, ol, li
   - 标题：h1-h6
   - 其他：blockquote, pre, code, span, div
   - 媒体：img (仅允许 src, alt, width, height 属性)
   - 链接：a (仅允许 href, title, target 属性)

### 实现位置
- `backend/app/api/v1/products.py` - `sanitize_html()` 函数


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

## 并发安全规范

### 钱包/余额相关操作

**背景**：钱包提现、余额扣减等操作存在并发风险，多笔同时请求可能导致余额超扣。

**规范**：
1. **必须使用行级锁** - 使用 `SELECT ... FOR UPDATE` 锁定钱包记录
2. **计算可用余额** - 可用余额 = 钱包余额 - 待审核（PENDING）提现总额
3. **事务边界清晰** - 余额更新与流水记录必须在同一事务中完成

**实现示例**：
```python
# 使用 FOR UPDATE 锁定钱包
wallet = await db.execute(
    select(Wallet).where(Wallet.user_id == user_id).with_for_update()
)

# 计算待审核提现总额
pending_total = await db.execute(
    select(func.sum(WalletTransaction.amount)).where(
        WalletTransaction.wallet_id == wallet.id,
        WalletTransaction.status == TransactionStatus.PENDING
    )
)

# 可用余额检查
available_balance = wallet.balance - pending_total
if available_balance < amount:
    raise ValueError("可用余额不足")
```

### 流水号生成

**风险**：使用"查询当日数量 +1"的方式生成流水号，高并发下可能产生重复。

**规范**：
1. **数据库唯一约束兜底** - 流水号字段必须添加 UNIQUE 约束
2. **推荐使用序列** - PostgreSQL 使用 SEQUENCE，MySQL 使用独立序号表
3. **或使用 UUID/ULID** - 无并发问题，但可读性稍差

## 索引设计

### 组合索引优先

对于多条件查询，优先使用组合索引而非多个单列索引：

```sql
-- 推荐：组合索引
CREATE INDEX idx_transactions_wallet_type_status ON wallet_transactions(wallet_id, transaction_type, status);

-- 不推荐：多个单列索引（查询优化器只能使用其中一个）
CREATE INDEX idx_wallet_id ON wallet_transactions(wallet_id);
CREATE INDEX idx_type ON wallet_transactions(transaction_type);
CREATE INDEX idx_status ON wallet_transactions(status);
```
