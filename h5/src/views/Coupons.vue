<template>
  <div class="coupons-page">
    <van-nav-bar
      title="我的优惠券"
      left-arrow
      @click-left="$router.back()"
    />

    <div class="empty-state">
      <van-empty
        image="https://fastly.jsdelivr.net/npm/@vant/assets/custom-empty-image.png"
        image-size="80"
        description="暂无优惠券"
      >
        <van-button type="primary" size="small" round @click="goToProducts">
          去逛逛
        </van-button>
      </van-empty>
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
import { useRouter } from 'vue-router'

const router = useRouter()

const goToProducts = () => {
  router.push('/products')
}
</script>

<style scoped>
.coupons-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  position: relative;
}

/* 顶部毛玻璃效果 */
.coupons-page::before {
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 100px);
  padding: 40px 20px;
}

.empty-state :deep(.van-empty) {
  margin-bottom: 24px;
}

.empty-state :deep(.van-empty__description) {
  color: #969799;
  font-size: 14px;
}

.empty-state :deep(.van-button) {
  margin-top: 16px;
  padding: 0 32px;
  height: 36px;
  font-size: 14px;
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
