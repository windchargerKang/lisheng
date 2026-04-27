---
name: product-profit-rate-20260425-01
status: designed
---

# 技术方案：产品分润比例配置

## 方案概述

为支持按产品差异化配置分润比例，在产品模型中新增 `service_fee_rate` 和 `agent_profit_rate` 字段，并在产品管理页面提供配置入口。分润计算时优先使用产品级配置，未配置时使用全局默认值。

## 详细设计

### 架构变更

- **后端**：修改 `Product` 模型、`ProductSchema`、`ProfitService._calculate_profit()` 方法
- **前端**：在产品管理页面的"定价"对话框中新增分润比例配置表单
- **数据库**：在 `products` 表中新增两个字段

### 数据模型变更

**`backend/app/models/product.py`**：
```python
class Product(Base):
    # ... 现有字段 ...
    service_fee_rate = Column(Numeric(5, 4), nullable=True)  # 服务费比例 (0.3000 = 30%)
    agent_profit_rate = Column(Numeric(5, 4), nullable=True)  # 区代利润比例 (0.1000 = 10%)
```

**`backend/app/schemas/product.py`**（新增 Schema）：
```python
class ProductUpdate(BaseModel):
    service_fee_rate: Optional[Decimal] = None
    agent_profit_rate: Optional[Decimal] = None
```

### 接口变更

**产品创建/更新接口**：
- `POST /products` - 支持传入 `service_fee_rate` 和 `agent_profit_rate`
- `PUT /products/{id}` - 支持更新分润比例

**产品列表接口**：
- `GET /products` - 返回中新增分润比例字段

### 分润计算逻辑修改

**`backend/app/services/profit_service.py`**：

```python
def _calculate_profit(self, order: Order) -> Tuple[Decimal, Decimal]:
    """
    计算分润金额
    
    优先级：
    1. 产品级配置（service_fee_rate, agent_profit_rate）
    2. 全局默认配置（config.json）
    """
    # 尝试从产品获取分润比例
    if order.product and order.product.service_fee_rate is not None:
        service_fee_rate = order.product.service_fee_rate
        agent_profit_rate = order.product.agent_profit_rate
    else:
        # 使用全局默认配置
        config = self._load_config()
        service_fee_rate = Decimal(str(config.get("profit", {}).get("service_fee_rate", 0.30)))
        agent_profit_rate = Decimal(str(config.get("profit", {}).get("agent_profit_rate", 0.10)))
    
    # 计算分润金额
    service_fee = (order.total_amount * service_fee_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    agent_profit = (order.total_amount * agent_profit_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    return service_fee, agent_profit
```

### 前端 UI 设计

在"定价"对话框中新增分润配置表单：

```
┌─────────────────────────────────┐
│  设置产品价格                   │
├─────────────────────────────────┤
│  零售价格：¥ [____]             │
│  店铺价格：¥ [____]             │
│  区代价格：¥ [____]             │
├─────────────────────────────────┤
│  分润配置                       │
│  服务费比例：[____] %           │
│  区代利润比例：[____] %         │
│  （留空表示使用全局默认值）      │
└─────────────────────────────────┘
```

## 影响范围

- **受影响模块**：
  - `backend/app/models/product.py`
  - `backend/app/schemas/product.py`
  - `backend/app/services/profit_service.py`
  - `backend/app/api/v1/products.py`
  - `frontend/src/views/Products.vue`

- **受保护路径变更**：无

- **向后兼容性**：
  - 新增字段为 nullable，旧数据不受影响
  - 未配置分润比例的产品自动使用全局默认值

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 历史订单分润计算错误 | 中 | 分润计算时基于订单关联的产品，历史订单不受影响 |
| 分润比例输入错误导致损失 | 中 | 前端添加范围校验（0-100%），后端添加合理性检查 |
| 数据库迁移失败 | 低 | 使用 Alembic 迁移脚本，支持回滚 |

## 事务与数据

- **事务边界**：分润计算在订单核销事务内完成
- **数据迁移**：
  ```sql
  ALTER TABLE products ADD COLUMN service_fee_rate NUMERIC(5, 4);
  ALTER TABLE products ADD COLUMN agent_profit_rate NUMERIC(5, 4);
  ```
- **回滚方案**：新增字段为 nullable，回滚只需删除字段

## 测试策略

1. **单元测试**：
   - `ProfitService._calculate_profit()` 使用产品配置
   - `ProfitService._calculate_profit()` 使用全局默认值

2. **集成测试**：
   - 产品创建/更新时分润比例的保存
   - 订单核销时分润计算的正确性

3. **手动验证**：
   - 在产品管理页面配置分润比例
   - 创建订单并核销，验证分润金额
