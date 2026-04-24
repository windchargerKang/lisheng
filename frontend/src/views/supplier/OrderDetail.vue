<template>
  <div class="page-container">
    <div class="page-header">
      <h2>订单详情</h2>
      <el-button @click="goBack">返回</el-button>
    </div>

    <el-card>
      <el-descriptions title="订单信息" :column="2" border>
        <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">¥{{ order.total_amount?.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getOrderStatusType(order.status)">
            {{ getOrderStatusText(order.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="供货确认">
          <el-tag :type="getConfirmStatusType(order.supplier_confirm_status)">
            {{ getConfirmStatusText(order.supplier_confirm_status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ order.created_at }}</el-descriptions-item>
        <el-descriptions-item label="运营确认时间">{{ order.confirmed_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="供应商确认时间">{{ order.supplier_confirmed_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ order.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>订单明细</template>
      <el-table :data="order.items" border>
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="cost_price" label="采购单价" width="120">
          <template #default="{ row }">¥{{ row.cost_price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="subtotal" label="小计" width="120">
          <template #default="{ row }">¥{{ row.subtotal?.toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 操作按钮 -->
    <el-card style="margin-top: 20px">
      <el-button
        v-if="order.supplier_confirm_status === 'pending' || !order.supplier_confirm_status"
        type="success"
        @click="handleConfirm"
      >
        确认供货
      </el-button>
      <el-button
        v-if="order.supplier_confirm_status === 'pending' || !order.supplier_confirm_status"
        type="warning"
        @click="showRejectDialog"
      >
        申请修改
      </el-button>
    </el-card>

    <!-- 申请修改对话框 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="申请修改订单"
      width="500px"
    >
      <el-form :model="rejectForm" :rules="rejectRules" ref="rejectFormRef" label-width="100px">
        <el-form-item label="修改原因" prop="reason">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请说明需要修改的内容和原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitReject" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import apiClient from '@/api'

const route = useRoute()
const router = useRouter()
const order = ref<any>({})
const rejectDialogVisible = ref(false)
const submitting = ref(false)
const rejectFormRef = ref()

const rejectForm = reactive({
  reason: '',
})

const rejectRules = {
  reason: [{ required: true, message: '请输入修改原因', trigger: 'blur' }],
}

const getOrderStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'warning',
    confirmed: 'success',
    completed: '',
    cancelled: 'danger',
  }
  return map[status] || ''
}

const getOrderStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消',
  }
  return map[status] || status
}

const getConfirmStatusType = (status: string | null) => {
  if (!status) return 'info'
  const map: Record<string, any> = {
    pending: 'warning',
    confirmed: 'success',
    rejected: 'danger',
  }
  return map[status] || ''
}

const getConfirmStatusText = (status: string | null) => {
  if (!status) return '待确认'
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    rejected: '已拒绝',
  }
  return map[status] || status
}

const fetchOrder = async () => {
  try {
    const response = await apiClient.get(`/supplier-portal/orders/${route.params.id}`)
    order.value = response.data
  } catch (error: any) {
    ElMessage.error('加载订单详情失败')
  }
}

const handleConfirm = async () => {
  try {
    await ElMessageBox.confirm('确定要确认此订单的供货吗？', '确认供货', {
      type: 'warning',
    })
    await apiClient.post(`/supplier-portal/orders/${route.params.id}/confirm`)
    ElMessage.success('已确认供货')
    fetchOrder()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '确认失败')
    }
  }
}

const showRejectDialog = () => {
  rejectForm.reason = ''
  rejectDialogVisible.value = true
}

const handleSubmitReject = async () => {
  await rejectFormRef.value?.validate()
  submitting.value = true
  try {
    await apiClient.post(`/supplier-portal/orders/${route.params.id}/reject`, {
      reason: rejectForm.reason,
    })
    ElMessage.success('修改申请已提交，等待运营审批')
    rejectDialogVisible.value = false
    fetchOrder()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchOrder()
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
</style>
