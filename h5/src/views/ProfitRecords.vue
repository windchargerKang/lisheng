<template>
  <div class="profit-records-page">
    <van-nav-bar
      title="收益明细"
      left-arrow
      @click-left="$router.back()"
    />

    <van-tabs v-model:active="activeTab" @change="handleTabChange">
      <van-tab name="all" title="全部" />
      <van-tab name="pending" title="待结算" />
      <van-tab name="paid" title="已结算" />
      <van-tab name="withdrawn" title="已提现" />
    </van-tabs>

    <van-list
      v-model:loading="loading"
      :finished="finished"
      finished-text="没有更多记录了"
      @load="onLoad"
    >
      <van-cell
        v-for="item in records"
        :key="item.id"
        :title="`订单号：${item.order_id || '-'}`"
        :value="`+¥${item.amount}`"
        value-class="amount-positive"
      >
        <template #label>
          <div class="record-info">
            <span>{{ formatDate(item.created_at) }}</span>
            <van-tag :type="getStatusType(item.status)">
              {{ getStatusText(item.status) }}
            </van-tag>
          </div>
        </template>
      </van-cell>
    </van-list>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import apiClient from '@/api'

const loading = ref(false)
const finished = ref(false)
const activeTab = ref('all')
const records = ref<any[]>([])

const getStatusType = (status: string): string => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    paid: 'success',
    withdrawn: 'primary',
  }
  return typeMap[status] || 'default'
}

const getStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    pending: '待结算',
    paid: '已结算',
    withdrawn: '已提现',
  }
  return textMap[status] || status
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const handleTabChange = () => {
  fetchRecords()
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const params: any = {
      page: 1,
      page_size: 10,
    }
    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }

    const response = await apiClient.get('/profit/records', { params })
    records.value = response.data.items || []
    finished.value = records.value.length < 10
  } catch (error) {
    console.error('获取收益记录失败:', error)
  } finally {
    loading.value = false
  }
}

const onLoad = () => {
  fetchRecords()
}
</script>

<style scoped>
.profit-records-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.record-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount-positive {
  color: #07c160;
  font-weight: bold;
}
</style>
