<template>
  <div class="wallet-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      title="我的钱包"
      left-arrow
      @click-left="$router.back()"
    />

    <!-- 钱包概览 -->
    <div class="wallet-header">
      <div class="balance">
        <div class="label">可用余额</div>
        <div class="amount">¥{{ wallet?.balance || '0.00' }}</div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <van-button type="primary" plain icon="plus" @click="showRecharge = true">充值</van-button>
      <van-button type="primary" plain icon="exchange" @click="showWithdraw = true">提现</van-button>
    </div>

    <!-- 流水记录 -->
    <div class="transactions-section">
      <div class="section-title">流水记录</div>
      <van-tabs v-model:active="activeTab" @change="onTabChange">
        <van-tab title="全部">
          <van-list
            v-model:loading="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="onLoad"
          >
            <van-cell
              v-for="item in transactions"
              :key="item.id"
              :title="item.transaction_no"
              :label="`${item.created_at?.slice(0, 16) || ''} · ${getStatusLabel(item.status)}`"
            >
              <template #right-side>
                <div :class="['transaction-amount', item.transaction_type === 'RECHARGE' ? 'income' : 'expense']">
                  {{ item.transaction_type === 'RECHARGE' ? '+' : '-' }}¥{{ item.amount }}
                </div>
              </template>
            </van-cell>
          </van-list>
        </van-tab>
        <van-tab title="充值">
          <van-list
            v-model:loading="rechargeLoading"
            :finished="rechargeFinished"
            finished-text="没有更多了"
            @load="onLoadRecharge"
          >
            <van-cell
              v-for="item in rechargeTransactions"
              :key="item.id"
              :title="item.transaction_no"
              :label="`${item.created_at?.slice(0, 16) || ''} · ${getStatusLabel(item.status)}`"
            >
              <template #right-side>
                <div class="transaction-amount income">+¥{{ item.amount }}</div>
              </template>
            </van-cell>
          </van-list>
        </van-tab>
        <van-tab title="提现">
          <van-list
            v-model:loading="withdrawLoading"
            :finished="withdrawFinished"
            finished-text="没有更多了"
            @load="onLoadWithdraw"
          >
            <van-cell
              v-for="item in withdrawTransactions"
              :key="item.id"
              :title="item.transaction_no"
              :label="`${item.created_at?.slice(0, 16) || ''} · ${getStatusLabel(item.status)}`"
            >
              <template #right-side>
                <div class="transaction-amount expense">-¥{{ item.amount }}</div>
              </template>
            </van-cell>
          </van-list>
        </van-tab>
      </van-tabs>
    </div>

    <!-- 充值对话框 -->
    <van-dialog
      v-model:show="showRecharge"
      title="充值"
      show-cancel-button
      @confirm="handleRecharge"
    >
      <van-field
        v-model="rechargeForm.amount"
        type="number"
        placeholder="请输入充值金额"
        :formatter="(value: string) => value.replace(/[^0-9.]/g, '')"
      />
    </van-dialog>

    <!-- 提现对话框 -->
    <van-dialog
      v-model:show="showWithdraw"
      title="申请提现"
      show-cancel-button
      @confirm="handleWithdraw"
    >
      <van-field
        v-model="withdrawForm.amount"
        type="number"
        placeholder="请输入提现金额"
        :formatter="(value: string) => value.replace(/[^0-9.]/g, '')"
      />
      <van-field
        v-model="withdrawForm.withdraw_method"
        placeholder="提现方式（银行卡/支付宝/微信）"
      />
      <van-field
        v-model="withdrawForm.withdraw_account"
        placeholder="提现账号"
      />
      <van-field
        v-model="withdrawForm.remark"
        placeholder="备注（可选）"
        rows="2"
        type="textarea"
      />
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { showToast, showSuccessToast, showFailToast } from 'vant'
import api from '@/api'

interface Wallet {
  id: number
  user_id: number
  balance: string
  created_at: string
  updated_at: string
}

interface Transaction {
  id: number
  wallet_id: number
  transaction_type: 'RECHARGE' | 'WITHDRAW'
  amount: string
  balance_after: string
  transaction_no: string
  status: 'PENDING' | 'COMPLETED' | 'REJECTED'
  withdraw_method?: string
  withdraw_account?: string
  remark?: string
  created_at: string
}

const wallet = ref<Wallet | null>(null)
const activeTab = ref(0)

// 流水记录
const transactions = ref<Transaction[]>([])
const rechargeTransactions = ref<Transaction[]>([])
const withdrawTransactions = ref<Transaction[]>([])

const loading = ref(false)
const rechargeLoading = ref(false)
const withdrawLoading = ref(false)
const finished = ref(false)
const rechargeFinished = ref(false)
const withdrawFinished = ref(false)

const page = ref(1)
const rechargePage = ref(1)
const withdrawPage = ref(1)

// 表单
const rechargeForm = reactive({
  amount: '',
})

const withdrawForm = reactive({
  amount: '',
  withdraw_method: '',
  withdraw_account: '',
  remark: '',
})

const showRecharge = ref(false)
const showWithdraw = ref(false)

