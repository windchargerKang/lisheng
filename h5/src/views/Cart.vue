<template>
  <div class="cart-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      title="购物车"
      right-text="管理"
      @click-right="toggleManageMode"
    />

    <van-empty v-if="cartItems.length === 0" description="购物车空空如也" />

    <!-- 管理模式下的商品列表 -->
    <div v-for="item in cartItems" :key="item.id" class="cart-item" v-if="isManageMode">
      <div class="cart-item-manage">
        <van-checkbox v-model="item.selected" icon-size="18px" @click="onSelectToggle(item)" />
        <div class="cart-item-info">
          <van-card
            :price="item.price"
            :num="item.quantity"
            :title="item.product_name"
            :thumb="item.image"
            class="product-card"
          >
            <template #num>
              <van-stepper
                v-model="item.quantity"
                min="1"
                max="99"
                @change="onQuantityChange(item)"
              />
            </template>
          </van-card>
        </div>
        <van-icon name="delete-o" size="20" color="#ee0a24" @click="onDelete(item)" />
      </div>
    </div>

    <!-- 正常模式下的商品列表 -->
    <div v-for="item in cartItems" :key="item.id" class="cart-item" v-else>
      <van-swipe-cell :right-width="50">
        <div class="cart-item-content" :class="{ selected: selectedIds.includes(item.id) }">
          <!-- 左侧复选框 -->
          <div class="cart-item-checkbox" @click="onSelectToggle(item)">
            <van-checkbox
              v-model="item.selected"
              :checked="selectedIds.includes(item.id)"
              icon-size="18px"
            />
          </div>
          <!-- 商品信息 -->
          <div class="cart-item-info">
            <van-card
              :price="item.price"
              :num="item.quantity"
              :title="item.product_name"
              :thumb="item.image"
              class="product-card"
            >
              <template #num>
                <van-stepper
                  v-model="item.quantity"
                  min="1"
                  max="99"
                  @change="onQuantityChange(item)"
                />
              </template>
            </van-card>
          </div>
        </div>
        <template #right>
          <van-button
            square
            icon="delete"
            type="danger"
            class="delete-button"
            @click="onDelete(item)"
          />
        </template>
      </van-swipe-cell>
    </div>

    <!-- 底部提示 -->
    <div class="page-footer" v-if="cartItems.length > 0">
      <div class="footer-content">
        <span class="footer-icon">🌸</span>
        <span class="footer-text">已经到底啦～</span>
      </div>
    </div>

    <!-- 底部固定区域：管理模式的删除按钮 或 正常模式的结算栏 -->
    <div class="cart-footer-wrapper" v-if="cartItems.length > 0">
      <!-- 管理模式下显示批量删除 -->
      <div class="manage-footer" v-if="isManageMode">
        <van-button
          block
          type="danger"
          size="large"
          :disabled="selectedIds.length === 0"
          @click="onDeleteSelected"
        >
          删除选中 ({{ selectedIds.length }})
        </van-button>
      </div>
      <!-- 正常模式显示结算栏 -->
      <van-submit-bar
        v-else
        :price="total * 100"
        button-text="结算"
        button-type="primary"
        :disabled="selectedIds.length === 0"
        @submit="onSubmit"
      >
        <template #tip>
          已选择 <span class="num">{{ selectedCount }}</span> 件商品
        </template>
      </van-submit-bar>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import apiClient from '@/api'

interface CartItem {
  id: number
  product_id: number
  product_name: string
  price: number
  quantity: number
  image?: string
  selected?: boolean
}

const cartItems = ref<CartItem[]>([])
const router = useRouter()
const selectedIds = ref<number[]>([])
const isManageMode = ref(false) // 管理模式

// 已选中的商品数量
const selectedCount = computed(() => {
  return cartItems.value
    .filter(item => selectedIds.value.includes(item.id))
    .reduce((sum, item) => sum + item.quantity, 0)
})

// 已选中商品的总价
const total = computed(() => {
  return cartItems.value
    .filter(item => selectedIds.value.includes(item.id))
    .reduce((sum, item) => sum + item.price * item.quantity, 0)
})

const toggleManageMode = () => {
  isManageMode.value = !isManageMode.value
  // 退出管理模式时清空选中状态
  if (!isManageMode.value) {
    selectedIds.value = []
    cartItems.value.forEach(item => item.selected = false)
  }
}

