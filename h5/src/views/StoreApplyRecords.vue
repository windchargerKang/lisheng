<template>
  <div class="store-apply-records-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      title="我的申请"
      left-arrow
      @click-left="$router.back()"
    />

    <!-- 空状态 -->
    <van-empty v-if="applications.length === 0 && !loading" description="暂无申请记录">
      <van-button round type="primary" @click="$router.back()">去申请</van-button>
    </van-empty>

    <!-- 申请列表 -->
    <div v-else class="application-list">
      <div
        v-for="item in applications"
        :key="item.id"
        class="application-card"
        @click="showDetail(item)"
      >
        <div class="application-header">
          <span class="application-type">
            {{ item.apply_type === 'SHOP' ? '店铺申请' : '区代申请' }}
          </span>
          <van-tag :type="getStatusType(item.status)">{{ getStatusText(item.status) }}</van-tag>
        </div>
        <div class="application-info">
          <span class="application-name">{{ item.shop_name || item.agent_name }}</span>
          <span class="application-date">{{ formatDate(item.created_at) }}</span>
        </div>
        <div v-if="item.status === 'REJECTED' && item.reject_reason" class="reject-reason">
          <van-icon name="warning-o" />
          <span>拒绝原因：{{ item.reject_reason }}</span>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <van-loading color="#1989fa">加载中...</van-loading>
    </div>

    <!-- 申请详情弹窗 -->
    <van-dialog
      v-model:show="detailVisible"
      title="申请详情"
      :show-confirm-button="false"
      :show-cancel-button="false"
    >
      <div class="detail-content">
        <van-cell title="申请类型" :value="currentApplication?.apply_type === 'SHOP' ? '店铺申请' : '区代申请'" />
        <van-cell title="申请状态">
          <van-tag :type="getStatusType(currentApplication?.status)">
            {{ getStatusText(currentApplication?.status) }}
          </van-tag>
        </van-cell>
        <van-cell title="申请名称" :value="currentApplication?.shop_name || currentApplication?.agent_name" />
        <van-cell
          v-if="currentApplication?.apply_type === 'SHOP'"
          title="店铺位置"
          :value="currentApplication?.shop_latitude && currentApplication?.shop_longitude ? `${currentApplication.shop_latitude}, ${currentApplication.shop_longitude}` : '未选择'"
        />
        <van-cell
          v-if="currentApplication?.status === 'REJECTED'"
          title="拒绝原因"
          :value="currentApplication?.reject_reason"
        />
        <van-cell title="申请时间" :value="formatDateTime(currentApplication?.created_at)" />

        <!-- 重新申请按钮 -->
        <div v-if="currentApplication?.status === 'REJECTED'" class="reapply-btn">
          <van-button round block type="primary" @click="reapply">重新申请</van-button>
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import apiClient from '@/api'

const router = useRouter()

interface Application {
  id: number
  apply_type: string
  shop_name?: string
  agent_name?: string
  status: string
  reject_reason?: string
  created_at: string
}

const applications = ref<Application[]>([])
const loading = ref(false)
const detailVisible = ref(false)
const currentApplication = ref<Application | null>(null)

const fetchApplications = async () => {
  loading.value = true
  try {
    const res = await apiClient.get('/store-applications/my')
    applications.value = res.data.items || []
  } catch (error) {
    console.error('获取申请记录失败:', error)
    showToast('获取申请记录失败')
  } finally {
    loading.value = false
  }
}

const getStatusType = (status: string): string => {
  const map: Record<string, string> = {
    PENDING: 'warning',
    APPROVED: 'success',
    REJECTED: 'danger',
  }
  return map[status] || 'default'
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = {
    PENDING: '待审核',
    APPROVED: '已通过',
    REJECTED: '已拒绝',
  }
  return map[status] || status
}

const formatDate = (dateStr: string): string => {
  if (!dateStr) return ''
  return dateStr.slice(0, 10)
}

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return ''
  return dateStr.slice(0, 16).replace('T', ' ')
}

const showDetail = (item: Application) => {
  currentApplication.value = item
  detailVisible.value = true
}

const reapply = () => {
  detailVisible.value = false
  router.push('/store-apply')
}

onMounted(() => {
  fetchApplications()
})
</script>

<style scoped>
.store-apply-records-page {
  min-height: 100vh;
  background-color: #F5F5F5;
  padding: 50px 0 0;
  position: relative;
}

/* 顶部毛玻璃效果 */
.store-apply-records-page::before {
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

/* 申请列表 */
.application-list {
  padding: 15px;
}

.application-card {
  background-color: #FFFFFF;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 15px;
  cursor: pointer;
}

.application-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.application-type {
  font-size: 15px;
  font-weight: bold;
  color: #333333;
}

.application-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.application-name {
  font-size: 14px;
  color: #666666;
}

.application-date {
  font-size: 12px;
  color: #999999;
}

.reject-reason {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px;
  background-color: #FFF5F5;
  border-radius: 8px;
  font-size: 13px;
  color: #FF6B6B;
}

.reject-reason van-icon {
  font-size: 16px;
}

/* 加载状态 */
.loading-state {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(0, 0, 0, 0.7);
  color: #FFFFFF;
  padding: 15px 25px;
  border-radius: 8px;
  z-index: 1000;
}

/* 详情内容 */
.detail-content {
  max-height: 60vh;
  overflow-y: auto;
}

.reapply-btn {
  padding: 20px 15px;
}
</style>
