<template>
  <div class="page-container">
    <div class="page-header">
      <h2>采购订单管理</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        创建订单
      </el-button>
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
        <el-form-item label="供应商">
          <el-select v-model="filterForm.supplier_id" placeholder="全部" clearable>
            <el-option
              v-for="s in suppliers"
              :key="s.id"
              :label="s.name"
              :value="s.id"
            />
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
        <el-table-column prop="supplier_name" label="供应商" width="150" />
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
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">详情</el-button>
            <el-button
              v-if="row.status === 'pending'"
              link
              type="success"
              @click="handleConfirm(row)"
            >
              确认
            </el-button>
            <el-button
              v-if="['pending', 'confirmed'].includes(row.status)"
              link
              type="danger"
              @click="handleCancel(row)"
            >
              取消
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import apiClient from '@/api'

interface Order {
  id: number
  order_no: string
  supplier_id: number
  supplier_name: string
  total_amount: number
  status: string
  created_at: string
}

interface Supplier {
  id: number
  name: string
}

const router = useRouter()
const tableData = ref<Order[]>([])
const suppliers = ref<Supplier[]>([])
const loading = ref(false)
const dialogVisible = ref(false)

const filterForm = reactive({
  status: '',
  supplier_id: null as number | null,
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'warning',
    confirmed: 'success',
    completed: '',
    cancelled: 'danger',
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消',
  }
  return map[status] || status
}

const fetchSuppliers = async () => {
  try {
    const response = await apiClient.get('/suppliers', {
      params: { page: 1, page_size: 100, status: 'active' },
    })
    suppliers.value = response.data.items
  } catch (error: any) {
    console.error('加载供应商失败', error)
  }
}

const fetchOrders = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/purchase-orders', {
      params: {
        page: pagination.page,
        page_size: pagination.page_size,
        status: filterForm.status || undefined,
        supplier_id: filterForm.supplier_id || undefined,
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

const handleCreate = () => {
  router.push('/purchase-orders/create')
}

const handleView = (row: Order) => {
  router.push(`/purchase-orders/${row.id}`)
}

const handleConfirm = async (row: Order) => {
  try {
    await ElMessageBox.confirm(`确定要确认订单"${row.order_no}"吗？`, '确认订单', {
      type: 'warning',
    })
    await apiClient.put(`/purchase-orders/${row.id}/confirm`)
    ElMessage.success('订单已确认')
    fetchOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '确认失败')
    }
  }
}

const handleCancel = async (row: Order) => {
  try {
    await ElMessageBox.confirm(`确定要取消订单"${row.order_no}"吗？`, '取消订单', {
      type: 'warning',
    })
    await apiClient.post(`/purchase-orders/${row.id}/cancel`)
    ElMessage.success('订单已取消')
    fetchOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '取消失败')
    }
  }
}

onMounted(() => {
  fetchSuppliers()
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
