<template>
  <div class="payment-page">
    <van-nav-bar
      title="选择支付方式"
      left-arrow
      @click-left="$router.back()"
    />

    <div class="payment-content">
      <div class="amount-section">
        <div class="amount-label">支付金额</div>
        <div class="amount-value">
          <span class="currency">¥</span>
          <span class="number">{{ amount }}</span>
        </div>
      </div>

      <!-- 支付方式选择 -->
      <van-cell-group class="payment-methods">
        <van-radio-group v-model="selectedMethod">
          <van-cell
            v-for="method in paymentMethods"
            :key="method.value"
            :title="method.label"
            clickable
            @click="selectedMethod = method.value"
          >
            <template #icon>
              <van-icon :name="method.icon" size="24" :color="method.color" style="margin-right: 8px;" />
            </template>
            <template #right-icon>
              <van-radio :name="method.value" icon-size="16px" />
            </template>
          </van-cell>
        </van-radio-group>
      </van-cell-group>

      <div class="tips">
        <van-icon name="info-o" />
        <span>模拟支付环境，不会发生真实扣款</span>
      </div>
    </div>

    <van-button
      type="primary"
      block
      round
      class="pay-button"
      @click="confirmPayment"
    >
      确认支付
    </van-button>

    <!-- 支付成功弹窗 -->
    <van-dialog
      v-model:show="successDialog"
      title="支付成功"
      :show-confirm-button="false"
      :before-close="onDialogClose"
    >
      <div class="success-content">
        <div class="success-icon">✓</div>
        <div class="success-title">支付成功</div>
        <div class="success-amount">¥{{ amount }}</div>
        <div class="success-status">订单已支付，正在配货中</div>
      </div>
      <div class="success-actions">
        <van-button plain type="default" @click="goToOrders">查看订单</van-button>
        <van-button type="primary" @click="goToHome">返回首页</van-button>
      </div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast } from 'vant'
import apiClient from '@/api'

const router = useRouter()
const route = useRoute()

const orderId = ref<number>(0)
const amount = ref<string>('0.00')
const selectedMethod = ref('wechat')
const successDialog = ref(false)

const paymentMethods = [
  { value: 'wechat', label: '微信支付', icon: 'wechat', color: '#07c160' },
  { value: 'alipay', label: '支付宝', icon: 'alipay', color: '#1677ff' },
  { value: 'bank', label: '银行卡', icon: 'bank-card', color: '#ff9500' }
]

const confirmPayment = async () => {
  try {
    // 调用 confirm 接口触发钱包扣款
    await apiClient.post(`/orders/${orderId.value}/confirm`)

    successDialog.value = true
  } catch (error: any) {
    showToast(error.response?.data?.detail || '支付失败')
  }
}

const onDialogClose = () => {
  return false // 阻止自动关闭，手动控制
}

const goToOrders = () => {
  router.push(`/orders/${orderId.value}`)
}

const goToHome = () => {
  router.push('/home')
}

onMounted(() => {
  orderId.value = Number(route.query.order_id) || 0
  amount.value = String(route.query.amount || '0.00')

  if (!orderId.value) {
    showToast('订单信息不完整')
    router.back()
  }
})
</script>

<style scoped>
.payment-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.payment-content {
  padding: 20px 16px;
}

.amount-section {
  text-align: center;
  padding: 30px 20px;
  background: white;
  border-radius: 12px;
  margin-bottom: 16px;
}

.amount-label {
  font-size: 14px;
  color: #969799;
  margin-bottom: 10px;
}

.amount-value {
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.amount-value .currency {
  font-size: 20px;
  color: #f44;
  margin-top: 4px;
}

.amount-value .number {
  font-size: 40px;
  color: #f44;
  font-weight: bold;
}

.payment-methods {
  margin-bottom: 16px;
}

.payment-methods :deep(.van-cell) {
  padding: 16px;
}

.tips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  color: #969799;
  padding: 10px;
}

.pay-button {
  margin: 20px 16px;
}

.success-content {
  padding: 30px 20px;
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  background: #07c160;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 50px;
  color: white;
  font-weight: bold;
}

.success-title {
  font-size: 18px;
  font-weight: 600;
  color: #323233;
  margin-bottom: 10px;
}

.success-amount {
  font-size: 28px;
  color: #f44;
  font-weight: bold;
  margin-bottom: 10px;
}

.success-status {
  font-size: 14px;
  color: #969799;
}

.success-actions {
  display: flex;
  gap: 10px;
  padding: 0 20px 20px;
}

.success-actions .van-button {
  flex: 1;
}
</style>
