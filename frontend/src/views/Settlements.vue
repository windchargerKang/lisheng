<template>
  <div class="page-container">
    <div class="page-header">
      <h2>结算管理</h2>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
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
        <el-form-item label="结算状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable>
            <el-option label="已付款" value="paid" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchSettlements">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表 -->
    <el-card>
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="supplier_name" label="供应商" width="150" />
        <el-table-column prop="order_no" label="采购订单号" width="180" />
        <el-table-column prop="amount" label="结算金额" width="120">
          <template #default="{ row }">
            ¥{{ row.amount.toFixed(2) }}
          </template>
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
  supplier_id: number
  supplier_name: string
  order_id: number
  order_no: string
  amount: number
  type: string
  status: string
  paid_at: string | null
  created_at: string
}

interface Supplier {
  id: number
  name: string
}

const tableData = ref<Settlement[]>([])
const suppliers = ref<Supplier[]>([])
const loading = ref(false)

const filterForm = reactive({
  supplier_id: null as number | null,
  status: '',
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

const fetchSuppliers = async () => {
  try {
    const response = await apiClient.get('/suppliers', {
      params: { page: 1, page_size: 100 },
    })
    suppliers.value = response.data.items
  } catch (error: any) {
    console.error('加载供应商失败', error)
  }
}

const fetchSettlements = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/purchase-inbounds/settlements', {
      params: {
        page: pagination.page,
        page_size: pagination.page_size,
        supplier_id: filterForm.supplier_id || undefined,
        status: filterForm.status || undefined,
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
  fetchSuppliers()
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

.filter-card {
  margin-bottom: 20px;
}
</style>
