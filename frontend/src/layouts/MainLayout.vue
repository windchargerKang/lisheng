<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="sidebar">
      <div class="logo">渠道管理系统</div>
      <el-menu
        :default-active="activeMenu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/regions">
          <el-icon><Location /></el-icon>
          <span>区域管理</span>
        </el-menu-item>
        <el-menu-item index="/shops">
          <el-icon><Shop /></el-icon>
          <span>店铺管理</span>
        </el-menu-item>
        <el-menu-item index="/agents">
          <el-icon><User /></el-icon>
          <span>区代管理</span>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon><Goods /></el-icon>
          <span>产品管理</span>
        </el-menu-item>
        <el-menu-item index="/wallet">
          <el-icon><Wallet /></el-icon>
          <span>我的钱包</span>
        </el-menu-item>
        <el-menu-item index="/wallet-admin" v-if="userStore.userInfo?.role_type === 'admin'">
          <el-icon><Wallet /></el-icon>
          <span>钱包管理</span>
        </el-menu-item>
        <el-sub-menu index="system-management">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/store-applications">店铺/区代申请</el-menu-item>
          <el-menu-item index="/roles">角色管理</el-menu-item>
          <el-menu-item index="/users">用户管理</el-menu-item>
          <el-menu-item index="/logs">操作日志</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/orders/list">
          <el-icon><List /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-sub-menu index="supplier-management">
          <template #title>
            <el-icon><ShoppingCart /></el-icon>
            <span>供应商管理</span>
          </template>
          <el-menu-item index="/suppliers">供应商档案</el-menu-item>
          <el-menu-item index="/purchase-orders">采购订单</el-menu-item>
          <el-menu-item index="/inbounds">入库管理</el-menu-item>
          <el-menu-item index="/settlements">结算管理</el-menu-item>
        </el-sub-menu>
        <!-- 供应商门户入口 -->
        <el-menu-item index="/supplier-portal/dashboard" v-if="userStore.userInfo?.role_type === 'supplier'">
          <el-icon><Shop /></el-icon>
          <span>供应商门户</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="breadcrumb-icon" @click="toggleSidebar"><Fold /></el-icon>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" icon="User" />
              <span class="username">{{ userStore.userInfo?.username || '管理员' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { Fold, Odometer, Location, Shop, User, Goods, ShoppingCart, Setting, List, Wallet } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const toggleSidebar = () => {
  // TODO: 实现侧边栏折叠
  console.log('Toggle sidebar')
}

const handleCommand = (command: string) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background-color: #2b3a4b;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.breadcrumb-icon {
  font-size: 20px;
  cursor: pointer;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  margin-left: 8px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
