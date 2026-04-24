---
name: user-address-management-20260420-02
status: completed
created: 2026-04-20
---

# 技术方案：用户地址管理功能

## 方案概述

为用户创建独立的地址管理模块，支持地址的增删改查和默认地址设置，并在结算页面实现地址选择联动，提升购物体验。

**核心设计原则：**
- YAGNI：地址信息简化处理，无需省市区选择器
- 复用优先：结算页地址选择复用地址管理列表
- 软删除：保留历史数据，支持数据恢复

## 详细设计

### 架构变更

**前端新增页面：**
| 页面 | 路径 | 说明 |
|------|------|------|
| Addresses.vue | /addresses | 地址列表页（支持选择模式） |
| AddressEdit.vue | /addresses/edit | 地址编辑页 |

**后端新增模块：**
| 模块 | 说明 |
|------|------|
| app/models/address.py | UserAddress 数据模型 |
| app/api/v1/addresses.py | 地址管理 API 路由 |

### 数据模型变更

**用户地址表 (user_addresses)：**
```sql
CREATE TABLE user_addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    receiver_name VARCHAR(100) NOT NULL,
    receiver_phone VARCHAR(20) NOT NULL,
    receiver_address VARCHAR(500) NOT NULL,
    province VARCHAR(50),
    city VARCHAR(50),
    district VARCHAR(50),
    detail_address VARCHAR(200),
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 接口变更

**新增 API 端点：**
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/addresses | 获取地址列表 |
| GET | /api/v1/addresses/{id} | 获取地址详情 |
| POST | /api/v1/addresses | 新增地址 |
| PUT | /api/v1/addresses/{id} | 更新地址 |
| DELETE | /api/v1/addresses/{id} | 删除地址 |
| POST | /api/v1/addresses/{id}/default | 设置默认地址 |
| PUT | /api/v1/orders/{id}/address | 更新订单地址（仅限 PENDING 状态） |
| PUT | /api/v1/orders/{id}/remark | 更新订单备注（仅限 PENDING 状态） |

### 前端实现设计

#### 1. 地址列表页 (Addresses.vue)

```typescript
// 选择模式判断
const isSelectMode = route.query.selectMode === '1'

// 地址选择处理
const selectAddress = (addr: Address) => {
  if (isSelectMode) {
    localStorage.setItem('selected_address', JSON.stringify(addr))
    window.dispatchEvent(new CustomEvent('address-selected', { detail: addr }))
    router.back()
  }
}
```

#### 2. 地址编辑页 (AddressEdit.vue)

```typescript
// 表单数据
const form = ref({
  receiver_name: '',
  receiver_phone: '',
  receiver_address: '',
  detail_address: '',
  is_default: false,
})

// 保存后处理
if (selectMode) {
  // 返回结算页并传递地址
  router.back()
}
```

#### 3. 结算页联动 (Checkout.vue)

```typescript
// 监听地址选择事件
const handleAddressSelected = (event: CustomEvent<Address>) => {
  selectedAddress.value = event.detail
  checkoutForm.value.receiver_name = event.detail.receiver_name
  checkoutForm.value.receiver_phone = event.detail.receiver_phone
  checkoutForm.value.receiver_address = event.detail.receiver_address
}

// 加载默认地址
const fetchDefaultAddress = async () => {
  const response = await apiClient.get('/addresses')
  const addresses = response.data.items || []
  selectedAddress.value = addresses.find(a => a.is_default) || addresses[0]
}
```

### 路由配置

```typescript
{
  path: 'addresses',
  name: 'Addresses',
  component: () => import('@/views/Addresses.vue'),
  meta: { requiresAuth: true, title: '收货地址' }
},
{
  path: 'addresses/edit',
  name: 'AddressEdit',
  component: () => import('@/views/AddressEdit.vue'),
  meta: { requiresAuth: true, title: '编辑地址' }
}
```

## 影响范围

### 受影响模块
- 前端：新增 Addresses.vue, AddressEdit.vue
- 前端：修改 Checkout.vue（地址选择联动）
- 前端：修改 Profile.vue（地址管理入口）
- 前端：修改 router/index.ts（新增路由）
- 后端：新增 app/models/address.py
- 后端：新增 app/api/v1/addresses.py
- 后端：修改 app/api/v1/api.py（注册路由）

### 受保护路径变更
- 无

### 向后兼容性
- 新增功能，不影响现有接口
- 订单表收货信息字段保持不变

## 风险评估

| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 地址数据与用户绑定错误 | 中 | API 层验证 user_id 与当前用户一致 |
| 默认地址并发设置 | 低 | 设置默认时先取消所有默认 |
| 结算页地址选择状态丢失 | 中 | 使用 localStorage + CustomEvent 传递 |

## 事务与数据

### 事务边界
- 设置默认地址：取消所有默认 + 设置新默认（同一事务）
- 新增/更新地址：单表操作，无需事务

### 数据迁移
```sql
-- 执行 migrations/003_add_user_addresses.sql
CREATE TABLE user_addresses (...);
CREATE INDEX idx_user_addresses_user_id;
CREATE INDEX idx_user_addresses_is_default;
```

### 回滚方案
- 删除新增的 user_addresses 表
- 恢复 Checkout.vue 到直接输入地址版本

## 测试策略

1. **后端测试**
   - 地址 CRUD API 测试
   - 默认地址设置测试
   - 地址权限验证（只能操作自己的地址）

2. **前端测试**
   - 地址列表渲染
   - 地址选择联动
   - 结算页地址填充

3. **集成测试**
   - 完整流程：新增地址 → 设为默认 → 结算页选择 → 提交订单
