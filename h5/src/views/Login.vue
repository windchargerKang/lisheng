<template>
  <div class="login-page">
    <div class="logo-section">
      <img src="@/assets/images/logo.png" alt="力生大健康" class="logo-image" />
      <!-- <h1 class="app-title">力生大健康</h1> -->
    </div>

    <!-- 登录方式切换 -->
    <van-tabs v-model:active="loginType" class="login-tabs">
      <van-tab name="phone" title="手机登录" />
      <van-tab name="account" title="账号登录" />
    </van-tabs>

    <!-- 手机号登录表单 -->
    <van-form v-if="loginType === 'phone'" @submit="handlePhoneLogin">
      <van-field
        v-model="phoneForm.phone"
        name="phone"
        type="tel"
        placeholder="请输入手机号"
        left-icon="phone-o"
        :rules="[
          { required: true, message: '请输入手机号' },
          { pattern: /^1\d{10}$/, message: '手机号格式不正确' }
        ]"
      >
        <template #left-icon>
          <span class="country-code">+86</span>
        </template>
      </van-field>
      <van-field
        v-model="phoneForm.password"
        type="password"
        name="password"
        placeholder="请输入密码"
        left-icon="lock"
        :rules="[{ required: true, message: '请输入密码' }]"
      />
      <!-- 滑块验证 -->
      <div class="captcha-container">
        <van-button
          v-if="!captchaPassed"
          size="small"
          block
          plain
          @click="showCaptcha = true"
        >
          点击进行滑块验证
        </van-button>
        <div v-else class="captcha-success">
          <van-icon name="checked" color="#07c160" /> 验证通过
        </div>
      </div>
      <!-- 协议勾选 -->
      <div class="agreement-container">
        <van-checkbox v-model="agreementChecked" icon-size="16px">
          我已阅读并同意
          <a href="#" @click.prevent="showAgreement = 'terms'">登录协议</a>
          与
          <a href="#" @click.prevent="showAgreement = 'privacy'">隐私权政策</a>
        </van-checkbox>
      </div>
      <div class="button-section">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          {{ loading ? '登录中...' : '登录' }}
        </van-button>
      </div>
      <div class="extra-links">
        <a href="#" @click.prevent="showForgotPassword">忘记密码？</a>
        <a @click.prevent="goToRegister">注册</a>
      </div>
    </van-form>

    <!-- 账号登录表单 -->
    <van-form v-else @submit="handleAccountLogin">
      <van-field
        v-model="accountForm.username"
        name="username"
        placeholder="请输入用户名"
        left-icon="user-o"
        :rules="[{ required: true, message: '请输入用户名' }]"
      />
      <van-field
        v-model="accountForm.password"
        type="password"
        name="password"
        placeholder="请输入密码"
        left-icon="lock"
        :rules="[{ required: true, message: '请输入密码' }]"
      />
      <div class="button-section">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          {{ loading ? '登录中...' : '登录' }}
        </van-button>
      </div>
      <div class="extra-links">
        <a href="#" @click.prevent="showForgotPassword">忘记密码？</a>
        <a @click.prevent="goToRegister">注册</a>
      </div>
    </van-form>

    <!-- 滑块验证弹窗 -->
    <van-dialog
      v-model:show="showCaptcha"
      title="滑块验证"
      :show-confirm-button="false"
      :close-on-click-overlay="false"
    >
      <div class="captcha-dialog">
        <p class="captcha-tip">请向右滑动完成验证</p>
        <!-- 简易滑块验证 -->
        <div class="slider-container">
          <div class="slider-track" ref="sliderTrack">
            <div class="slider-knob" @touchstart="onSliderStart" @mousedown="onSliderStart">
              →
            </div>
          </div>
        </div>
      </div>
    </van-dialog>

    <!-- 协议弹窗 -->
    <van-dialog
      v-model:show="showAgreement"
      :title="agreementType === 'terms' ? '登录协议' : '隐私权政策'"
      :show-confirm-button="true"
      confirm-button-text="同意"
    >
      <div class="agreement-content">
        <p v-if="agreementType === 'terms'">
          欢迎使用渠道销售管理系统。使用本服务即表示您同意我们的登录协议...
        </p>
        <p v-if="agreementType === 'privacy'">
          我们非常重视您的隐私保护。使用本服务时我们将收集和处理您的个人信息...
        </p>
      </div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '@/stores'
import apiClient from '@/api'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

// 登录方式：'phone' | 'account'
const loginType = ref<'phone' | 'account'>('phone')

// 手机号登录表单
const phoneForm = reactive({
  phone: '',
  password: '',
})

// 账号登录表单
const accountForm = reactive({
  username: '',
  password: '',
})

