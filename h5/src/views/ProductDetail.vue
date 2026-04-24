<template>
  <div class="product-detail-page">
    <van-nav-bar
      title="商品详情"
      left-arrow
      @click-left="$router.back()"
    >
      <template #right>
        <van-icon name="service-o" size="20" @click="contactCustomerService" />
      </template>
    </van-nav-bar>

    <div v-if="product" class="detail-content">
      <!-- 商品图片轮播 -->
      <van-swipe :autoplay="3000" indicator-color="white" style="height: 375px;">
        <van-swipe-item v-for="(img, index) in displayImages" :key="index">
          <img :src="img" style="width: 100%; height: 100%; object-fit: cover;" />
        </van-swipe-item>
      </van-swipe>

      <!-- 商品信息 -->
      <div class="product-info">
        <div class="product-name">{{ product.name }}</div>
        <div class="product-desc">{{ product.description }}</div>

        <!-- 价格展示 -->
        <div class="price-section">
          <div class="price-label">价格</div>
          <div class="price-value">
            <span class="currency">¥</span>
            <span class="price-number">{{ getCurrentPrice }}</span>
          </div>
          <div class="price-tip">{{ currentRoleName }}价</div>
        </div>

        <!-- 三级价格展示（仅管理员可见） -->
        <van-cell-group class="price-tiers" v-if="showAllPriceTiers">
          <van-cell
            v-for="tier in priceTiers"
            :key="tier.type"
            :title="tier.name"
            :value="'¥' + tier.price"
          />
        </van-cell-group>

        <!-- 数量选择 -->
        <div class="quantity-section">
          <div class="quantity-label">数量</div>
          <div class="quantity-selector">
            <van-stepper
              v-model="quantity"
              min="1"
              :max="product.stock || 999"
              integer
              @change="onQuantityChange"
            />
            <span class="stock-tip">库存 {{ product.stock }} 件</span>
          </div>
        </div>
      </div>

      <!-- 商品详情 -->
      <van-cell-group class="detail-section">
        <van-cell title="商品详情">
          <template #label>
            <div class="detail-content-text" v-html="product.detail"></div>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 底部提示 -->
      <div class="page-footer">
        <div class="footer-content">
          <span class="footer-icon">🌸</span>
          <span class="footer-text">已经到底啦～</span>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="bottom-bar" v-if="product">
      <div class="bar-icons">
        <div class="bar-icon" @click="contactCustomerService">
          <van-icon name="service-o" size="20" />
          <span>客服</span>
        </div>
        <div class="bar-icon" @click="goToCart">
          <van-badge :content="cartCount" :max="99">
            <van-icon name="shopping-cart-o" size="20" />
          </van-badge>
          <span>购物车</span>
        </div>
      </div>
      <div class="bar-actions">
        <van-button type="warning" size="large" @click="addToCart">加入购物车</van-button>
        <van-button type="primary" size="large" @click="buyNow">立即购买</van-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import { useUserStore } from '@/stores'
import apiClient from '@/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const product = ref<any>(null)
const loading = ref(false)
const quantity = ref(1)
const cartCount = ref(0)

// 轮播图片列表
const displayImages = computed(() => {
  if (!product.value) return []
  if (product.value.images && product.value.images.length > 0) {
    return product.value.images
  }
  if (product.value.image_url) {
    return [product.value.image_url]
  }
  if (product.value.image) {
    return [product.value.image]
  }
  return []
})

interface PriceTier {
  type: string
  name: string
  price: string
}

const priceTiers = computed<PriceTier[]>(() => {
  if (!product.value?.prices) return []

  const tierMap: Record<string, string> = {
    retail: '零售价',
    shop: '店铺价',
    agent: '区代价',
  }

  return product.value.prices.map((p: any) => ({
    type: p.tier_type,
    name: tierMap[p.tier_type] || p.tier_type,
    price: p.price,
  }))
})

// 是否显示三级价格（只有管理员才显示）
const showAllPriceTiers = computed(() => {
  return product.value?.prices?.length > 1
})

const getCurrentPrice = computed(() => {
  if (!product.value?.prices) return '0'
  return product.value.prices[0]?.price || '0'
})

const currentRoleName = computed(() => {
  if (!product.value?.prices?.[0]) return '零售'
  const tierNameMap: Record<string, string> = {
    retail: '零售',
    shop: '店铺',
    agent: '区代',
  }
  return tierNameMap[product.value.prices[0].tier_type] || '零售'
})

