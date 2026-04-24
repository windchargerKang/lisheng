---
name: mobile-shopping-flow-20260420-01
status: designed
created: 2026-04-20
---

# 技术方案：移动端购物全流程打通

## 方案概述

完善 H5 移动端购物流程，实现从首页浏览 → 产品详情 → 加入购物车 → 结算确认 → 模拟支付 → 订单生成的完整闭环。

**核心设计原则：**
- YAGNI：简化地址功能，下单时填写，无需地址管理
- 复用优先：购物车、订单列表等已有功能直接复用
- 模拟支付：前端弹窗选择支付方式，后端记录支付状态

## 详细设计

### 架构变更

**前端新增页面：**
| 页面 | 路径 | 说明 |
|------|------|------|
| Checkout.vue | /checkout | 结算确认页（地址表单 + 订单备注 + 提交） |
| Payment.vue | /payment | 支付页（支付方式选择 + 支付成功弹窗） |

**后端新增 API：**
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/orders/:id/pay | 订单支付（模拟） |

### 数据模型变更

**订单表扩展字段：**
- `receiver_name` - 收货人姓名
- `receiver_phone` - 收货人电话
- `receiver_address` - 收货地址
- `remark` - 订单备注

**新增支付记录表（可选）：**
- `order_id` - 关联订单
- `payment_method` - 支付方式（wechat/alipay/bank）
- `transaction_id` - 交易号（模拟生成）
- `paid_at` - 支付时间

### 前端实现设计

#### 1. 首页推荐产品列表 (Home.vue)

```typescript
// 修改 onLoad 函数，调用 API 获取推荐产品
const fetchProducts = async () => {
  const response = await apiClient.get('/products', {
    params: { page: 1, page_size: 10, is_new: 1 }
  })
  products.value = response.data.items || []
}
```

#### 2. 结算确认页 (Checkout.vue)

```typescript
// 表单数据
const checkoutForm = ref({
  receiver_name: '',
  receiver_phone: '',
  receiver_address: '',
  remark: ''
})

// 从购物车获取商品明细
const fetchCartItems = async () => {
  const response = await apiClient.get('/cart/items')
  cartItems.value = response.data.items || []
}

// 提交订单
const submitOrder = async () => {
  const response = await apiClient.post('/orders', {
    cart_item_ids: cartItems.value.map(item => item.id),
    receiver_name: checkoutForm.value.receiver_name,
    receiver_phone: checkoutForm.value.receiver_phone,
    receiver_address: checkoutForm.value.receiver_address,
    remark: checkoutForm.value.remark
  })
  // 跳转到支付
  showPaymentDialog(response.data.id)
}
```

#### 3. 支付弹窗组件

```typescript
// 支付方式选择
const paymentMethods = [
  { value: 'wechat', label: '微信支付', icon: 'wechat' },
  { value: 'alipay', label: '支付宝', icon: 'alipay' },
  { value: 'bank', label: '银行卡', icon: 'bank-card' }
]

// 调用支付 API
const confirmPayment = async (orderId: number, method: string) => {
  await apiClient.post(`/orders/${orderId}/pay`, {
    payment_method: method,
    transaction_id: `MOCK_${Date.now()}` // 模拟交易号
  })
  // 跳转到支付成功页
  router.push(`/payment/success?order_id=${orderId}`)
}
```

#### 4. 支付成功页 (PaymentSuccess.vue)

```typescript
// 从路由获取订单 ID 和金额
const route = useRoute()
const orderId = route.query.order_id as string
const amount = route.query.amount as string

// 按钮操作
const goToOrder = () => router.push(`/orders/${orderId}`)
const goToHome = () => router.push('/home')
```

### 后端实现设计

#### 订单支付 API (orders.py)

```python
@router.post("/{order_id}/pay")
async def pay_order(
    order_id: int,
    request: PaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """订单支付（模拟）"""
    # 获取订单
    order = await get_order_or_404(db, order_id)
    
    # 验证订单属于当前用户
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此订单")
    
    # 验证订单状态
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="订单状态不支持支付")
    
    # 更新订单状态
    order.status = OrderStatus.PAID
    order.paid_at = datetime.now()
    
    # 创建支付记录
    payment = PaymentRecord(
        order_id=order_id,
        payment_method=request.payment_method,
        transaction_id=request.transaction_id or f"MOCK_{int(time.time())}",
        amount=order.total_amount,
        status=PaymentStatus.SUCCESS
    )
    db.add(payment)
    
    await db.commit()
    
    return {"message": "支付成功", "order_id": order_id}
```

### 路由配置 (router/index.ts)

```typescript
const routes: RouteRecordRaw[] = [
  // ... 现有路由
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('@/views/Checkout.vue'),
    meta: { requiresAuth: true, title: '确认订单' }
  },
  {
    path: '/payment',
    name: 'Payment',
    component: () => import('@/views/Payment.vue'),
    meta: { requiresAuth: true, title: '支付' }
  }
]
```

## 影响范围

### 受影响模块
- 前端：Home.vue, Checkout.vue(新增), PaymentSuccess.vue(新增), router/index.ts
- 后端：orders.py, models/order.py, models/payment.py(新增)

### 受保护路径变更
- 无

### 向后兼容性
- 订单表新增字段为可空，不影响现有数据
- 新增 API 不影响现有接口

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 订单表新增字段需迁移 | 低 | 使用 alembic 创建迁移脚本 |
| 支付状态流转并发问题 | 中 | 使用数据库事务 + 状态校验 |
| 地址信息未持久化 | 低 | 订单保存地址快照，满足基本需求 |

## 事务与数据

### 事务边界
- 支付操作：订单状态更新 + 支付记录创建在同一事务中

### 数据迁移
- 订单表新增字段迁移：
```sql
ALTER TABLE orders ADD COLUMN receiver_name VARCHAR(100);
ALTER TABLE orders ADD COLUMN receiver_phone VARCHAR(20);
ALTER TABLE orders ADD COLUMN receiver_address TEXT;
ALTER TABLE orders ADD COLUMN remark TEXT;
ALTER TABLE orders ADD COLUMN paid_at DATETIME;
```

### 回滚方案
- 支付失败时回滚订单状态和支付记录

## 测试策略

1. **前端测试**
   - 首页推荐产品列表渲染
   - 结算表单验证
   - 支付弹窗交互
   - 支付成功页跳转

2. **后端测试**
   - 支付 API 权限验证
   - 订单状态流转验证
   - 支付记录创建验证

3. **集成测试**
   - 完整购物流程：首页 → 详情 → 购物车 → 结算 → 支付 → 订单
