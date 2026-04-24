<template>
  <div class="address-edit-page">
    <van-nav-bar
      title="编辑地址"
      left-arrow
      @click-left="$router.back()"
    />

    <van-form @submit="onSubmit">
      <van-cell-group inset class="form-group">
        <van-field
          v-model="form.receiver_name"
          name="receiver_name"
          label="收货人"
          placeholder="请输入收货人姓名"
          :rules="[{ required: true, message: '请输入收货人姓名' }]"
        />
        <van-field
          v-model="form.receiver_phone"
          name="receiver_phone"
          label="手机号"
          type="tel"
          placeholder="请输入手机号"
          :rules="[
            { required: true, message: '请输入手机号' },
            { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' }
          ]"
        />
        <van-field
          v-model="form.receiver_address"
          name="receiver_address"
          label="收货地址"
          type="textarea"
          rows="2"
          placeholder="请输入省/市/区/街道地址"
          :rules="[{ required: true, message: '请输入收货地址' }]"
        />
        <van-field
          v-model="form.detail_address"
          name="detail_address"
          label="详细地址"
          type="textarea"
          rows="2"
          placeholder="选填：门牌号等详细信息"
        />
        <van-cell center title="设为默认地址">
          <template #right-icon>
            <van-switch v-model="form.is_default" size="20" />
          </template>
        </van-cell>
      </van-cell-group>

      <div class="buttons">
        <van-button block type="primary" native-type="submit" class="submit-btn">
          保存地址
        </van-button>
      </div>
    </van-form>

    <!-- 删除按钮（仅编辑模式显示） -->
    <van-button
      v-if="isEditMode"
      block
      type="danger"
      plain
      class="delete-btn"
      @click="confirmDelete"
    >
      删除地址
    </van-button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast, showDialog } from 'vant'
import apiClient from '@/api'

const router = useRouter()
const route = useRoute()

const addressId = computed(() => Number(route.query.id) || 0)
const isEditMode = computed(() => addressId.value > 0)

const form = ref({
  receiver_name: '',
  receiver_phone: '',
  receiver_address: '',
  detail_address: '',
  is_default: false,
})

const fetchAddress = async () => {
  if (!addressId.value) return

  try {
    const response = await apiClient.get(`/addresses/${addressId.value}`)
    const data = response.data
    form.value = {
      receiver_name: data.receiver_name,
      receiver_phone: data.receiver_phone,
      receiver_address: data.receiver_address,
      detail_address: data.detail_address || '',
      is_default: data.is_default,
    }
  } catch (error) {
    console.error('获取地址详情失败:', error)
    showToast('获取地址详情失败')
  }
}

const onSubmit = async () => {
  try {
    if (isEditMode.value) {
      await apiClient.put(`/addresses/${addressId.value}`, form.value)
      showToast('地址更新成功')
    } else {
      const response = await apiClient.post('/addresses', form.value)
      showToast('地址添加成功')
    }

    // 如果是从结算页进入的选择模式，返回并传递地址
    const selectMode = route.query.selectMode === '1'
    if (selectMode) {
      // 重新获取地址列表以获取最新 ID
      const listResponse = await apiClient.get('/addresses')
      const addresses = listResponse.data.items || []
      // 获取刚保存的地址（可能是新增的，取默认的或最后一个）
      const savedAddress = addresses.find((a: any) => a.is_default) || addresses[addresses.length - 1]

      if (savedAddress) {
        localStorage.setItem('selected_address', JSON.stringify(savedAddress))
        window.dispatchEvent(new CustomEvent('address-selected', { detail: savedAddress }))
      }
      router.back()
    } else {
      router.back()
    }
  } catch (error: any) {
    console.error('保存地址失败:', error)
    showToast(error.response?.data?.detail || '保存失败')
  }
}

const confirmDelete = async () => {
  if (!addressId.value) return

  try {
    await showDialog({
      title: '确认删除',
      message: '确定要删除这个收货地址吗？',
    })

    await apiClient.delete(`/addresses/${addressId.value}`)
    showToast('删除成功')
    router.back()
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  fetchAddress()
})
</script>

<style scoped>
.address-edit-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-top: 46px;
}

.form-group {
  margin: 16px;
}

.buttons {
  padding: 16px;
}

.submit-btn {
  margin-bottom: 12px;
}

.delete-btn {
  margin: 0 16px 16px;
}
</style>
