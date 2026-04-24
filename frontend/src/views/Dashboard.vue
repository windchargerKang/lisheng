<template>
  <div class="dashboard">
    <h2>欢迎使用渠道销售管理系统</h2>
    <el-row :gutter="20" style="margin-top: 30px">
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <el-icon :size="40" color="#409EFF"><Shop /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.shopCount }}</div>
              <div class="stat-label">店铺总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <el-icon :size="40" color="#67C23A"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.agentCount }}</div>
              <div class="stat-label">区代总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <el-icon :size="40" color="#E6A23C"><Goods /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.productCount }}</div>
              <div class="stat-label">产品总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <el-icon :size="40" color="#F56C6C"><Location /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.regionCount }}</div>
              <div class="stat-label">区域总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api'

const stats = ref({
  shopCount: 0,
  agentCount: 0,
  productCount: 0,
  regionCount: 0
})

const fetchStats = async () => {
  try {
    // 获取店铺数量
    const shopsResponse = await apiClient.get('/shops', { params: { page: 1, page_size: 1 } })
    stats.value.shopCount = shopsResponse.data.total || 0

    // 获取区代数量
    const agentsResponse = await apiClient.get('/agents', { params: { page: 1, page_size: 1 } })
    stats.value.agentCount = agentsResponse.data.total || 0

    // 获取产品数量
    const productsResponse = await apiClient.get('/products', { params: { page: 1, page_size: 1 } })
    stats.value.productCount = productsResponse.data.total || 0

    // 获取区域数量 (区域 API 返回树形结构，计算数组长度)
    const regionsResponse = await apiClient.get('/regions')
    const regions = regionsResponse.data.regions || []
    // 递归计算所有区域数量
    const countRegions = (list: any[]): number => {
      let count = list.length
      for (const item of list) {
        if (item.children && item.children.length > 0) {
          count += countRegions(item.children)
        }
      }
      return count
    }
    stats.value.regionCount = countRegions(regions)
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard h2 {
  color: #303133;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
</style>