const fetchWallet = async () => {
  try {
    const res = await api.get('/wallet')
    wallet.value = res.data
  } catch (error: any) {
    if (error.response?.status !== 404) {
      showToast('加载钱包信息失败')
    }
  }
}

const loadTransactions = async (pageNum: number, type?: string) => {
  const params: Record<string, any> = {
    page: pageNum,
    page_size: 10,
  }
  if (type) {
    params.transaction_type = type
  }

  const res = await api.get('/wallet/transactions', { params })
  return res.data
}

const onLoad = async () => {
  loading.value = true
  try {
    const data = await loadTransactions(page.value)
    if (page.value === 1) {
      transactions.value = []
    }
    transactions.value.push(...data.items)
    page.value++
    finished.value = transactions.value.length >= data.total
  } catch (error) {
    showFailToast('加载失败')
  } finally {
    loading.value = false
  }
}

const onLoadRecharge = async () => {
  rechargeLoading.value = true
  try {
    const data = await loadTransactions(rechargePage.value, 'RECHARGE')
    if (rechargePage.value === 1) {
      rechargeTransactions.value = []
    }
    rechargeTransactions.value.push(...data.items)
    rechargePage.value++
    rechargeFinished.value = rechargeTransactions.value.length >= data.total
  } catch (error) {
    showFailToast('加载失败')
  } finally {
    rechargeLoading.value = false
  }
}

const onLoadWithdraw = async () => {
  withdrawLoading.value = true
  try {
    const data = await loadTransactions(withdrawPage.value, 'WITHDRAW')
    if (withdrawPage.value === 1) {
      withdrawTransactions.value = []
    }
    withdrawTransactions.value.push(...data.items)
    withdrawPage.value++
    withdrawFinished.value = withdrawTransactions.value.length >= data.total
  } catch (error) {
    showFailToast('加载失败')
  } finally {
    withdrawLoading.value = false
  }
}

const onTabChange = (index: number) => {
  activeTab.value = index
  // 重置对应 tab 的状态
  if (index === 0) {
    page.value = 1
    finished.value = false
  } else if (index === 1) {
    rechargePage.value = 1
    rechargeFinished.value = false
  } else if (index === 2) {
    withdrawPage.value = 1
    withdrawFinished.value = false
  }
}

const handleRecharge = async () => {
  if (!rechargeForm.amount || parseFloat(rechargeForm.amount) <= 0) {
    showToast('请输入有效的充值金额')
    return false
  }

  try {
    await api.post('/wallet/recharge', {
      user_id: wallet.value?.user_id,
      amount: parseFloat(rechargeForm.amount),
      remark: 'H5 充值',
    })
    showSuccessToast('充值成功')
    rechargeForm.amount = ''
    fetchWallet()
    // 重置列表
    page.value = 1
    finished.value = false
    onLoad()
    return true
  } catch (error: any) {
    showFailToast(error.response?.data?.detail || '充值失败')
    return false
  }
}

const handleWithdraw = async () => {
  if (!withdrawForm.amount || parseFloat(withdrawForm.amount) <= 0) {
    showToast('请输入有效的提现金额')
    return false
  }
  if (!withdrawForm.withdraw_method) {
    showToast('请选择提现方式')
    return false
  }
  if (!withdrawForm.withdraw_account) {
    showToast('请输入提现账号')
    return false
  }

  try {
    await api.post('/wallet/withdraw', {
      amount: parseFloat(withdrawForm.amount),
      withdraw_method: withdrawForm.withdraw_method,
      withdraw_account: withdrawForm.withdraw_account,
      remark: withdrawForm.remark || undefined,
    })
    showSuccessToast('提现申请已提交，等待审核')
    withdrawForm.amount = ''
    withdrawForm.withdraw_method = ''
    withdrawForm.withdraw_account = ''
    withdrawForm.remark = ''
    fetchWallet()
    // 重置列表
    withdrawPage.value = 1
    withdrawFinished.value = false
    onLoadWithdraw()
    return true
  } catch (error: any) {
    showFailToast(error.response?.data?.detail || '提现申请失败')
    return false
  }
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    PENDING: '待审核',
    COMPLETED: '已完成',
    REJECTED: '已拒绝',
  }
  return map[status] || status
}

onMounted(() => {
  fetchWallet()
})
</script>

<style scoped>
.wallet-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-top: 46px;
  position: relative;
}

.wallet-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px 60px;
  text-align: center;
}

.balance .label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  margin-bottom: 8px;
}

.balance .amount {
  color: #fff;
  font-size: 36px;
  font-weight: bold;
}

.actions {
  display: flex;
  gap: 12px;
  padding: 0 16px;
  margin-top: -30px;
}

.actions .van-button {
  flex: 1;
  height: 44px;
  font-size: 15px;
}

.transactions-section {
  margin-top: 12px;
  background-color: #fff;
}

.section-title {
  padding: 16px;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #f0f0f0;
}

.transaction-amount {
  font-size: 15px;
  font-weight: bold;
}

.transaction-amount.income {
  color: #07c160;
}

.transaction-amount.expense {
  color: #f56c6c;
}
</style>
