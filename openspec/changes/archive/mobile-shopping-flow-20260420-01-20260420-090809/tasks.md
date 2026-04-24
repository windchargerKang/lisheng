---
name: mobile-shopping-flow-20260420-01
status: planned
---

# 执行任务：mobile-shopping-flow-20260420-01

## 任务列表

### Milestone 1：数据库迁移

- [ ] Task 1.1：创建订单表扩展字段迁移
  - receiver_name VARCHAR(100)
  - receiver_phone VARCHAR(20)
  - receiver_address TEXT
  - remark TEXT
  - paid_at DATETIME

- [ ] Task 1.2：创建支付记录表迁移
  - id, order_id, payment_method, transaction_id, amount, status, paid_at, created_at

- [ ] Task 1.3：验证迁移执行成功

### Milestone 2：后端支付 API

- [ ] Task 2.1：定义 PaymentRequest 和 PaymentRecord 模型
  - PaymentRequest: payment_method, transaction_id (optional)
  - PaymentRecord: 支付记录 ORM 模型

- [ ] Task 2.2：实现 POST /api/v1/orders/:id/pay 接口
  - 验证订单归属
  - 验证订单状态
  - 更新订单状态为 PAID
  - 创建支付记录

- [ ] Task 2.3：添加订单元数据字段更新（receiver_*，remark）
  - 修改 OrderCreateRequest
  - 修改创建订单逻辑

- [ ] Task 2.4：编写支付 API 单元测试

### Milestone 3：前端首页推荐产品

- [ ] Task 3.1：修改 Home.vue onLoad 函数
  - 调用 GET /products API
  - 按 is_new 排序获取推荐产品

- [ ] Task 3.2：完善产品卡片展示
  - 显示产品图片、名称、价格
  - 点击跳转到产品详情

- [ ] Task 3.3：验证首页产品列表渲染

### Milestone 4：前端结算确认页

- [ ] Task 4.1：创建 Checkout.vue 页面
  - 收货地址表单（姓名、电话、地址）
  - 订单备注输入框
  - 商品清单展示
  - 金额计算

- [ ] Task 4.2：实现表单验证
  - 姓名、电话、地址必填
  - 手机号格式验证

- [ ] Task 4.3：实现提交订单逻辑
  - 调用 POST /orders API
  - 成功后跳转到支付弹窗

- [ ] Task 4.4：添加路由配置 /checkout

### Milestone 5：前端支付功能

- [ ] Task 5.1：创建支付弹窗组件
  - Vant Popup 弹窗
  - 三种支付方式选择（微信/支付宝/银行卡）
  - 确认支付按钮

- [ ] Task 5.2：实现支付 API 调用
  - POST /orders/:id/pay
  - 生成模拟交易号

- [ ] Task 5.3：创建 PaymentSuccess.vue 页面
  - 支付成功图标
  - 支付金额显示
  - 查看订单/返回首页按钮

- [ ] Task 5.4：添加路由配置 /payment/success

### Milestone 6：集成测试与验证

- [ ] Task 6.1：完整购物流程测试
  - 首页浏览产品
  - 加入购物车
  - 结算页填写地址
  - 选择支付方式
  - 支付成功
  - 查看订单

- [ ] Task 6.2：边界情况测试
  - 空购物车提交
  - 表单验证失败
  - 支付失败处理

- [ ] Task 6.3：验证订单状态正确流转

## 验收检查点

- [ ] 编译通过
- [ ] 前端页面渲染正常
- [ ] 后端 API 测试通过
- [ ] 完整购物流程打通
- [ ] Review 通过

## 下一步

执行 `/harness-apply mobile-shopping-flow-20260420-01`
