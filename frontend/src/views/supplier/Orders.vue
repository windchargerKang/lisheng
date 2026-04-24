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
            <el-option label="已确认" value="confirmed" />
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
        <el-table-column prop="total_amount" label="订单金额" width="120">
          <template #default="{ row }">¥{{ row.total_amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="订单状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getOrderStatusType(row.status)">
              {{ getOrderStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="supplier_confirm_status" label="供货确认" width="100">
          <template #default="{ row }">
            <el-tag :type="getConfirmStatusType(row.supplier_confirm_status)">
              {{ getConfirmStatusText(row.supplier_confirm_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">详情</el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api'

interface Order {
  id: number
  order_no: string
  total_amount: number
  status: string
  supplier_confirm_status: string | null
  created_at: string
}

const tableData = ref<Order[]>([])
const loading = ref(false)

const filterForm = reactive({
  status: '',
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

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

const fetchOrders = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/supplier-portal/orders', {
      params: {
        page: pagination.page,
        page_size: pagination.page_size,
        status: filterForm.status || undefined,
      },
    })
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error('加载订单数据失败')
  } finally {
    loading.value = false
  }
}

const handleView = (row: Order) => {
  window.location.href = `/supplier-portal/orders/${row.id}`
}

onMounted(() => {
  fetchOrders()
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
</style>
