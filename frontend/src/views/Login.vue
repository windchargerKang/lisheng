<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="login-title">渠道销售管理系统</h2>
      <el-form :model="loginForm" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleLogin" style="width: 100%">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores'
import { login } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  await formRef.value?.validate()
  loading.value = true

  try {
    const result = await login(loginForm)

    userStore.setToken(result.token)
    userStore.setUserInfo(result.user)

    ElMessage.success('登录成功')
    router.push('/')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  padding: 20px;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
  font-size: 24px;
}
</style>