const onQuantityChange = async (item: CartItem) => {
  try {
    await apiClient.put(`/cart/items/${item.id}`, {
      quantity: item.quantity,
    })
    showToast('数量已更新')
  } catch (error: any) {
    showToast(error.response?.data?.detail || '更新失败')
    // 恢复原数量
    fetchCart()
  }
}

const onDelete = async (item: CartItem) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: '确定要删除该商品吗？',
    })
    await apiClient.delete(`/cart/items/${item.id}`)
    cartItems.value = cartItems.value.filter((i) => i.id !== item.id)
    selectedIds.value = selectedIds.value.filter(id => id !== item.id)
    showToast('删除成功')
  } catch {
    // 用户取消
  }
}

const onDeleteSelected = async () => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定要删除选中的 ${selectedIds.value.length} 件商品吗？`,
    })
    // 批量删除
    await Promise.all(selectedIds.value.map(id => apiClient.delete(`/cart/items/${id}`)))
    cartItems.value = cartItems.value.filter((i) => !selectedIds.value.includes(i.id))
    selectedIds.value = []
    showToast('删除成功')
  } catch {
    // 用户取消
  }
}

const onSelectToggle = (item: CartItem) => {
  const index = selectedIds.value.indexOf(item.id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
    item.selected = false
  } else {
    selectedIds.value.push(item.id)
    item.selected = true
  }
}

const onSubmit = async () => {
  if (selectedIds.value.length === 0) {
    showToast('请选择要结算的商品')
    return
  }

  try {
    const response = await apiClient.post('/orders', {
      cart_item_ids: selectedIds.value,
    })

    showToast('下单成功')
    // 跳转到订单详情页
    router.push(`/orders/${response.data.id}`)
    // 清空已选
    selectedIds.value = []
  } catch (error: any) {
    showToast(error.response?.data?.detail || '下单失败')
  }
}

const fetchCart = async () => {
  try {
    const response = await apiClient.get('/cart/items')
    cartItems.value = response.data.items || []
    // 初始化选中状态为全选
    selectedIds.value = cartItems.value.map(item => item.id)
    cartItems.value.forEach(item => {
      item.selected = true
    })
  } catch (error) {
    console.error('获取购物车失败:', error)
    cartItems.value = []
    selectedIds.value = []
  }
}

onMounted(() => {
  fetchCart()
})
</script>

<style scoped>
.cart-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 50px 0 20px;
  position: relative;
}

/* 顶部毛玻璃效果 */
.cart-page::before {
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

/* 结算栏定位 */
.cart-footer-wrapper {
  position: fixed;
  bottom: 50px;
  left: 0;
  right: 0;
  z-index: 99;
}

.cart-footer-wrapper :deep(.van-submit-bar) {
  position: static !important;
  z-index: auto !important;
  box-shadow: none !important;
}

.manage-footer {
  position: fixed;
  bottom: 50px;
  left: 0;
  right: 0;
  z-index: 99;
  padding: 10px 16px;
  background-color: #fff;
  border-top: 1px solid #f0f0f0;
}

.manage-footer :deep(.van-button) {
  height: 44px;
}

/* 底部提示 */
.page-footer {
  position: relative;
  padding: 10px 20px 20px;
  text-align: center;
}

.page-footer .footer-content {
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

.page-footer .footer-icon {
  font-size: 16px;
}

.page-footer .footer-text {
  font-size: 12px;
  color: #999999;
}


.cart-item {
  margin-bottom: 10px;
  background-color: #fff;
}

.cart-item-content {
  display: flex;
  align-items: flex-start;
  padding: 12px 12px 12px 0;
}

/* 管理模式下的商品项 */
.cart-item-manage {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  gap: 10px;
}

.cart-item-manage :deep(.van-checkbox) {
  margin-top: 40px;
}

.cart-item-manage .cart-item-info {
  flex: 1;
}

.cart-item-manage .delete-icon {
  margin-top: 40px;
  cursor: pointer;
}

.cart-item-checkbox {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px 0 12px;
  cursor: pointer;
  flex-shrink: 0;
}

.cart-item-checkbox :deep(.van-checkbox) {
  margin: 0;
}

.cart-item-info {
  flex: 1;
  min-width: 0;
}

.product-card {
  background-color: #fff;
}

.product-card :deep(.van-card) {
  background-color: #fff;
}

.delete-button {
  height: 100%;
}

.num {
  color: #1989fa;
  font-weight: bold;
}
</style>
