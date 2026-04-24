<template>
  <div class="layout-container" :class="{ 'has-tabbar': activeTab >= 0 }">
    <router-view />
    <van-tabbar v-model="activeTab" route v-if="activeTab >= 0">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="shopping-cart-o" to="/cart">购物车</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/orders">订单</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const activeTab = computed(() => {
  const pathMap: Record<string, number> = {
    '/home': 0,
    '/cart': 1,
    '/orders': 2,
    '/profile': 3,
  }
  // 处理 /products 路径也显示在首页 tab
  if (route.path.startsWith('/products')) {
    return 0
  }
  // 处理 /verification 路径不显示任何 tab（隐藏 tabbar）
  if (route.path === '/verification') {
    return -1
  }
  return pathMap[route.path] || 0
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-container > router-view {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 150px;
}

/* 确保 tabbar 在最上层 */
:deep(.van-tabbar) {
  z-index: 999 !important;
}
</style>
