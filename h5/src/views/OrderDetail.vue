<template>
  <div class="order-detail-page">
    <van-nav-bar
      title="订单详情"
      left-arrow
      @click-left="$router.back()"
    />

    <div v-if="order" class="order-content">
      <!-- 订单状态 -->
      <van-cell-group class="status-group">
        <van-cell center :border="false">
          <template #title>
            <div class="status-info">
              <van-icon :name="getStatusIcon(order.status)" size="24" />
              <span class="status-text">{{ getStatusText(order.status) }}</span>
            </div>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 订单信息 -->
      <van-cell-group class="info-group">
        <van-cell title="订单编号" :value="order.order_no" />
        <van-cell title="下单时间" :value="formatDate(order.created_at)" />
        <van-cell title="订单状态" :value="getStatusText(order.status)" />
      </van-cell-group>

      <!-- 收货地址（待确认状态可修改） -->
      <van-cell-group class="address-group">
        <van-cell title="收货地址" :border="false">
          <template #right-icon>
            <van-icon
              v-if="canEdit"
              name="edit"
              size="18"
              @click="openAddressEdit"
            />
          </template>
          <div class="address-content">
            <div>{{ order.receiver_name }} {{ order.receiver_phone }}</div>
            <div>{{ order.receiver_address }}</div>
          </div>
        </van-cell>
      </van-cell-group>

      <!-- 订单备注（待确认状态可修改） -->
      <van-cell-group class="remark-group">
        <van-cell title="订单备注" :border="false">
          <template #right-icon>
            <van-icon
              v-if="canEdit"
              name="edit"
              size="18"
              @click="showRemarkEdit = true"
            />
          </template>
          <div class="remark-content">
            {{ order.remark || '无备注' }}
          </div>
        </van-cell>
      </van-cell-group>

      <!-- 商品列表 -->
      <van-cell-group class="items-group">
        <van-cell title="商品信息" :border="false" />
        <div class="items-list">
          <div
            v-for="item in order.items"
            :key="item.product_id"
            class="item-row"
          >
            <div class="item-info">
              <div class="item-name">{{ item.product_name }}</div>
              <div class="item-detail">
                <span>单价：¥{{ item.unit_price }}</span>
                <span>数量：{{ item.quantity }}</span>
              </div>
            </div>
            <div class="item-subtotal">¥{{ item.subtotal }}</div>
          </div>
        </div>
      </van-cell-group>

      <!-- 修改地址弹窗 -->
      <van-dialog
        v-model:show="showAddressEdit"
        title="修改收货地址"
        show-cancel-button
        @confirm="confirmAddressEdit"
      >
        <div class="edit-dialog">
          <van-radio-group v-model="selectedAddressId">
            <van-cell
              v-for="addr in addresses"
              :key="addr.id"
              clickable
              @click="selectedAddressId = addr.id"
            >
              <template #title>
                <div>
                  <div>{{ addr.receiver_name }} {{ addr.receiver_phone }}</div>
                  <div style="font-size: 12px; color: #969799;">{{ addr.receiver_address }}</div>
                </div>
              </template>
              <template #right-icon>
                <van-radio :name="addr.id" icon-size="16px" />
              </template>
            </van-cell>
          </van-radio-group>
          <van-divider>或手动输入</van-divider>
          <van-field
            v-model="customAddress.receiver_name"
            label="收货人"
            placeholder="请输入姓名"
          />
          <van-field
            v-model="customAddress.receiver_phone"
            label="手机号"
            type="tel"
            placeholder="请输入手机号"
          />
          <van-field
            v-model="customAddress.receiver_address"
            label="地址"
            type="textarea"
            rows="2"
            placeholder="请输入详细地址"
          />
        </div>
      </van-dialog>

      <!-- 修改备注弹窗 -->
      <van-dialog
        v-model:show="showRemarkEdit"
        title="修改订单备注"
        show-cancel-button
        @confirm="confirmRemarkEdit"
      >
        <van-field
          v-model="editRemark"
          type="textarea"
          rows="3"
          placeholder="请输入订单备注"
        />
      </van-dialog>

      <!-- 核销码（仅核销模式订单且已完成） -->
      <van-cell-group v-if="order.order_type === 'verification' && order.status === 'completed' && order.verification_code_obj" class="code-group">
        <van-cell title="核销码" :border="false">
          <template #right-icon>
            <van-tag type="primary" size="large" @click="copyCode(order.verification_code_obj.code)">
              {{ formatVerificationCode(order.verification_code_obj.code) }}
            </van-tag>
          </template>
          <template #label>
            <div style="font-size: 12px; color: #969799; margin-top: 4px;">
              点击复制核销码，出示给店铺进行核销
            </div>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 金额信息 -->
      <van-cell-group class="amount-group">
        <van-cell title="订单金额" :value="'¥' + order.total_amount" />
      </van-cell-group>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <van-button
          v-if="order.status === 'pending'"
          plain
          type="danger"
          @click="handleCancel"
        >
          取消订单
        </van-button>
        <van-button
          v-if="order.status === 'pending'"
          type="primary"
          @click="handleConfirm"
        >
          确认订单
        </van-button>
        <van-button
          v-if="order.status === 'shipped'"
          type="primary"
          @click="handleConfirmReceipt"
        >
          确认收货
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { showToast, showConfirmDialog, showDialog, showNotify } from 'vant'
import apiClient from '@/api'

const route = useRoute()
const order = ref<any>(null)

// 编辑状态
const showAddressEdit = ref(false)
const showRemarkEdit = ref(false)
const selectedAddressId = ref<number | null>(null)
const addresses = ref<any[]>([])
const customAddress = ref({
  receiver_name: '',
  receiver_phone: '',
  receiver_address: '',
})
const editRemark = ref('')

