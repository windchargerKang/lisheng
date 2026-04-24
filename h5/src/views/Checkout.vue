<template>
  <div class="checkout-page">
    <van-nav-bar
      title="确认订单"
      left-arrow
      @click-left="$router.back()"
    />

    <!-- 收货地址选择 -->
    <van-cell-group class="address-section">
      <van-cell
        title="收货地址"
        :value="selectedAddressText"
        is-link
        @click="goToAddressSelect"
      />
      <van-cell v-if="selectedAddress" class="selected-address-detail">
        <div class="address-detail">
          <div>{{ selectedAddress.receiver_name }} {{ selectedAddress.receiver_phone }}</div>
          <div>{{ selectedAddress.receiver_address }}</div>
        </div>
      </van-cell>
    </van-cell-group>

    <!-- 订单备注 -->
    <van-cell-group class="remark-section">
      <van-field
        v-model="checkoutForm.remark"
        name="remark"
        label="订单备注"
        type="textarea"
        rows="2"
        placeholder="选填：对本订单的说明（如配送时间、特殊要求等）"
      />
    </van-cell-group>

    <!-- 商品清单 -->
    <van-cell-group class="products-section">
      <van-cell title="商品信息" />
      <div v-for="item in cartItems" :key="item.id" class="product-item">
        <van-image :src="item.image" width="60" height="60" fit="cover" />
        <div class="product-info">
          <div class="product-name">{{ item.product_name }}</div>
          <div class="product-meta">
            <span class="price">¥{{ item.price }}</span>
            <span class="quantity">×{{ item.quantity }}</span>
          </div>
        </div>
      </div>
    </van-cell-group>

    <!-- 金额明细 -->
    <van-cell-group class="summary-section">
      <van-cell title="商品总额" :value="`¥${totalAmount}`" />
      <van-cell title="运费" :value="'¥0.00'" />
      <van-cell title="实付款" :value="`¥${totalAmount}`" class="total-cell" />
    </van-cell-group>

    <!-- 提交订单 -->
    <van-submit-bar
      :price="parseFloat(totalAmount) * 100"
      button-text="提交订单"
      button-type="primary"
      @submit="submitOrder"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import apiClient from '@/api'

const router = useRouter()
const route = useRoute()

interface CartItem {
  id: number
  product_id: number
  product_name: string
  price: number
  quantity: number
  image?: string
}

// 立即购买模式：从 URL query 参数获取商品信息
const buyNowMode = ref(false)
const buyNowProduct = ref<any>(null)
const buyNowQuantity = ref(1)

interface Address {
  id: number
  receiver_name: string
  receiver_phone: string
  receiver_address: string
  is_default: boolean
}

const cartItems = ref<CartItem[]>([])
const checkoutForm = ref({
  receiver_name: '',
  receiver_phone: '',
  receiver_address: '',
  remark: ''
})

const selectedAddress = ref<Address | null>(null)

const selectedAddressText = computed(() => {
  if (selectedAddress.value) {
    return `${selectedAddress.value.receiver_name} · ${selectedAddress.value.receiver_phone}`
  }
  return '请选择收货地址'
})

const totalAmount = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2)
})

// 处理地址选择事件
const handleAddressSelected = (event: CustomEvent<Address>) => {
  const addr = event.detail
  selectedAddress.value = addr
  checkoutForm.value.receiver_name = addr.receiver_name
  checkoutForm.value.receiver_phone = addr.receiver_phone
  checkoutForm.value.receiver_address = addr.receiver_address
}

const goToAddressSelect = () => {
  router.push('/addresses?selectMode=1')
}

const fetchCartItems = async () => {
  // 检查是否为立即购买模式
  const productId = route.query.product_id
  const quantity = route.query.quantity

  if (productId && quantity) {
    // 立即购买模式：获取商品详情
    buyNowMode.value = true
    buyNowQuantity.value = parseInt(quantity as string)
    try {
      const response = await apiClient.get(`/products/${productId}`)
      buyNowProduct.value = response.data
      // 构造购物车项
      cartItems.value = [{
        id: 0, // 临时 ID
        product_id: response.data.id,
        product_name: response.data.name,
        price: parseFloat(response.data.prices?.[0]?.price || '0'),
        quantity: buyNowQuantity.value,
        image: response.data.image_url || response.data.image,
      }]
    } catch (error) {
      console.error('获取商品详情失败:', error)
      showToast('获取商品信息失败')
      router.back()
    }
  } else {
    // 购物车结算模式
    try {
      const response = await apiClient.get('/cart/items')
      cartItems.value = response.data.items || []
      if (cartItems.value.length === 0) {
        showToast('购物车为空')
        router.back()
      }
    } catch (error) {
      console.error('获取购物车失败:', error)
      showToast('获取购物车失败')
      router.back()
    }
  }
}

