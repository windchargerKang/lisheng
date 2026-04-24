<template>
  <div class="page-container">
    <div class="page-header">
      <h2>结算记录</h2>
    </div>

    <!-- 列表 -->
    <el-card>
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="order_no" label="采购订单号" width="180" />
        <el-table-column prop="amount" label="结算金额" width="120">
          <template #default="{ row }">¥{{ row.amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="type" label="结算方式" width="100">
          <template #default="{ row }">
            {{ row.type === 'cash' ? '现款' : '账期' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag type="success">{{ row.status === 'paid' ? '已付款' : row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="paid_at" label="付款时间" width="180" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchSettlements"
        @size-change="fetchSettlements"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api'

interface Settlement {
  id: number
  order_id: number
  order_no: string
  amount: number
  type: string
  status: string
  paid_at: string | null
  created_at: string
}

const tableData = ref<Settlement[]>([])
const loading = ref(false)

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

const fetchSettlements = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/supplier-portal/settlements', {
      params: {
        page: pagination.page,
        page_size: pagination.page_size,
      },
    })
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error('加载结算数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchSettlements()
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