// 滑块验证状态
const showCaptcha = ref(false)
const captchaPassed = ref(false)
const sliderTrack = ref<HTMLElement | null>(null)

// 协议勾选
const agreementChecked = ref(false)
const showAgreement = ref<string | null>(null)
const agreementType = ref<'terms' | 'privacy'>('terms')

// 手机号登录
const handlePhoneLogin = async () => {
  if (!captchaPassed.value) {
    showToast('请先完成滑块验证')
    return
  }
  if (!agreementChecked.value) {
    showToast('请先勾选同意协议')
    return
  }

  loading.value = true

  try {
    const response = await apiClient.post('/auth/login', {
      username: phoneForm.phone,
      password: phoneForm.password,
    })
    const { token, user } = response.data

    userStore.setToken(token)
    userStore.setUserInfo(user)

    showToast('登录成功')
    router.push('/')
  } catch (error: any) {
    showToast(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

// 账号登录
const handleAccountLogin = async () => {
  loading.value = true

  try {
    const response = await apiClient.post('/auth/login', {
      username: accountForm.username,
      password: accountForm.password,
    })
    const { token, user } = response.data

    userStore.setToken(token)
    userStore.setUserInfo(user)

    showToast('登录成功')
    router.push('/')
  } catch (error: any) {
    showToast(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

// 滑块验证开始
const onSliderStart = (e: TouchEvent | MouseEvent) => {
  const track = sliderTrack.value
  if (!track) return

  const knob = e.target as HTMLElement
  const startX = 'touches' in e ? e.touches[0].clientX : e.clientX
  const trackRect = track.getBoundingClientRect()
  const maxMove = trackRect.width - 40

  let moved = false

  const onMove = (moveEvent: TouchEvent | MouseEvent) => {
    const currentX = 'touches' in moveEvent ? moveEvent.touches[0].clientX : moveEvent.clientX
    let deltaX = currentX - startX
    deltaX = Math.max(0, Math.min(deltaX, maxMove))
    knob.style.transform = `translateX(${deltaX}px)`
    moved = deltaX >= maxMove - 10
  }

  const onEnd = () => {
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onEnd)
    document.removeEventListener('touchmove', onMove)
    document.removeEventListener('touchend', onEnd)

    if (moved) {
      captchaPassed.value = true
      showCaptcha.value = false
      showToast('验证通过')
    } else {
      ;(knob as HTMLElement).style.transform = 'translateX(0)'
    }
  }

  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onEnd)
  document.addEventListener('touchmove', onMove)
  document.addEventListener('touchend', onEnd)
}

// 忘记密码
const showForgotPassword = () => {
  showToast('请联系管理员重置密码')
}

// 跳转注册
const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-page {
  padding: 40px 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.logo-section {
  text-align: center;
  margin-bottom: 40px;
}

.logo-image {
  width: 120px;
  height: 120px;
  object-fit: contain;
}

.app-title {
  margin-top: 16px;
  font-size: 24px;
  color: #323233;
}

.login-tabs {
  margin-bottom: 20px;
}

.country-code {
  font-size: 14px;
  color: #333;
  font-weight: bold;
  margin-right: 4px;
}

.captcha-container {
  padding: 16px;
  background: #f7f8fa;
  margin: 16px 0;
  border-radius: 8px;
}

.captcha-success {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #07c160;
  font-size: 14px;
}

.agreement-container {
  padding: 16px;
}

.agreement-container :deep(.van-checkbox) {
  display: flex;
  align-items: flex-start;
}

.agreement-container :deep(.van-checkbox__label) {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

.agreement-container a {
  color: #1989fa;
  text-decoration: none;
}

.button-section {
  margin-top: 32px;
}

.extra-links {
  display: flex;
  justify-content: space-between;
  padding: 16px;
  font-size: 14px;
}

.extra-links a {
  color: #666;
  text-decoration: none;
}

.captcha-dialog {
  padding: 20px;
}

.captcha-tip {
  text-align: center;
  margin-bottom: 16px;
  font-size: 14px;
  color: #666;
}

.slider-container {
  position: relative;
  height: 40px;
  background: #f0f0f0;
  border-radius: 20px;
  overflow: hidden;
}

.slider-track {
  position: relative;
  height: 100%;
  background: linear-gradient(90deg, #1989fa 0%, #1989fa 100%);
  border-radius: 20px;
}

.slider-knob {
  position: absolute;
  left: 0;
  top: 0;
  width: 40px;
  height: 40px;
  background: #fff;
  border: 2px solid #1989fa;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  transition: transform 0.1s;
  user-select: none;
}

.agreement-content {
  padding: 16px;
  font-size: 14px;
  line-height: 1.6;
  color: #666;
  max-height: 300px;
  overflow-y: auto;
}
</style>
