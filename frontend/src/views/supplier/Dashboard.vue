<template>
  <div class="supplier-dashboard">
    <h2>供应商门户</h2>

    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.pendingOrders }}</div>
            <div class="stat-label">待确认订单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.confirmedOrders }}</div>
            <div class="stat-label">已确认订单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.completedOrders }}</div>
            <div class="stat-label">已完成订单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">¥{{ stats.settlementAmount?.toFixed(2) || '0.00' }}</div>
            <div class="stat-label">结算金额</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>待处理订单</span>
              <el-button link type="primary" @click="$router.push('/supplier-portal/orders')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="pendingOrders" style="width: 100%">
            <el-table-column prop="order_no" label="订单号" />
            <el-table-column prop="total_amount" label="金额">
              <template #default="{ row }">¥{{ row.total_amount?.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="{ row }">
                <el-button link type="primary" @click="$router.push(`/supplier-portal/orders/${row.id}`)">处理</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近结算</span>
              <el-button link type="primary" @click="$router.push('/supplier-portal/settlements')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentSettlements" style="width: 100%">
            <el-table-column prop="order_no" label="订单号" />
            <el-table-column prop="amount" label="金额">
              <template #default="{ row }">¥{{ row.amount?.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag type="success">{{ row.status === 'paid' ? '已付款' : row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api'

const stats = reactive({
  pendingOrders: 0,
  confirmedOrders: 0,
  completedOrders: 0,
  settlementAmount: 0,
})

const pendingOrders = ref<any[]>([])
const recentSettlements = ref<any[]>([])

const fetchStats = async () => {
  try {
    // 获取订单统计
    const ordersResponse = await apiClient.get('/supplier-portal/orders', {
      params: { page: 1, page_size: 100 },
    })
    const orders = ordersResponse.data.items
    stats.pendingOrders = orders.filter((o: any) => o.supplier_confirm_status === 'pending').length
    stats.confirmedOrders = orders.filter((o: any) => o.supplier_confirm_status === 'confirmed').length
    stats.completedOrders = orders.filter((o: any) => o.status === 'completed').length

    // 获取待处理订单
    pendingOrders.value = orders
      .filter((o: any) => o.supplier_confirm_status === 'pending')
      .slice(0, 5)

    // 获取最近结算
    const settlementsResponse = await apiClient.get('/supplier-portal/settlements', {
      params: { page: 1, page_size: 5 },
    })
    recentSettlements.value = settlementsResponse.data.items
    stats.settlementAmount = settlementsResponse.data.items.reduce((sum: number, s: any) => sum + s.amount, 0)
  } catch (error: any) {
    ElMessage.error('加载数据失败')
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.supplier-dashboard h2 {
  margin-bottom: 20px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 10px 0;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  color: #909399;
  margin-top: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
