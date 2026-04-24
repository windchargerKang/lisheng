<template>
  <div class="products-page">
    <van-search
      v-model="searchQuery"
      placeholder="搜索商品"
      shape="round"
      @search="handleSearch"
    />

    <van-tabs v-model:active="activeTab" @change="handleTabChange">
      <van-tab name="all" title="全部" />
      <van-tab name="category" title="分类" />
    </van-tabs>

    <van-list
      v-model:loading="loading"
      :finished="finished"
      finished-text="没有更多了"
      @load="onLoad"
    >
      <van-card
        v-for="item in products"
        :key="item.id"
        :price="getPrice(item)"
        :title="item.name"
        :thumb="item.image_url || item.image"
        :desc="item.description"
        @click="goToDetail(item.id)"
      >
        <template #tags>
          <van-tag plain type="primary" v-if="item.is_new">新品</van-tag>
        </template>
      </van-card>
    </van-list>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores'
import apiClient from '@/api'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const searchQuery = ref('')
const loading = ref(false)
const finished = ref(false)
const activeTab = ref('all')
const products = ref<any[]>([])

const getPrice = (item: any) => {
  // 后端已根据用户角色过滤价格，直接返回第一个价格即可
  // 管理员看到三个价格，返回第一个（retail）
  return item.prices?.[0]?.price || 0
}

const handleSearch = () => {
  fetchProducts()
}

const handleTabChange = () => {
  fetchProducts()
}

const goToDetail = (id: number) => {
  router.push(`/products/${id}`)
}

const fetchProducts = async () => {
  loading.value = true
  try {
    const params: any = {
      page: 1,
      page_size: 10,
    }
    if (searchQuery.value) {
      params.keyword = searchQuery.value
    }
    if (activeTab.value === 'category') {
      // TODO: 添加分类筛选
    }

    const response = await apiClient.get('/products', { params })
    products.value = response.data.items || []
    finished.value = products.value.length < 10
  } catch (error) {
    console.error('获取产品列表失败:', error)
  } finally {
    loading.value = false
  }
}

const onLoad = () => {
  fetchProducts()
}

onMounted(() => {
  if (route.query.keyword) {
    searchQuery.value = route.query.keyword as string
  }
})
</script>

<style scoped>
.products-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}
</style>
