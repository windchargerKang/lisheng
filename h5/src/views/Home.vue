<template>
  <div class="home-page">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-input">
        <span class="search-icon">🔍</span>
        <input v-model="searchQuery" placeholder="搜索药品、症状、品牌" @keyup.enter="handleSearch" />
      </div>
    </div>

    <!-- 轮播图 -->
    <div class="banner-section">
      <van-swipe :autoplay="3000" indicator-color="white" class="banner-swipe">
        <van-swipe-item v-for="(item, index) in banners" :key="index">
          <div class="banner-item" :style="{ background: item.bgColor }">
            <div class="banner-content">
              <div class="banner-title">{{ item.title }}</div>
              <div class="banner-subtitle">{{ item.subtitle }}</div>
              <button class="banner-btn">立即选购</button>
            </div>
          </div>
        </van-swipe-item>
      </van-swipe>
    </div>

    <!-- 功能图标 -->
    <div class="icon-grid">
      <div class="icon-item" v-for="(item, index) in icons" :key="index" @click="handleIconClick(item)">
        <div class="icon-bg" :style="{ backgroundColor: item.color }">
          <span class="icon">{{ item.icon }}</span>
        </div>
        <span class="icon-text">{{ item.name }}</span>
      </div>
    </div>

    <!-- 推荐产品 -->
    <div class="product-section">
      <div class="section-header">
        <h3 class="section-title">推荐产品</h3>
        <span class="section-more" @click="$router.push('/products')">查看更多 ></span>
      </div>
      <div class="product-list">
        <div class="product-item" v-for="item in products" :key="item.id" @click="goToDetail(item.id)">
          <div class="product-image">
            <img :src="item.image_url || item.image || '/placeholder.png'" alt="" />
          </div>
          <div class="product-info">
            <div class="product-name">{{ item.name }}</div>
            <div class="product-desc">{{ item.description }}</div>
            <div class="product-price">¥{{ getPrice(item) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部提示 -->
    <div class="page-footer">
      <div class="footer-content">
        <span class="footer-icon">🌸</span>
        <span class="footer-text">已经到底啦～</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import apiClient from '@/api'

const router = useRouter()
const userStore = useUserStore()
const searchQuery = ref('')
const products = ref<any[]>([])

const banners = ref([
  {
    title: '健康生活每一天',
    subtitle: '贴心好药伴您行',
    bgColor: 'linear-gradient(135deg, #FFB347 0%, #FFCC33 100%)'
  }
])

const icons = ref([
  { name: '全部商品', icon: '🏪', color: '#FF9500', path: '/products' },
  { name: '热销榜', icon: '🔥', color: '#FF6B6B', path: '/products?sort=hot' },
  { name: '新品上市', icon: '🆕', color: '#4ECDC4', path: '/products?sort=new' },
  { name: '优惠券', icon: '🎫', color: '#95E1D3', path: '/coupons' }
])

const handleSearch = () => {
  router.push(`/products?keyword=${searchQuery.value}`)
}

const handleIconClick = (item: any) => {
  if (item.path) {
    router.push(item.path)
  }
}

const goToDetail = (id: number) => {
  router.push(`/products/${id}`)
}

const getPrice = (item: any) => {
  const role = userStore.roleType
  const priceMap: Record<string, string> = {
    customer: 'retail',
    shop: 'shop',
    agent: 'agent',
  }
  const tier = priceMap[role] || 'retail'
  const price = item.prices?.find((p: any) => p.tier_type === tier)
  return price ? price.price : item.prices?.[0]?.price || 0
}

const fetchProducts = async () => {
  try {
    const response = await apiClient.get('/products', {
      params: { page: 1, page_size: 10 }
    })
    products.value = response.data.items || []
  } catch (error) {
    console.error('获取产品列表失败:', error)
  }
}

fetchProducts()
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: #F5F5F5;
  padding: 50px 0 0;
  position: relative;
}

/* 顶部毛玻璃效果 */
.home-page::before {
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

/* 搜索栏 */
.search-bar {
  padding: 10px 15px;
  background-color: #FFFFFF;
}

.search-input {
  display: flex;
  align-items: center;
  background-color: #F5F5F5;
  border-radius: 20px;
  padding: 10px 15px;
}

.search-input .search-icon {
  font-size: 16px;
  margin-right: 8px;
}

.search-input input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: #333333;
}

.search-input input::placeholder {
  color: #999999;
}

/* 轮播图 */
.banner-section {
  margin: 15px;
}

.banner-swipe {
  height: 160px;
  border-radius: 12px;
  overflow: hidden;
}

.banner-item {
  height: 100%;
}

.banner-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.banner-title {
  font-size: 24px;
  font-weight: bold;
  color: #FFFFFF;
  margin-bottom: 8px;
}

.banner-subtitle {
  font-size: 16px;
  color: #FFFFFF;
  margin-bottom: 15px;
}

.banner-btn {
  background-color: #FFFFFF;
  color: #FF9500;
  font-size: 14px;
  padding: 8px 30px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
}

/* 功能图标 */
.icon-grid {
  display: flex;
  justify-content: space-around;
  padding: 20px 15px;
  background-color: #FFFFFF;
  margin-bottom: 15px;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.icon-bg {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 8px;
}

.icon {
  font-size: 24px;
}

.icon-text {
  font-size: 12px;
  color: #666666;
}

/* 推荐产品 */
.product-section {
  background-color: #FFFFFF;
  padding: 15px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333333;
  margin: 0;
}

.section-more {
  font-size: 12px;
  color: #999999;
  cursor: pointer;
}

.product-list {
  display: flex;
  flex-direction: column;
}

.product-item {
  display: flex;
  padding: 15px 0;
  border-bottom: 1px solid #F0F0F0;
  cursor: pointer;
}

.product-item:last-child {
  border-bottom: none;
}

.product-image {
  width: 80px;
  height: 80px;
  margin-right: 12px;
  border-radius: 8px;
  overflow: hidden;
  background-color: #F5F5F5;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-name {
  font-size: 15px;
  color: #333333;
  font-weight: 500;
}

.product-desc {
  font-size: 12px;
  color: #999999;
}

.product-price {
  font-size: 18px;
  color: #FF9500;
  font-weight: bold;
}

/* 底部提示 */
.page-footer {
  position: relative;
  padding: 10px 20px 60px;
  text-align: center;
}

.footer-content {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.footer-icon {
  font-size: 16px;
}

.footer-text {
  font-size: 12px;
  color: #999999;
}
</style>
