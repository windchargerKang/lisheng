<template>
  <div class="profile-page">
    <!-- 用户信息头部 -->
    <div class="user-header">
      <div class="user-info">
        <div class="avatar">
          <van-icon name="user-o" size="40" />
        </div>
        <div class="user-detail">
          <div class="username">{{ userStore.userInfo?.username || '用户' }}</div>
          <div class="user-id">ID: {{ userStore.userInfo?.id || '' }}</div>
          <div class="user-role">{{ getRoleText(userStore.roleType || '') }}</div>
        </div>
      </div>
    </div>

    <!-- 订单状态栏 -->
    <div class="order-status">
      <div class="status-title">我的订单</div>
      <div class="status-list">
        <div class="status-item" v-for="(item, index) in orderStatus" :key="index">
          <div class="status-icon">{{ item.icon }}</div>
          <div class="status-text">{{ item.name }}</div>
        </div>
      </div>
      <div class="view-all" @click="$router.push('/orders')">查看全部订单 ></div>
    </div>

    <!-- 功能菜单 -->
    <van-cell-group :border="false" class="menu-group">
      <van-cell title="我想开店" icon="shop-o" is-link to="/store-apply" />
      <van-cell title="我的钱包" icon="cash-o" is-link to="/wallet" />
      <van-cell v-show="userStore.userInfo?.role_code === 'shop'" title="订单核销" is-link to="/verification" icon="orders-o" />
      <van-cell title="附近店铺" icon="location-o" is-link to="/nearby-shops" />
      <van-cell title="地址管理" icon="location-o" is-link to="/addresses" />
      <van-cell title="联系客服" icon="service-o" is-link />
      <van-cell title="关于我们" icon="info-o" is-link />
    </van-cell-group>

    <!-- 退出登录 -->
    <div class="logout-section">
      <van-button round block plain type="danger" @click="handleLogout">
        退出登录
      </van-button>
    </div>

    <!-- 底部占位空间 -->
    <div class="bottom-spacer"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import { useUserStore } from '@/stores'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

const orderStatus = [
  { name: '待付款', icon: '💳' },
  { name: '待发货', icon: '📦' },
  { name: '待收货', icon: '🚚' },
  { name: '已完成', icon: '✅' },
  { name: '售后', icon: '🔄' }
]

const getRoleText = (roleType: string): string => {
  const textMap: Record<string, string> = {
    customer: '客户',
    shop: '店铺',
    agent: '区代',
    admin: '管理员',
  }
  return textMap[roleType] || '未知'
}

const handleLogout = async () => {
  try {
    await showConfirmDialog({
      title: '确认退出',
      message: '确定要退出登录吗？',
    })
    userStore.logout()
    router.push('/login')
    showToast('已退出登录')
  } catch {
    // 用户取消
  }
}

const loadUserInfo = async () => {
  try {
    // 获取角色列表
    const roles = await userStore.fetchUserRoles()
    console.log('角色列表:', roles)
    // 再获取用户详情（包含 role_code）
    const response = await api.get('/auth/profile')
    userStore.setUserInfo(response.data)
    console.log('用户信息:', response.data)
    console.log('当前角色 ID:', userStore.currentRoleId)
    console.log('角色类型 (roleType):', userStore.roleType)
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #F5F5F5;
  padding: 50px 0 0;
  position: relative;
}

/* 顶部毛玻璃效果 */
.profile-page::before {
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

/* 用户信息头部 */
.user-header {
  background: linear-gradient(135deg, #FFF5EB 0%, #FFE8D0 100%);
  padding: 30px 20px 20px;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #FFFFFF;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 15px;
}

.user-detail {
  flex: 1;
}

.username {
  font-size: 20px;
  font-weight: bold;
  color: #333333;
  margin-bottom: 5px;
}

.user-id {
  font-size: 12px;
  color: #999999;
  margin-bottom: 4px;
}

.user-role {
  font-size: 12px;
  color: #ff6b6b;
  font-weight: 500;
}

/* 订单状态栏 */
.order-status {
  background-color: #FFFFFF;
  margin: 10px 15px;
  padding: 20px 15px;
  border-radius: 12px;
}

.status-title {
  font-size: 16px;
  font-weight: bold;
  color: #333333;
  margin-bottom: 15px;
}

.status-list {
  display: flex;
  justify-content: space-around;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.status-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.status-text {
  font-size: 12px;
  color: #666666;
}

.view-all {
  text-align: right;
  font-size: 12px;
  color: #999999;
  margin-top: 15px;
  cursor: pointer;
}

/* 功能菜单 */
.menu-group {
  background-color: #FFFFFF;
  margin: 10px 15px;
  border-radius: 12px;
  overflow: hidden;
}

/* 退出登录 */
.logout-section {
  margin: 30px 15px;
}

.bottom-spacer {
  height: 100px;
}
</style>
