<template>
  <div class="orders-page">
    <van-tabs v-model:active="activeTab" @change="handleTabChange">
      <van-tab name="all" title="全部" />
      <van-tab name="pending" title="待确认" />
      <van-tab name="confirmed" title="待发货" />
      <van-tab name="shipped" title="已发货" />
      <van-tab name="completed" title="已完成" />
    </van-tabs>

    <van-list
      v-model:loading="loading"
      :finished="finished"
      finished-text="没有更多订单了"
      @load="onLoad"
    >
      <van-card
        v-for="order in orders"
        :key="order.id"
        :price="order.total_amount"
        :title="`订单号：${order.order_no}`"
        :num="order.items_count"
        @click="goToDetail(order.id)"
      >
        <template #tags>
          <van-tag :type="getStatusType(order.status)">
            {{ getStatusText(order.status) }}
          </van-tag>
        </template>
      </van-card>
    </van-list>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api'

const router = useRouter()
const loading = ref(false)
const finished = ref(false)
const activeTab = ref('all')
const orders = ref<any[]>([])
const currentPage = ref(1)
const total = ref(0)

const getStatusType = (status: string): string => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    confirmed: 'primary',
    shipped: 'success',
    completed: 'success',
    verified: 'success',
  }
  return typeMap[status] || 'default'
}

const getStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    pending: '待确认',
    confirmed: '待发货',
    shipped: '已发货',
    completed: '已完成',
    verified: '已核销',
    cancelled: '已取消',
  }
  return textMap[status] || status
}

const handleTabChange = () => {
  // 切换 tab 时重置分页
  currentPage.value = 1
  orders.value = []
  finished.value = false
  fetchOrders()
}

const goToDetail = (id: number) => {
  router.push(`/orders/${id}`)
}

const fetchOrders = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: 10,
    }
    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }

    const response = await apiClient.get('/orders', { params })
    // 累计加载订单
    orders.value = currentPage.value === 1
      ? (response.data.items || [])
      : [...orders.value, ...(response.data.items || [])]

    total.value = response.data.total || 0
    // 判断是否加载完毕
    finished.value = orders.value.length >= total.value

    // 准备下一页
    if (!finished.value) {
      currentPage.value++
    }
  } catch (error) {
    console.error('获取订单列表失败:', error)
  } finally {
    loading.value = false
  }
}

const onLoad = () => {
  fetchOrders()
}
</script>

<style scoped>
.orders-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 50px 0 20px;
  position: relative;
}

/* 顶部毛玻璃效果 */
.orders-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 100;
}
</style>
