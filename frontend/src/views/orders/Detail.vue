<template>
  <div class="page-container">
    <div class="page-header">
      <h2>订单详情</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>

    <el-card v-if="order" v-loading="loading">
      <el-descriptions title="订单信息" :column="2" border>
        <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getStatusType(order.status)">
            {{ getStatusText(order.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="下单时间">{{ order.created_at }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">¥{{ order.total_amount.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="收货人">{{ order.receiver_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ order.receiver_phone }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ order.receiver_address }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ order.remark || '无' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <el-descriptions title="物流信息" :column="2" border v-if="order.courier_company || order.courier_no">
        <el-descriptions-item label="物流公司">{{ order.courier_company || '-' }}</el-descriptions-item>
        <el-descriptions-item label="物流单号">{{ order.courier_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="发货时间">{{ order.shipped_at || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-alert v-else title="该订单尚未发货" type="warning" :closable="false" />

      <el-divider />

      <h3>商品明细</h3>
      <el-table :data="order.items" border>
        <el-table-column prop="product_id" label="商品 ID" width="100" />
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="{ row }">
            ¥{{ row.unit_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="subtotal" label="小计" width="100">
          <template #default="{ row }">
            ¥{{ row.subtotal.toFixed(2) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 操作按钮 -->
      <div class="action-buttons" v-if="order.status === 'confirmed'">
        <el-button type="primary" @click="handleShip">发货</el-button>
      </div>
    </el-card>

    <!-- 发货弹窗 -->
    <el-dialog
      v-model="shipDialogVisible"
      title="订单发货"
      width="500px"
    >
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="物流公司" required>
          <el-input v-model="shipForm.courier_company" placeholder="如：顺丰速运" />
        </el-form-item>
        <el-form-item label="物流单号" required>
          <el-input v-model="shipForm.courier_no" placeholder="如：SF1234567890" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shipDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmShip">确认发货</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import apiClient from '@/api'

const route = useRoute()
const router = useRouter()
const order = ref<any>(null)
const loading = ref(false)

const shipDialogVisible = ref(false)
const shipForm = reactive({
  courier_company: '',
  courier_no: '',
})

const getStatusType = (status: string): string => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    confirmed: 'primary',
    shipped: 'success',
    completed: '',
    cancelled: 'info',
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    pending: '待确认',
    confirmed: '待发货',
    shipped: '已发货',
    completed: '已完成',
    cancelled: '已取消',
  }
  return textMap[status] || status
}

const fetchOrderDetail = async () => {
  loading.value = true
  try {
    const orderId = route.params.id
    const response = await apiClient.get(`/admin/orders/${orderId}`)
    order.value = response.data
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载订单详情失败')
  } finally {
    loading.value = false
  }
}

const handleShip = () => {
  shipForm.courier_company = ''
  shipForm.courier_no = ''
  shipDialogVisible.value = true
}

const confirmShip = async () => {
  if (!shipForm.courier_company || !shipForm.courier_no) {
    ElMessage.warning('请填写物流公司和物流单号')
    return
  }

  try {
    const orderId = route.params.id
    await apiClient.post(`/admin/orders/${orderId}/ship`, shipForm)
    ElMessage.success('发货成功')
    shipDialogVisible.value = false
    fetchOrderDetail()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '发货失败')
  }
}

onMounted(() => {
  fetchOrderDetail()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

h3 {
  margin: 16px 0;
}
</style>
