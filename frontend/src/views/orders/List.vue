<template>
  <div class="page-container">
    <div class="page-header">
      <h2>订单管理</h2>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="订单状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable>
            <el-option label="待确认" value="pending" />
            <el-option label="待发货" value="confirmed" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchOrders">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表 -->
    <el-card>
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="user_id" label="用户 ID" width="80" />
        <el-table-column prop="total_amount" label="订单金额" width="100">
          <template #default="{ row }">
            ¥{{ row.total_amount.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="receiver_name" label="收货人" width="100" />
        <el-table-column prop="courier_no" label="物流单号" width="150" />
        <el-table-column prop="created_at" label="下单时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">详情</el-button>
            <el-button
              v-if="row.status === 'confirmed'"
              link
              type="success"
              @click="handleShip(row)"
            >
              发货
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchOrders"
        @size-change="fetchOrders"
        style="margin-top: 20px; justify-content: flex-end"
      />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import apiClient from '@/api'

const router = useRouter()
const tableData = ref<any[]>([])
const loading = ref(false)

const filterForm = reactive({
  status: '',
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})

const shipDialogVisible = ref(false)
const currentOrder = ref<any>(null)
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

const fetchOrders = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.page_size,
    }
    if (filterForm.status) {
      params.status = filterForm.status
    }

    const response = await apiClient.get('/admin/orders', { params })
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载订单列表失败')
  } finally {
    loading.value = false
  }
}

const handleView = (row: any) => {
  router.push(`/orders/${row.id}`)
}

const handleShip = (row: any) => {
  currentOrder.value = row
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
    await apiClient.post(`/admin/orders/${currentOrder.value.id}/ship`, shipForm)
    ElMessage.success('发货成功')
    shipDialogVisible.value = false
    fetchOrders()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '发货失败')
  }
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 20px;
}
</style>
