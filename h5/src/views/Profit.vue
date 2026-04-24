<template>
  <div class="profit-page">
    <!-- 收益总览卡片 -->
    <div class="overview-card">
      <div class="total-profit">
        <div class="label">累计收益</div>
        <div class="amount">¥{{ overview.total_profit?.toFixed(2) || '0.00' }}</div>
      </div>
      <div class="stats-row">
        <div class="stat-item">
          <div class="stat-label">可提现</div>
          <div class="stat-value">¥{{ overview.available_amount?.toFixed(2) || '0.00' }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">待结算</div>
          <div class="stat-value">¥{{ overview.pending_amount?.toFixed(2) || '0.00' }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">已提现</div>
          <div class="stat-value">¥{{ overview.withdrawn_amount?.toFixed(2) || '0.00' }}</div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-row">
      <van-button
        type="primary"
        block
        round
        :disabled="overview.available_amount <= 0"
        @click="showWithdraw = true"
      >
        申请提现
      </van-button>
    </div>

    <!-- 收益明细 -->
    <van-cell-group class="records-group">
      <van-cell title="收益明细" is-link to="/profit/records">
        <template #label>
          查看完整记录
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 提现记录 -->
    <van-cell-group class="records-group">
      <van-cell title="提现记录" is-link to="/profit/withdrawals">
        <template #label>
          查看提现历史
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 提现弹窗 -->
    <van-dialog
      v-model:show="showWithdraw"
      title="申请提现"
      show-cancel-button
      @confirm="handleWithdraw"
    >
      <van-field
        v-model="withdrawAmount"
        type="number"
        placeholder="请输入提现金额"
        :label="金额"
      >
        <template #button>
          <van-button
            size="small"
            type="primary"
            plain
            @click="withdrawAll"
          >
            全部提现
          </van-button>
        </template>
      </van-field>
      <div class="withdraw-tip">
        可提现金额：¥{{ overview.available_amount?.toFixed(2) || '0.00' }}
      </div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import apiClient from '@/api'

const router = useRouter()

const overview = reactive({
  total_profit: 0,
  available_amount: 0,
  pending_amount: 0,
  withdrawn_amount: 0,
})

const showWithdraw = ref(false)
const withdrawAmount = ref('')

const fetchOverview = async () => {
  try {
    const response = await apiClient.get('/profit/overview')
    Object.assign(overview, response.data)
  } catch (error) {
    console.error('获取收益总览失败:', error)
  }
}

const withdrawAll = () => {
  withdrawAmount.value = overview.available_amount.toFixed(2)
}

const handleWithdraw = async () => {
  const amount = parseFloat(withdrawAmount.value)
  if (!amount || amount <= 0) {
    showToast('请输入有效的提现金额')
    return
  }

  try {
    await apiClient.post('/profit/withdrawals', { amount })
    showToast('提现申请已提交')
    withdrawAmount.value = ''
    fetchOverview()
  } catch (error: any) {
    showToast(error.response?.data?.detail || '提现失败')
  }
}

onMounted(() => {
  fetchOverview()
})
</script>

<style scoped>
.profit-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 16px;
}

.overview-card {
  background: linear-gradient(135deg, #1989fa 0%, #0e6fd6 100%);
  border-radius: 12px;
  padding: 24px 20px;
  color: #fff;
  margin-bottom: 16px;
}

.total-profit {
  text-align: center;
  margin-bottom: 24px;
}

.total-profit .label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.total-profit .amount {
  font-size: 36px;
  font-weight: bold;
}

.stats-row {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
}

.stat-item .stat-label {
  font-size: 12px;
  opacity: 0.8;
  margin-bottom: 4px;
}

.stat-item .stat-value {
  font-size: 16px;
  font-weight: bold;
}

.action-row {
  margin-bottom: 16px;
}

.action-row :deep(.van-button) {
  height: 44px;
}

.records-group {
  margin-bottom: 16px;
  border-radius: 12px;
  overflow: hidden;
}

.withdraw-tip {
  padding: 12px 16px;
  font-size: 13px;
  color: #969799;
  background-color: #f7f8fa;
}
</style>
