<template>
  <div class="page-container">
    <div class="page-header">
      <h2>我的钱包</h2>
    </div>

    <!-- 钱包概览 -->
    <el-card class="wallet-card">
      <div class="wallet-info">
        <div class="balance">
          <span class="label">可用余额</span>
          <span class="amount">¥{{ wallet?.balance || '0.00' }}</span>
        </div>
        <div class="actions">
          <el-button type="primary" @click="showWithdrawDialog = true">
            <el-icon><Plus /></el-icon>
            申请提现
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 流水记录 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>流水记录</span>
          <el-form :inline="true" :model="filterForm">
            <el-form-item label="类型">
              <el-select v-model="filterForm.transaction_type" placeholder="全部类型" clearable>
                <el-option label="充值" value="RECHARGE" />
                <el-option label="提现" value="WITHDRAW" />
                <el-option label="订单收支" value="ORDER_PAYMENT" />
                <el-option label="服务费" value="SERVICE_FEE" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
                <el-option label="待审核" value="PENDING" />
                <el-option label="审核通过" value="COMPLETED" />
                <el-option label="审核拒绝" value="REJECTED" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchTransactions">查询</el-button>
            </el-form-item>
          </el-form>
        </div>
      </template>

      <el-table :data="transactions" border v-loading="loading">
        <el-table-column prop="transaction_no" label="流水号" width="180" />
        <el-table-column prop="transaction_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTransactionTypeTag(row.transaction_type)">
              {{ getTransactionTypeLabel(row.transaction_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            <span :class="getAmountClass(row)">
              {{ getAmountSign(row) }}¥{{ Math.abs(getAmountValue(row)) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="balance_after" label="余额" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="withdraw_method" label="提现方式" width="120" v-if="filterForm.transaction_type !== 'RECHARGE'" />
        <el-table-column prop="withdraw_account" label="提现账号" width="150" v-if="filterForm.transaction_type !== 'RECHARGE'" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @change="fetchTransactions"
        />
      </div>
    </el-card>

    <!-- 提现对话框 -->
    <el-dialog v-model="showWithdrawDialog" title="申请提现" width="500px">
      <el-form :model="withdrawForm" :rules="withdrawRules" ref="formRef" label-width="100px">
        <el-form-item label="提现金额" prop="amount">
          <el-input-number v-model="withdrawForm.amount" :min="0.01" :precision="2" :step="0.01" style="width: 100%" />
        </el-form-item>
        <el-form-item label="提现方式" prop="withdraw_method">
          <el-select v-model="withdrawForm.withdraw_method" placeholder="请选择提现方式" style="width: 100%">
            <el-option label="银行卡" value="银行卡" />
            <el-option label="支付宝" value="支付宝" />
            <el-option label="微信" value="微信" />
          </el-select>
        </el-form-item>
        <el-form-item label="提现账号" prop="withdraw_account">
          <el-input v-model="withdrawForm.withdraw_account" placeholder="请输入提现账号" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="withdrawForm.remark" type="textarea" :rows="3" placeholder="备注（可选）" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showWithdrawDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api'

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
  transaction_type: 'RECHARGE' | 'WITHDRAW' | 'ORDER_PAYMENT' | 'SERVICE_FEE'
  amount: string | number
  balance_after: string
  transaction_no: string
  status: 'PENDING' | 'COMPLETED' | 'REJECTED'
  withdraw_method?: string
  withdraw_account?: string
  remark?: string
  created_at: string
}

const loading = ref(false)
const submitting = ref(false)
const showWithdrawDialog = ref(false)
const wallet = ref<Wallet | null>(null)
const transactions = ref<Transaction[]>([])
const formRef = ref()

const filterForm = reactive({
  transaction_type: '' as string | null,
  status: '' as string | null,
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

const withdrawForm = reactive({
  amount: null as number | null,
  withdraw_method: '',
  withdraw_account: '',
  remark: '',
})

const withdrawRules = {
  amount: [{ required: true, message: '请输入提现金额', trigger: 'blur' }],
  withdraw_method: [{ required: true, message: '请选择提现方式', trigger: 'change' }],
  withdraw_account: [{ required: true, message: '请输入提现账号', trigger: 'blur' }],
}

const fetchWallet = async () => {
  try {
    const response = await apiClient.get('/wallet')
    wallet.value = response.data
  } catch (error: any) {
    if (error.response?.status !== 404) {
      ElMessage.error('加载钱包信息失败')
    }
  }
}

const fetchTransactions = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: pagination.page,
      page_size: pagination.page_size,
    }
    if (filterForm.transaction_type) params.transaction_type = filterForm.transaction_type
    if (filterForm.status) params.status = filterForm.status

    const response = await apiClient.get('/wallet/transactions', { params })
    transactions.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error('加载流水记录失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  await formRef.value?.validate()
  submitting.value = true

  try {
    await apiClient.post('/wallet/withdraw', {
      amount: withdrawForm.amount,
      withdraw_method: withdrawForm.withdraw_method,
      withdraw_account: withdrawForm.withdraw_account,
      remark: withdrawForm.remark || undefined,
    })
    ElMessage.success('提现申请已提交，等待审核')
    showWithdrawDialog.value = false
    fetchWallet()
    fetchTransactions()
    // 重置表单
    withdrawForm.amount = null
    withdrawForm.withdraw_method = ''
    withdrawForm.withdraw_account = ''
    withdrawForm.remark = ''
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const getAmountValue = (row: Transaction) => {
  return typeof row.amount === 'number' ? row.amount : parseFloat(row.amount)
}

const getAmountClass = (row: Transaction) => {
  const amount = getAmountValue(row)
  return amount >= 0 ? 'text-success' : 'text-danger'
}

const getAmountSign = (row: Transaction) => {
  const amount = getAmountValue(row)
  return amount >= 0 ? '+' : '-'
}

const getTransactionTypeTag = (type: string) => {
  const tagMap: Record<string, 'success' | 'warning' | 'info'> = {
    RECHARGE: 'success',
    WITHDRAW: 'warning',
    ORDER_PAYMENT: 'info',
    SERVICE_FEE: 'info',
  }
  return tagMap[type] || 'info'
}

const getTransactionTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    RECHARGE: '充值',
    WITHDRAW: '提现',
    ORDER_PAYMENT: '订单收支',
    SERVICE_FEE: '服务费',
  }
  return labelMap[type] || type
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, 'warning' | 'success' | 'danger'> = {
    PENDING: 'warning',
    COMPLETED: 'success',
    REJECTED: 'danger',
  }
  return typeMap[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    PENDING: '待审核',
    COMPLETED: '已完成',
    REJECTED: '已拒绝',
  }
  return labelMap[status] || status
}

onMounted(() => {
  fetchWallet()
  fetchTransactions()
})
</script>

<style scoped>
.page-container {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  color: #303133;
  margin: 0;
}

.wallet-card {
  margin-bottom: 20px;
}

.wallet-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.balance {
  display: flex;
  flex-direction: column;
}

.balance .label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.balance .amount {
  font-size: 36px;
  color: #f56c6c;
  font-weight: bold;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}
</style>