// 是否可编辑（只有待确认订单可修改）
const canEdit = computed(() => {
  return order.value?.status === 'pending'
})

const getStatusIcon = (status: string): string => {
  const iconMap: Record<string, string> = {
    pending: 'clock-o',
    confirmed: 'checked',
    shipped: 'truck-o',
    completed: 'success',
    cancelled: 'close',
  }
  return iconMap[status] || 'info-o'
}

const getStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    pending: '待确认',
    confirmed: '待发货',
    shipped: '已发货',
    completed: '已完成',
    verified: '已核销',
    cancelled: '已取消',
  }
  return textMap[status] || status
}

const formatVerificationCode = (code: string | null): string => {
  if (!code) return ''
  // 格式化为 4-4-4 形式：1234-5678-9012
  return code.replace(/(\d{4})(\d{4})(\d{4})/, '$1-$2-$3')
}

const copyCode = async (code: string | null) => {
  if (!code) return
  try {
    await navigator.clipboard.writeText(code)
    showNotify({ type: 'success', message: '核销码已复制' })
  } catch (error) {
    showToast('复制失败')
  }
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const fetchOrderDetail = async () => {
  try {
    const orderId = route.params.id
    const response = await apiClient.get(`/orders/${orderId}`)
    order.value = response.data
  } catch (error) {
    console.error('获取订单详情失败:', error)
    showToast('加载失败')
  }
}

const fetchAddresses = async () => {
  try {
    const response = await apiClient.get('/addresses')
    addresses.value = response.data.items || []
  } catch (error) {
    console.error('获取地址列表失败:', error)
  }
}

const openAddressEdit = async () => {
  // 重置状态
  selectedAddressId.value = null
  customAddress.value = {
    receiver_name: '',
    receiver_phone: '',
    receiver_address: '',
  }
  // 加载地址列表
  await fetchAddresses()
  showAddressEdit.value = true
}

const confirmAddressEdit = async () => {
  try {
    let updateData: any = {}

    // 如果选择了已有地址
    if (selectedAddressId.value) {
      const addr = addresses.value.find(a => a.id === selectedAddressId.value)
      if (addr) {
        updateData = {
          receiver_name: addr.receiver_name,
          receiver_phone: addr.receiver_phone,
          receiver_address: addr.receiver_address,
        }
      }
    } else if (customAddress.value.receiver_name && customAddress.value.receiver_address) {
      // 使用手动输入的地址
      updateData = { ...customAddress.value }
    } else {
      showToast('请选择地址或填写收货信息')
      return false
    }

    // 调用后端 API 更新订单
    await apiClient.put(`/orders/${order.value.id}/address`, updateData)
    showToast('地址已更新')
    fetchOrderDetail()
    return true
  } catch (error: any) {
    showToast(error.response?.data?.detail || '更新失败')
    return false
  }
}

const confirmRemarkEdit = async () => {
  try {
    await apiClient.put(`/orders/${order.value.id}/remark`, {
      remark: editRemark.value,
    })
    showToast('备注已更新')
    fetchOrderDetail()
    return true
  } catch (error: any) {
    showToast(error.response?.data?.detail || '更新失败')
    return false
  }
}

const handleCancel = async () => {
  try {
    await showConfirmDialog({
      title: '确认取消',
      message: '确定要取消该订单吗？',
    })
    await apiClient.post(`/orders/${order.value.id}/cancel`)
    showToast('订单已取消')
    fetchOrderDetail()
  } catch {
    // 用户取消
  }
}

const handleConfirm = async () => {
  try {
    await showConfirmDialog({
      title: '确认订单',
      message: '确认后将使用钱包余额支付，是否继续？',
    })
    await apiClient.post(`/orders/${order.value.id}/confirm`)
    showToast('订单已确认')
    fetchOrderDetail()
  } catch (error: any) {
    // 用户取消确认
    if (error !== 'cancel') {
      showToast(error.response?.data?.detail || '操作失败')
    }
  }
}

const handleConfirmReceipt = async () => {
  try {
    await showConfirmDialog({
      title: '确认收货',
      message: '请确认您已收到商品，确认后将完成订单。',
    })
    await apiClient.post(`/orders/${order.value.id}/confirm`)
    showToast('确认收货成功')
    fetchOrderDetail()
  } catch (error: any) {
    // 用户取消确认
    if (error !== 'cancel') {
      showToast(error.response?.data?.detail || '操作失败')
    }
  }
}

onMounted(() => {
  fetchOrderDetail()
})
</script>

<style scoped>
.order-detail-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 50px 0 120px;
  position: relative;
}

/* 顶部毛玻璃效果 */
.order-detail-page::before {
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

.action-buttons {
  position: fixed;
  bottom: 50px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: flex-end;
  padding: 10px 16px;
  background-color: #fff;
  border-top: 1px solid #eee;
  gap: 12px;
  z-index: 1000;
}

.status-info {
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-text {
  margin-left: 8px;
  font-size: 16px;
  font-weight: bold;
  color: #1989fa;
}

.info-group,
.items-group,
.amount-group {
  margin-top: 16px;
}

.items-list {
  padding: 0 16px 16px;
}

.item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.item-row:last-child {
  border-bottom: none;
}

.item-info {
  flex: 1;
}

.item-name {
  font-size: 14px;
  color: #323233;
  margin-bottom: 4px;
}

.item-detail {
  font-size: 12px;
  color: #969799;
  display: flex;
  gap: 16px;
}

.item-subtotal {
  font-size: 14px;
  font-weight: bold;
  color: #f44;
}

.amount-group :deep(.van-cell__value) {
  color: #f44;
  font-weight: bold;
}

.action-buttons :deep(.van-button) {
  width: 100px;
}
</style>
