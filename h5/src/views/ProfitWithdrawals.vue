<template>
  <div class="withdrawals-page">
    <van-nav-bar
      title="提现记录"
      left-arrow
      @click-left="$router.back()"
    />

    <van-tabs v-model:active="activeTab" @change="handleTabChange">
      <van-tab name="all" title="全部" />
      <van-tab name="pending" title="待审核" />
      <van-tab name="approved" title="已通过" />
      <van-tab name="rejected" title="已拒绝" />
    </van-tabs>

    <van-list
      v-model:loading="loading"
      :finished="finished"
      finished-text="没有更多记录了"
      @load="onLoad"
    >
      <van-card
        v-for="item in withdrawals"
        :key="item.id"
        :price="item.amount"
        currency="¥"
      >
        <template #title>
          <div class="withdrawal-title">提现申请</div>
        </template>
        <template #tags>
          <van-tag :type="getStatusType(item.status)">
            {{ getStatusText(item.status) }}
          </van-tag>
        </template>
        <template #num>
          <div class="withdrawal-time">
            {{ formatDate(item.created_at) }}
          </div>
        </template>
        <template #desc>
          <div v-if="item.remark" class="withdrawal-remark">
            备注：{{ item.remark }}
          </div>
        </template>
      </van-card>
    </van-list>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import apiClient from '@/api'

const loading = ref(false)
const finished = ref(false)
const activeTab = ref('all')
const withdrawals = ref<any[]>([])

const getStatusType = (status: string): string => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
  }
  return typeMap[status] || 'default'
}

const getStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
  }
  return textMap[status] || status
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const handleTabChange = () => {
  fetchWithdrawals()
}

const fetchWithdrawals = async () => {
  loading.value = true
  try {
    const params: any = {
      page: 1,
      page_size: 10,
    }
    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }

    const response = await apiClient.get('/profit/withdrawals', { params })
    withdrawals.value = response.data.items || []
    finished.value = withdrawals.value.length < 10
  } catch (error) {
    console.error('获取提现记录失败:', error)
  } finally {
    loading.value = false
  }
}

const onLoad = () => {
  fetchWithdrawals()
}
</script>

<style scoped>
.withdrawals-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.withdrawal-title {
  font-size: 15px;
  font-weight: bold;
}

.withdrawal-time {
  font-size: 12px;
  color: #969799;
}

.withdrawal-remark {
  font-size: 13px;
  color: #969799;
  margin-top: 4px;
}
</style>
