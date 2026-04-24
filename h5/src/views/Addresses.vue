<template>
  <div class="addresses-page">
    <van-nav-bar
      title="收货地址"
      left-arrow
      @click-left="$router.back()"
    >
      <template #right>
        <van-icon name="plus" @click="goToEdit()" />
      </template>
    </van-nav-bar>

    <van-empty v-if="addresses.length === 0" description="暂无收货地址" />

    <div v-else class="address-list">
      <van-cell
        v-for="addr in addresses"
        :key="addr.id"
        clickable
        @click="selectAddress(addr)"
      >
        <template #title>
          <div class="address-item" :class="{ default: addr.is_default }">
            <div class="address-header">
              <span class="receiver-name">{{ addr.receiver_name }}</span>
              <span class="receiver-phone">{{ addr.receiver_phone }}</span>
              <van-tag v-if="addr.is_default" type="primary" size="mini">默认</van-tag>
            </div>
            <div class="address-detail">{{ addr.receiver_address }}</div>
          </div>
        </template>
        <template #right-icon>
          <div class="address-actions">
            <van-icon name="edit" @click.stop="goToEdit(addr)" />
            <van-icon name="delete-o" @click.stop="confirmDelete(addr)" />
          </div>
        </template>
      </van-cell>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast, showDialog } from 'vant'
import apiClient from '@/api'

const router = useRouter()
const route = useRoute()

// 是否为选择模式（从结算页进入）
const isSelectMode = route.query.selectMode === '1'

interface Address {
  id: number
  receiver_name: string
  receiver_phone: string
  receiver_address: string
  province?: string
  city?: string
  district?: string
  detail_address?: string
  is_default: boolean
}

const addresses = ref<Address[]>([])

const fetchAddresses = async () => {
  try {
    const response = await apiClient.get('/addresses')
    addresses.value = response.data.items || []
  } catch (error) {
    console.error('获取地址列表失败:', error)
    showToast('获取地址列表失败')
  }
}

const selectAddress = (addr: Address) => {
  if (isSelectMode) {
    // 返回到结算页并传递地址信息
    router.back()
    // 通过事件或 localStorage 传递地址
    localStorage.setItem('selected_address', JSON.stringify(addr))
    // 触发结算页的地址更新
    window.dispatchEvent(new CustomEvent('address-selected', { detail: addr }))
  } else {
    goToEdit(addr)
  }
}

const goToEdit = (addr?: Address) => {
  if (addr) {
    router.push(`/addresses/edit?id=${addr.id}`)
  } else {
    router.push('/addresses/edit')
  }
}

const confirmDelete = async (addr: Address) => {
  try {
    await showDialog({
      title: '确认删除',
      message: '确定要删除这个收货地址吗？',
    })

    await apiClient.delete(`/addresses/${addr.id}`)
    showToast('删除成功')
    fetchAddresses()
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  fetchAddresses()
})
</script>

<style scoped>
.addresses-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 50px 0 0;
  position: relative;
}

/* 顶部毛玻璃效果 */
.addresses-page::before {
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

.address-list {
  padding: 16px;
}

.address-item {
  padding: 12px;
  background: white;
  border-radius: 8px;
  margin-bottom: 12px;
}

.address-item.default {
  border: 1px solid #1989fa;
}

.address-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.receiver-name {
  font-size: 15px;
  font-weight: 600;
  color: #323233;
}

.receiver-phone {
  font-size: 14px;
  color: #646566;
}

.address-detail {
  font-size: 14px;
  color: #646566;
  line-height: 1.5;
}

.address-actions {
  display: flex;
  gap: 16px;
  color: #969799;
}

.address-actions van-icon {
  font-size: 18px;
}
</style>
