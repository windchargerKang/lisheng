<template>
  <div class="verification-page">
    <van-nav-bar
      title="订单核销"
      left-arrow
      @click-left="$router.back()"
    />

    <!-- 核销码输入 -->
    <div class="verification-form">
      <van-form @submit="handleVerify">
        <van-cell-group>
          <van-field
            v-model="form.verification_code"
            name="verification_code"
            label="核销码"
            placeholder="请输入核销码（如 1234-5678-9012）"
            maxlength="14"
            :formatter="(val) => formatInput(val)"
            :rules="[{ required: true, message: '请输入核销码' }, { pattern: /^\d{4}-\d{4}-\d{4}$/, message: '核销码格式应为 XXXX-XXXX-XXXX' }]"
          >
            <template #left-icon>
              <van-icon name="orders-o" size="20" />
            </template>
          </van-field>
        </van-cell-group>

        <div class="submit-button">
          <van-button
            type="primary"
            native-type="submit"
            :loading="verifying"
            block
            round
          >
            确认核销
          </van-button>
        </div>
      </van-form>
    </div>

    <!-- 核销结果 -->
    <div v-if="verificationResult" class="verification-result">
      <van-cell-group>
        <van-cell
          :title="verificationResult.success ? '核销成功' : '核销失败'"
          :icon="verificationResult.success ? 'checked' : 'close'"
          :value-color="verificationResult.success ? '#07c160' : '#ee0a24'"
        />
        <van-cell title="订单号" :value="verificationResult.order_no" />
        <van-cell title="服务费" :value="`¥${verificationResult.service_fee}`" />
        <van-cell title="区代利润" :value="`¥${verificationResult.agent_profit}`" />
      </van-cell-group>
    </div>

    <!-- 核销记录 -->
    <div class="verification-history">
      <van-cell-group>
        <template #title>
          <div class="history-title">核销记录</div>
        </template>
        <van-empty v-if="history.length === 0" description="暂无核销记录" />
        <van-list v-else>
          <van-cell
            v-for="item in history"
            :key="item.order_no"
            :title="item.order_no"
            :label="`服务费：¥${item.service_fee} | 区代利润：¥${item.agent_profit}`"
            :value="formatDate(item.created_at)"
            is-link
          />
        </van-list>
      </van-cell-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { showToast } from 'vant'
import api from '@/api'

interface VerificationResult {
  success: boolean
  order_no: string
  service_fee: number
  agent_profit: number
}

interface HistoryItem {
  order_no: string
  service_fee: number
  agent_profit: number
  created_at: string
}

const form = reactive({
  verification_code: '',
})

const verifying = ref(false)

// 格式化输入：自动添加 - 分隔符
const formatInput = (val: string): string => {
  // 移除所有非数字字符
  const digits = val.replace(/\D/g, '').slice(0, 12)
  // 格式化为 XXXX-XXXX-XXXX
  if (digits.length <= 4) return digits
  if (digits.length <= 8) return `${digits.slice(0, 4)}-${digits.slice(4)}`
  return `${digits.slice(0, 4)}-${digits.slice(4, 8)}-${digits.slice(8)}`
}

// 提取纯数字核销码用于提交
const getRawCode = (formattedCode: string): string => {
  return formattedCode.replace(/\D/g, '')
}
const verificationResult = ref<VerificationResult | null>(null)
const history = ref<HistoryItem[]>([])

const handleVerify = async () => {
  verifying.value = true
  try {
    const response = await api.post('/verification/verify', {
      verification_code: getRawCode(form.verification_code),
    })

    verificationResult.value = {
      success: true,
      order_no: response.data.order_no || response.data.order_id,
      service_fee: response.data.service_fee,
      agent_profit: response.data.agent_profit,
    }

    showToast('核销成功')

    // 清空输入
    form.verification_code = ''

    // 刷新核销记录
    loadHistory()
  } catch (error: any) {
    verificationResult.value = {
      success: false,
      order_no: '',
      service_fee: 0,
      agent_profit: 0,
    }

    showToast(error.response?.data?.detail || '核销失败')
  } finally {
    verifying.value = false
  }
}

const loadHistory = async () => {
  // 从 API 加载核销记录（通过查询已核销订单）
  try {
    const response = await api.get('/orders', { params: { status: 'verified', page: 1, page_size: 50 } })
    history.value = (response.data.items || []).map((item: any) => ({
      order_no: item.order_no,
      service_fee: 0,  // 需要后端返回分润金额，后续扩展 API
      agent_profit: 0,
      created_at: item.created_at,
    }))
  } catch (error: any) {
    console.error('加载核销记录失败:', error)
    // 401 未登录或 403 无权限时清空记录
    if (error.response?.status === 401 || error.response?.status === 403) {
      history.value = []
    }
  }
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.verification-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 20px;
  padding-top: 10px;
}

.verification-form {
  margin-top: 10px;
}

.submit-button {
  padding: 20px 16px;
}

.verification-result {
  margin-top: 20px;
}

.verification-history {
  margin-top: 20px;
}

.history-title {
  padding: 16px;
  font-size: 16px;
  font-weight: bold;
  color: #323233;
}
</style>
