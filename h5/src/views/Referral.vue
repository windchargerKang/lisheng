<template>
  <div class="referral-page">
    <van-nav-bar
      title="分享中心"
      left-arrow
      @click-left="$router.back()"
    />

    <!-- 分享统计卡片 -->
    <div class="stats-card">
      <div class="stats-title">我的团队</div>
      <div class="stats-numbers">
        <div class="stat-item">
          <div class="stat-value">{{ stats.total_referrals }}</div>
          <div class="stat-label">累计分享</div>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <div class="stat-value">{{ stats.active_referrals }}</div>
          <div class="stat-label">有效分享</div>
        </div>
      </div>
    </div>

    <!-- 分享方式 -->
    <van-cell-group class="share-methods">
      <van-cell title="分享链接" :border="false">
        <template #label>
          <div class="share-link-container">
            <input
              v-model="shareLink"
              class="share-link-input"
              readonly
              @click="copyLink"
            />
            <van-button
              size="small"
              type="primary"
              plain
              @click="copyLink"
            >
              复制
            </van-button>
          </div>
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 二维码 -->
    <van-cell-group class="qr-section">
      <van-cell title="分享二维码" :border="false">
        <template #label>
          <div class="qr-container">
            <canvas ref="qrCanvas" width="200" height="200"></canvas>
          </div>
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 操作菜单 -->
    <van-cell-group class="menu-group">
      <van-cell
        title="我的团队"
        icon="friends-o"
        is-link
        to="/referral/team"
      />
      <van-cell
        title="分享记录"
        icon="share-o"
        is-link
        to="/referral/records"
      />
    </van-cell-group>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { showToast } from 'vant'
import apiClient from '@/api'
import QRCode from 'qrcode'

const stats = ref({
  total_referrals: 0,
  active_referrals: 0,
})

const shareLink = ref('')
const qrCanvas = ref<HTMLCanvasElement | null>(null)

const fetchStats = async () => {
  try {
    const response = await apiClient.get('/referral/stats')
    stats.value = response.data
  } catch (error) {
    console.error('获取分享统计失败:', error)
  }
}

const fetchShareLink = async () => {
  try {
    const response = await apiClient.get('/referral/code')
    // 构建完整的分享链接
    const baseUrl = window.location.origin
    shareLink.value = `${baseUrl}${response.data.share_link}`
    // 生成二维码
    await nextTick()
    generateQRCode(response.data.share_link)
  } catch (error) {
    console.error('获取分享码失败:', error)
  }
}

const generateQRCode = async (text: string) => {
  if (!qrCanvas.value) return

  try {
    const url = window.location.origin + text
    await QRCode.toCanvas(qrCanvas.value, url, {
      width: 200,
      height: 200,
      margin: 2,
    })
  } catch (error) {
    console.error('生成二维码失败:', error)
  }
}

const copyLink = () => {
  navigator.clipboard.writeText(shareLink.value).then(() => {
    showToast('链接已复制')
  }).catch(() => {
    showToast('复制失败')
  })
}

onMounted(() => {
  fetchStats()
  fetchShareLink()
})
</script>

<style scoped>
.referral-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.stats-card {
  background: linear-gradient(135deg, #1989fa 0%, #0e6fd6 100%);
  padding: 24px 20px;
  color: #fff;
  margin-bottom: 16px;
}

.stats-title {
  text-align: center;
  font-size: 16px;
  margin-bottom: 20px;
}

.stats-numbers {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background-color: rgba(255, 255, 255, 0.3);
  margin: 0 20px;
}

.share-link-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.share-link-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #dcdee0;
  border-radius: 4px;
  font-size: 13px;
  color: #323233;
  background-color: #fff;
}

.qr-container {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

.menu-group {
  margin-top: 16px;
  border-radius: 12px;
  overflow: hidden;
}
</style>