const fetchProductDetail = async () => {
  loading.value = true
  try {
    const productId = route.params.id
    const response = await apiClient.get(`/products/${productId}`)
    product.value = response.data
  } catch (error) {
    console.error('获取商品详情失败:', error)
    showToast('加载失败')
  } finally {
    loading.value = false
  }
}

// 获取购物车数量
const fetchCartCount = async () => {
  try {
    const response = await apiClient.get('/cart/items')
    cartCount.value = response.data.total || 0
  } catch (error) {
    console.error('获取购物车数量失败:', error)
  }
}

const onQuantityChange = (value: number) => {
  quantity.value = value
}

const addToCart = async () => {
  try {
    await apiClient.post('/cart/items', {
      product_id: product.value.id,
      quantity: quantity.value,
    })
    showToast('已加入购物车')
    fetchCartCount()
  } catch (error: any) {
    showToast(error.response?.data?.detail || '添加失败')
  }
}

const buyNow = async () => {
  try {
    // 直接跳转到确认订单页面
    router.push({
      path: '/checkout',
      query: {
        product_id: product.value.id,
        quantity: quantity.value,
      },
    })
  } catch (error: any) {
    showToast('跳转失败')
  }
}

const goToCart = () => {
  router.push('/cart')
}

const contactCustomerService = () => {
  // 可以跳转到客服聊天页面或显示客服联系方式
  showConfirmDialog({
    title: '联系客服',
    message: '客服电话：400-123-4567\n服务时间：9:00-18:00',
    showCancelButton: false,
    confirmButtonText: '拨打电话',
  }).then(() => {
    window.location.href = 'tel:4001234567'
  }).catch(() => {
    // 用户取消
  })
}

onMounted(() => {
  fetchProductDetail()
  fetchCartCount()
})
</script>

<style scoped>
.product-detail-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 50px 0 180px;
  position: relative;
}

/* 顶部毛玻璃效果 */
.product-detail-page::before {
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

.detail-content {
  background-color: #fff;
}

:deep(.van-swipe-item) {
  background-color: #f5f5f5;
}

.product-info {
  padding: 16px;
}

.product-name {
  font-size: 18px;
  font-weight: bold;
  color: #323233;
  margin-bottom: 8px;
}

.product-desc {
  font-size: 14px;
  color: #969799;
  margin-bottom: 16px;
}

.price-section {
  display: flex;
  align-items: baseline;
  margin-bottom: 16px;
}

.price-label {
  font-size: 14px;
  color: #969799;
  margin-right: 8px;
}

.price-value {
  display: flex;
  align-items: baseline;
}

.currency {
  font-size: 14px;
  color: #f44;
}

.price-number {
  font-size: 24px;
  font-weight: bold;
  color: #f44;
}

.price-tip {
  margin-left: 8px;
  font-size: 12px;
  color: #969799;
}

.price-tiers {
  margin-bottom: 16px;
}

.price-tiers :deep(.van-cell) {
  padding: 12px 16px;
}

/* 数量选择 */
.quantity-section {
  display: flex;
  align-items: center;
  margin-top: 16px;
}

.quantity-label {
  font-size: 14px;
  color: #969799;
  margin-right: 16px;
}

.quantity-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stock-tip {
  font-size: 12px;
  color: #969799;
}

.detail-section {
  margin-top: 16px;
}

.detail-content-text {
  font-size: 14px;
  line-height: 1.6;
  color: #323233;
  white-space: pre-wrap;
}

/* 底部操作栏 */
.bottom-bar {
  position: fixed;
  bottom: 50px;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  padding: 8px 0;
  background-color: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  z-index: 99;
}

.bar-icons {
  display: flex;
  padding: 0 16px;
  gap: 24px;
}

.bar-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #666666;
  font-size: 10px;
  cursor: pointer;
}

.bar-icon :deep(.van-icon) {
  margin-bottom: 4px;
}

.bar-icon :deep(.van-badge) {
  display: flex;
  justify-content: center;
}

.bar-actions {
  flex: 1;
  display: flex;
  gap: 8px;
  padding-right: 16px;
}

.bar-actions :deep(.van-button) {
  flex: 1;
  height: 40px;
  font-size: 14px;
}

.bar-actions :deep(.van-button--warning) {
  background-color: #ff9500;
  border-color: #ff9500;
}

.bar-actions :deep(.van-button--primary) {
  background-color: #ff6b6b;
  border-color: #ff6b6b;
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
