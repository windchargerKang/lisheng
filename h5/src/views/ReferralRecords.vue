<template>
  <div class="referral-records-page">
    <van-nav-bar
      title="分享记录"
      left-arrow
      @click-left="$router.back()"
    />

    <van-list
      v-model:loading="loading"
      :finished="finished"
      finished-text="没有更多记录了"
      @load="onLoad"
    >
      <van-cell
        v-for="item in records"
        :key="item.id"
        :title="`被推荐人：${item.referee_username}`"
        :label="`分享类型：${getReferrerTypeText(item.referrer_type)}`"
      >
        <template #right-icon>
          <span class="record-time">{{ formatDate(item.created_at) }}</span>
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
const records = ref<any[]>([])

const getReferrerTypeText = (type: string): string => {
  const textMap: Record<string, string> = {
    customer: '客户',
    shop: '店铺',
    agent: '区代',
  }
  return textMap[type] || type
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const params = {
      page: 1,
      page_size: 10,
    }
    const response = await apiClient.get('/referral/records', { params })
    records.value = response.data.items || []
    finished.value = records.value.length < 10
  } catch (error) {
    console.error('获取分享记录失败:', error)
  } finally {
    loading.value = false
  }
}

const onLoad = () => {
  fetchRecords()
}
</script>

<style scoped>
.referral-records-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.record-time {
  font-size: 12px;
  color: #969799;
}
</style>
