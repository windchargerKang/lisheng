<template>
  <div class="page-container">
    <div class="page-header">
      <h2>入库管理</h2>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="采购订单">
          <el-input
            v-model="filterForm.order_id"
            placeholder="输入订单 ID"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchInbounds">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表 -->
    <el-card>
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="order_no" label="采购订单号" width="180" />
        <el-table-column prop="supplier_name" label="供应商" width="150" />
        <el-table-column prop="total_quantity" label="入库数量" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag type="success">{{ row.status === 'completed' ? '已完成' : row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="warehouse_operator_id" label="入库操作人" width="100" />
        <el-table-column prop="created_at" label="入库时间" width="180" />
        <el-table-column label="操作" width="120" fixed="right">
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
        @current-change="fetchInbounds"
        @size-change="fetchInbounds"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api'

interface Inbound {
  id: number
  order_id: number
  order_no: string
  supplier_id: number
  supplier_name: string
  total_quantity: number
  warehouse_operator_id: number | null
  status: string
  created_at: string
}

const tableData = ref<Inbound[]>([])
const loading = ref(false)

const filterForm = reactive({
  order_id: null as number | null,
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

const fetchInbounds = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/purchase-inbounds', {
      params: {
        page: pagination.page,
        page_size: pagination.page_size,
        order_id: filterForm.order_id || undefined,
      },
    })
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error('加载入库数据失败')
  } finally {
    loading.value = false
  }
}

const handleView = (row: Inbound) => {
  // 跳转到对应的订单详情页
  window.location.href = `/purchase-orders/${row.order_id}`
}

onMounted(() => {
  fetchInbounds()
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