const fetchDefaultAddress = async () => {
  try {
    const response = await apiClient.get('/addresses')
    const addresses = response.data.items || []
    // 优先使用默认地址，否则使用第一个地址
    const defaultAddr = addresses.find((a: Address) => a.is_default) || addresses[0]
    if (defaultAddr) {
      selectedAddress.value = defaultAddr
      checkoutForm.value.receiver_name = defaultAddr.receiver_name
      checkoutForm.value.receiver_phone = defaultAddr.receiver_phone
      checkoutForm.value.receiver_address = defaultAddr.receiver_address
    }
  } catch (error) {
    console.error('获取地址列表失败:', error)
    // 地址获取失败不影响结算流程
  }
}

const submitOrder = async () => {
  // 表单验证
  if (!selectedAddress.value) {
    showToast('请选择收货地址')
    return
  }

  try {
    await showConfirmDialog({
      title: '确认提交',
      message: '确认提交订单吗？'
    })

    let response
    if (buyNowMode.value) {
      // 立即购买模式：直接提交商品和数量
      response = await apiClient.post('/orders', {
        items: [{
          product_id: buyNowProduct.value.id,
          quantity: buyNowQuantity.value,
        }],
        receiver_name: selectedAddress.value.receiver_name,
        receiver_phone: selectedAddress.value.receiver_phone,
        receiver_address: selectedAddress.value.receiver_address,
        remark: checkoutForm.value.remark
      })
    } else {
      // 购物车模式：提交购物车 ID 列表
      response = await apiClient.post('/orders', {
        cart_item_ids: cartItems.value.map(item => item.id),
        receiver_name: selectedAddress.value.receiver_name,
        receiver_phone: selectedAddress.value.receiver_phone,
        receiver_address: selectedAddress.value.receiver_address,
        remark: checkoutForm.value.remark
      })
    }

    // 所有订单都直接确认订单，钱包扣款
    try {
      await apiClient.post(`/orders/${response.data.id}/confirm`)
      showToast('订单确认成功')
      router.push(`/orders/${response.data.id}`)
    } catch (error: any) {
      showToast(error.response?.data?.detail || '订单确认失败')
    }
  } catch (error: any) {
    // 用户取消对话框
    if (error.message === 'cancel') {
      return
    }
    // API 错误
    showToast(error.response?.data?.detail || '下单失败，请重试')
  }
}

onMounted(() => {
  fetchCartItems()
  fetchDefaultAddress()
  // 监听地址选择事件
  window.addEventListener('address-selected', handleAddressSelected as EventListener)
})

onUnmounted(() => {
  window.removeEventListener('address-selected', handleAddressSelected as EventListener)
})
</script>

<style scoped>
.checkout-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 50px 0 100px;
  position: relative;
}

/* 顶部毛玻璃效果 */
.checkout-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 90;
  pointer-events: none;
}

/* 底部提示 */
.checkout-page :deep(.van-submit-bar) {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.address-section {
  margin-bottom: 16px;
}

.selected-address-detail {
  padding: 12px 16px;
  background-color: #f7f8fa;
}

.address-detail {
  font-size: 14px;
  color: #646566;
  line-height: 1.6;
}

.remark-section {
  margin-bottom: 16px;
}

.products-section {
  margin-bottom: 16px;
}

.product-item {
  display: flex;
  gap: 10px;
  padding: 10px 16px;
  border-bottom: 1px solid #f5f5f5;
}

.product-item:last-child {
  border-bottom: none;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-name {
  font-size: 14px;
  color: #323233;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  color: #f44;
  font-size: 15px;
  font-weight: bold;
}

.quantity {
  color: #969799;
  font-size: 13px;
}

.summary-section {
  margin-bottom: 16px;
}

.total-cell :deep(.van-cell__title) {
  font-weight: bold;
}

.total-cell :deep(.van-cell__value) {
  color: #f44;
  font-weight: bold;
  font-size: 15px;
}
</style>
