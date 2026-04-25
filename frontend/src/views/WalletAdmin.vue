<template>
  <div class="page-container">
    <div class="page-header">
      <h2>钱包管理</h2>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="用户 ID">
          <el-input-number v-model="filterForm.user_id" :min="1" placeholder="用户 ID" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchWallets">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 钱包列表 -->
    <el-card class="table-card">
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column prop="id" label="钱包 ID" width="100" />
        <el-table-column prop="user_id" label="用户 ID" width="100" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="balance" label="余额" width="120">
          <template #default="{ row }">
            <span class="text-price">¥{{ row.balance }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleRecharge(row)">代客充值</el-button>
            <el-button link type="success" @click="handleViewTransactions(row)">流水记录</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @change="fetchWallets"
        />
      </div>
    </el-card>

    <!-- 代客充值对话框 -->
    <el-dialog v-model="rechargeDialogVisible" title="代客充值" width="500px">
      <el-form :model="rechargeForm" :rules="rechargeRules" ref="rechargeFormRef" label-width="100px">
        <el-form-item label="用户 ID" prop="user_id">
          <el-input-number v-model="rechargeForm.user_id" :min="1" disabled style="width: 100%" />
        </el-form-item>
        <el-form-item label="当前余额" prop="current_balance">
          <el-input :model-value="currentBalance" disabled style="width: 100%" />
        </el-form-item>
        <el-form-item label="充值金额" prop="amount">
          <el-input-number v-model="rechargeForm.amount" :min="0.01" :precision="2" :step="0.01" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="rechargeForm.remark" type="textarea" :rows="3" placeholder="备注（可选）" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rechargeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRechargeSubmit" :loading="rechargeSubmitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 流水记录对话框 -->
    <el-dialog v-model="transactionsDialogVisible" title="流水记录" width="800px">
      <el-form :inline="true" :model="transactionsFilter">
        <el-form-item label="类型">
          <el-select v-model="transactionsFilter.transaction_type" placeholder="全部类型" clearable style="width: 120px">
            <el-option label="充值" value="RECHARGE" />
            <el-option label="提现" value="WITHDRAW" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="transactionsFilter.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="待审核" value="PENDING" />
            <el-option label="已完成" value="COMPLETED" />
            <el-option label="已拒绝" value="REJECTED" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchTransactions">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="transactionsData" border v-loading="transactionsLoading">
        <el-table-column prop="transaction_no" label="流水号" width="180" />
        <el-table-column prop="transaction_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.transaction_type === 'RECHARGE' ? 'success' : 'warning'">
              {{ row.transaction_type === 'RECHARGE' ? '充值' : '提现' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            <span :class="getAmountClass(row)">
              {{ getAmountSign(row) }}¥{{ Math.abs(row.amount) }}
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
        <el-table-column prop="withdraw_method" label="提现方式" width="120" />
        <el-table-column prop="withdraw_account" label="提现账号" width="150" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right" v-if="showAuditAction">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'PENDING'"
              link
              type="success"
              @click="handleApproveWithdraw(row, true)"
            >
              通过
            </el-button>
            <el-button
              v-if="row.status === 'PENDING'"
              link
              type="danger"
              @click="handleApproveWithdraw(row, false)"
            >
              拒绝
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="transactionsPagination.page"
          v-model:page-size="transactionsPagination.page_size"
          :total="transactionsPagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @change="fetchTransactions"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
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
  amount: number | string
  balance_after: string
  transaction_no: string
  status: 'PENDING' | 'COMPLETED' | 'REJECTED'
  withdraw_method?: string
  withdraw_account?: string
  remark?: string
  created_at: string
}

const loading = ref(false)
const tableData = ref<Wallet[]>([])

const filterForm = reactive({
  user_id: null as number | null,
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

// 代客充值
const rechargeDialogVisible = ref(false)
const rechargeSubmitting = ref(false)
const rechargeFormRef = ref()
const currentBalance = ref('0.00')

const rechargeForm = reactive({
  user_id: null as number | null,
  amount: null as number | null,
  remark: '',
})

const rechargeRules = {
  user_id: [{ required: true, message: '用户 ID 不能为空', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入充值金额', trigger: 'blur' }],
}

// 流水记录
const transactionsDialogVisible = ref(false)
const transactionsLoading = ref(false)
const transactionsData = ref<Transaction[]>([])
const currentWalletId = ref<number | null>(null)

const transactionsFilter = reactive({
  transaction_type: '' as string | null,
  status: '' as string | null,
})

const transactionsPagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

const showAuditAction = computed(() => {
  // 只有待审核的提现才显示审核操作
  return transactionsData.value.some((row) => row.status === 'PENDING')
})

const fetchWallets = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: pagination.page,
      page_size: pagination.page_size,
    }
    if (filterForm.user_id) params.user_id = filterForm.user_id

    const response = await apiClient.get('/wallet/admin/wallets', { params })
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error('加载钱包数据失败')
  } finally {
    loading.value = false
  }
}

const handleRecharge = (row: Wallet) => {
  rechargeForm.user_id = row.user_id
  currentBalance.value = row.balance
  rechargeDialogVisible.value = true
}

const handleRechargeSubmit = async () => {
  await rechargeFormRef.value?.validate()
  rechargeSubmitting.value = true

  try {
    await apiClient.post('/wallet/recharge', {
      user_id: rechargeForm.user_id,
      amount: rechargeForm.amount,
      remark: rechargeForm.remark || undefined,
    })
    ElMessage.success('充值成功')
    rechargeDialogVisible.value = false
    fetchWallets()
    // 重置表单
    rechargeForm.user_id = null
    rechargeForm.amount = null
    rechargeForm.remark = ''
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '充值失败')
  } finally {
    rechargeSubmitting.value = false
  }
}

const handleViewTransactions = (row: Wallet) => {
  currentWalletId.value = row.id
  transactionsDialogVisible.value = true
  fetchTransactions()
}

const fetchTransactions = async () => {
  transactionsLoading.value = true
  try {
    const params: Record<string, any> = {
      page: transactionsPagination.page,
      page_size: transactionsPagination.page_size,
    }
    if (transactionsFilter.transaction_type) params.transaction_type = transactionsFilter.transaction_type
    if (transactionsFilter.status) params.status = transactionsFilter.status

    // 查询该钱包的流水
    const response = await apiClient.get(`/wallet/transactions`, {
      params: { ...params, wallet_id: currentWalletId.value },
    })
    transactionsData.value = response.data.items
    transactionsPagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error('加载流水记录失败')
  } finally {
    transactionsLoading.value = false
  }
}

const handleApproveWithdraw = async (row: Transaction, approved: boolean) => {
  try {
    await ElMessageBox.confirm(
      `确定要${approved ? '通过' : '拒绝'}该提现申请吗？`,
      '确认操作',
      { type: 'warning' }
    )

    await apiClient.post(`/wallet/withdraw/${row.id}/approve`, { approved })
    ElMessage.success(approved ? '审核通过' : '已拒绝')
    fetchTransactions()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

const getAmountClass = (row: Transaction) => {
  // 根据金额正负判断颜色：正数为收入（绿色），负数为支出（红色）
  const amount = typeof row.amount === 'number' ? row.amount : parseFloat(row.amount)
  return amount >= 0 ? 'text-success' : 'text-danger'
}

const getAmountSign = (row: Transaction) => {
  // 根据金额正负判断符号
  const amount = typeof row.amount === 'number' ? row.amount : parseFloat(row.amount)
  return amount >= 0 ? '+' : '-'
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
  fetchWallets()
})
</script>

<style scoped>
.page-container {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  color: #303133;
  margin: 0;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.text-price {
  color: #f56c6c;
  font-weight: bold;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}
</style>
