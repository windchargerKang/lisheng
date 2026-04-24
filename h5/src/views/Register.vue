<template>
  <div class="register-page">
    <div class="logo-section">
      <img src="@/assets/images/logo.png" alt="力生大健康" class="logo-image" />
      <h1 class="app-title">力生大健康</h1>
    </div>

    <!-- 顶部导航栏 -->
    <van-nav-bar
      title=""
      left-arrow
      @click-left="$router.back()"
    />

    <van-form @submit="handleRegister">
      <div class="form-container">
        <!-- 手机号 -->
        <van-field
          v-model="registerForm.phone"
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

        <!-- 密码 -->
        <van-field
          v-model="registerForm.password"
          type="password"
          name="password"
          placeholder="请输入密码"
          left-icon="lock"
          :rules="[
            { required: true, message: '请输入密码' },
            { min: 6, message: '密码至少 6 位' }
          ]"
        />

        <!-- 确认密码 -->
        <van-field
          v-model="registerForm.confirmPassword"
          type="password"
          name="confirmPassword"
          placeholder="请确认密码"
          left-icon="lock"
          :rules="[
            { required: true, message: '请确认密码' },
            { validator: validatePasswordConfirm, message: '两次输入的密码不一致' }
          ]"
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
            <a href="#" @click.prevent="showAgreement = 'terms'">注册协议</a>
            与
            <a href="#" @click.prevent="showAgreement = 'privacy'">隐私权政策</a>
          </van-checkbox>
        </div>
      </div>

      <!-- 注册按钮 -->
      <div class="button-section">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          {{ loading ? '注册中...' : '注册' }}
        </van-button>
      </div>

      <!-- 去登录 -->
      <div class="extra-links">
        <span>已有账号？</span>
        <a href="#" @click.prevent="goToLogin">去登录</a>
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
      :title="agreementType === 'terms' ? '注册协议' : '隐私权政策'"
      :show-confirm-button="true"
      confirm-button-text="同意"
    >
      <div class="agreement-content">
        <p v-if="agreementType === 'terms'">
          欢迎使用渠道销售管理系统。注册账号即表示您同意我们的注册协议...
        </p>
        <p v-if="agreementType === 'privacy'">
          我们非常重视您的隐私保护。注册账号时我们将收集和处理您的个人信息...
        </p>
      </div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import apiClient from '@/api'

const router = useRouter()
const loading = ref(false)

// 注册表单
const registerForm = reactive({
  phone: '',
  password: '',
  confirmPassword: '',
})

// 滑块验证状态
const showCaptcha = ref(false)
const captchaPassed = ref(false)
const sliderTrack = ref<HTMLElement | null>(null)

// 协议勾选
const agreementChecked = ref(false)
const showAgreement = ref<string | null>(null)
const agreementType = ref<'terms' | 'privacy'>('terms')

// 验证密码一致性
const validatePasswordConfirm = () => {
  return registerForm.password === registerForm.confirmPassword
}

// 注册
const handleRegister = async () => {
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
    await apiClient.post('/auth/register-by-phone', {
      phone_number: registerForm.phone,
      password: registerForm.password,
      confirm_password: registerForm.confirmPassword,
    })

    showToast('注册成功')
    router.push('/login')
  } catch (error: any) {
    showToast(error.response?.data?.detail || '注册失败')
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

// 跳转登录
const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background-color: #fff;
}

.logo-section {
  text-align: center;
  padding: 20px 0;
}

.logo-image {
  width: 100px;
  height: 100px;
  object-fit: contain;
}

.app-title {
  margin-top: 12px;
  font-size: 20px;
  color: #323233;
}

.form-container {
  padding: 20px 16px;
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
  padding: 16px;
  margin-top: 32px;
}

.extra-links {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  font-size: 14px;
  color: #666;
}

.extra-links a {
  color: #1989fa;
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
