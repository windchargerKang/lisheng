<template>
  <div class="store-apply-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      title="我想开店"
      left-arrow
      @click-left="$router.back()"
    >
      <template #right>
        <van-icon name="orders-o" @click="$router.push('/store-apply/records')" />
      </template>
    </van-nav-bar>

    <!-- 申请类型选择 -->
    <div class="type-selector">
      <div class="type-options">
        <div
          :class="['type-option', applyType === 'SHOP' ? 'active' : '']"
          @click="applyType = 'SHOP'"
        >
          <div class="option-icon">
            <van-icon name="shop-o" />
          </div>
          <div class="option-text">申请店铺</div>
        </div>
        <div
          :class="['type-option', applyType === 'AGENT' ? 'active' : '']"
          @click="applyType = 'AGENT'"
        >
          <div class="option-icon">
            <van-icon name="manager-o" />
          </div>
          <div class="option-text">申请区代</div>
        </div>
      </div>
    </div>

    <!-- 表单内容 -->
    <van-form @submit="onSubmit" class="apply-form">
      <!-- 店铺申请字段 -->
      <template v-if="applyType === 'SHOP'">
        <van-field
          v-model="shopForm.name"
          name="shop_name"
          label="店铺名称"
          placeholder="请输入店铺名称"
          :rules="[{ required: true, message: '请填写店铺名称' }]"
        />
        <van-field
          v-model="shopForm.regionText"
          is-link
          readonly
          name="shop_region"
          label="选择区域"
          placeholder="请选择所在区域"
          @click="showRegionPicker = true"
          :rules="[{ required: true, message: '请选择所在区域' }]"
        />
        <van-field
          v-model="shopForm.agentText"
          readonly
          name="shop_agent"
          label="对应区代"
          placeholder="由所选区域自动关联"
          disabled
        />
        <van-field
          v-model="shopForm.locationText"
          is-link
          readonly
          name="shop_location"
          label="地图定位"
          placeholder="请点击选择店铺位置"
          @click="showMapDialog = true"
          :rules="[{ required: true, message: '请选择店铺位置' }]"
        />
      </template>

      <!-- 区代申请字段 -->
      <template v-else>
        <van-field
          v-model="agentForm.name"
          name="agent_name"
          label="区代名称"
          placeholder="请输入区代名称"
          :rules="[{ required: true, message: '请填写区代名称' }]"
        />
        <van-field
          v-model="agentForm.regionText"
          is-link
          readonly
          name="agent_region"
          label="选择区域"
          placeholder="请选择负责区域"
          @click="showRegionPicker = true"
          :rules="[
            { required: true, message: '请选择负责区域' },
            { validator: validateRegionAvailability, message: '该区域已被申请' }
          ]"
        />
        <van-field
          v-model="agentForm.referrerText"
          is-link
          readonly
          name="agent_referrer"
          label="推荐区代"
          placeholder="请选择推荐区代（选填）"
          @click="showReferrerPicker = true"
        />
      </template>

      <!-- 提交按钮 -->
      <div class="submit-btn-wrapper">
        <van-button round block type="primary" native-type="submit" :loading="submitting">
          {{ submitting ? '提交中...' : '提交申请' }}
        </van-button>
      </div>
    </van-form>

    <!-- 区域选择器 -->
    <van-popup v-model:show="showRegionPicker" position="bottom" :style="{ height: '50vh' }">
      <van-cascader
        v-model="selectedRegion"
        :options="regionOptions"
        title="请选择区域"
        @close="showRegionPicker = false"
        @finish="onRegionFinish"
      />
    </van-popup>

    <!-- 推荐区代选择器 -->
    <van-popup v-model:show="showReferrerPicker" position="bottom">
      <van-picker
        :columns="agentColumns"
        title="选择推荐区代"
        show-toolbar
        @confirm="onReferrerConfirm"
        @cancel="showReferrerPicker = false"
      >
        <template #cancel>
          <span @click="agentForm.referrerId = null; agentForm.referrerText = ''; showReferrerPicker = false">清空</span>
        </template>
      </van-picker>
    </van-popup>

    <!-- 地图选点弹窗 -->
    <van-dialog
      v-model:show="showMapDialog"
      title="选择店铺位置"
      show-cancel-button
      cancel-button-text="取消"
      confirm-button-text="确定"
      @confirm="onMapConfirm"
      @cancel="onMapCancel"
      @open="onMapDialogOpen"
    >
      <div class="map-dialog-content">
        <div id="map-picker-container" ref="mapContainer" class="map-picker-container"></div>
        <div class="selected-location">
          <span>已选位置：{{ shopForm.locationText || '请点击地图选择' }}</span>
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showFailToast, showSuccessToast } from 'vant'
import AMapLoader from '@amap/amap-jsapi-loader'
import apiClient from '@/api'

const router = useRouter()

// 申请类型
const applyType = ref<'SHOP' | 'AGENT'>('SHOP')

// 表单数据
const shopForm = reactive({
  name: '',
  regionId: null as number | null,
  regionText: '',
  agentId: null as number | null,
  agentText: '',
  latitude: null as number | null,
  longitude: null as number | null,
  locationText: '',
})

const agentForm = reactive({
  name: '',
  regionId: null as number | null,
  regionText: '',
  referrerId: null as number | null,
  referrerText: '',
})

// 选择器状态
const showRegionPicker = ref(false)
const showReferrerPicker = ref(false)
const showMapDialog = ref(false)

// 选中区域
const selectedRegion = ref<any[]>([])
const regionOptions = ref<any[]>([])
const selectedRegionText = ref<string[]>([])

// 区代列表
const agents = ref<any[]>([])

// 提交状态
const submitting = ref(false)

// 地图相关
const map = ref<any>(null)
const marker = ref<any>(null)
const mapContainer = ref<HTMLElement | null>(null)
const mapInitialized = ref(false)

// 加载区域数据
const loadRegions = async () => {
  try {
    const res = await apiClient.get('/regions')
    // API 返回格式：{ regions: tree }
    const tree = res.data.regions || []
    console.log('区域树:', tree)

    // 转换为 van-cascader 需要的格式
    const convertTree = (nodes: any[]): any[] => {
      return nodes.map((node) => {
        const result: any = {
          text: node.name,
          value: node.id,
        }
        // 只有有子节点时才添加 children，否则不添加（让 van-cascader 识别为叶子节点）
        if (node.children && node.children.length > 0) {
          result.children = convertTree(node.children)
        }
        return result
      })
    }

    regionOptions.value = convertTree(tree)
    console.log('转换后的区域树:', regionOptions.value)
  } catch (error) {
    console.error('加载区域失败:', error)
    showToast('加载区域失败')
  }
}

// 加载区代列表
const loadAgents = async () => {
  try {
    const res = await apiClient.get('/agents', { params: { page: 1, page_size: 100 } })
    agents.value = res.data.items || []
  } catch (error) {
    console.error('加载区代失败:', error)
  }
}

// 区域选择完成
const onRegionFinish = (e: any) => {
  console.log('finish 事件:', e)
  // van-cascader 的 finish 事件参数包含 selectedOptions
  const selectedOptions = e.selectedOptions || []

  if (selectedOptions.length === 0) {
    console.warn('没有选中的区域')
    showRegionPicker.value = false
    return
  }

  const lastOption = selectedOptions[selectedOptions.length - 1]
  const regionId = lastOption?.value
  const regionText = selectedOptions.map((o: any) => o.text).join('/')

  console.log('区域 ID:', regionId)
  console.log('区域文本:', regionText)

  if (applyType.value === 'SHOP') {
    shopForm.regionId = regionId
    shopForm.regionText = regionText
    console.log('店铺申请 - 设置 regionId:', shopForm.regionId, 'regionText:', shopForm.regionText)
    // 根据区域自动选择对应区代
    const agent = agents.value.find((a: any) => a.region_id === regionId)
    if (agent) {
      shopForm.agentId = agent.id
      shopForm.agentText = agent.name || `${lastOption.text}区代`
    }
  } else {
    agentForm.regionId = regionId
    agentForm.regionText = regionText
    console.log('区代申请 - 设置 regionId:', agentForm.regionId, 'regionText:', agentForm.regionText)
  }

  showRegionPicker.value = false
  // 重置选中状态
  selectedRegion.value = []
}

// 推荐区代确认
const onReferrerConfirm = ({ selectedOptions }: any) => {
  const option = selectedOptions[0]
  agentForm.referrerId = option.value
  agentForm.referrerText = option.text
  showReferrerPicker.value = false
}

// 区域可用性校验
const validateRegionAvailability = async (value: any) => {
  if (!agentForm.regionId) return true

  try {
    const res = await apiClient.get('/store-applications/check-region', {
      params: { region_id: agentForm.regionId, type: 'AGENT' },
    })
    return res.data.available
  } catch {
    return true
  }
}

// 初始化地图
const initMapPicker = async () => {
  if (mapInitialized.value) return

  try {
    await new Promise(resolve => setTimeout(resolve, 100))

    window._AMapSecurityConfig = {
      securityJsCode: 'a4ffb9efc6af3053bd6ca94633d2fa40',
    }

    const AMap = await AMapLoader.load({
      key: 'aa44b61446e611d6aa60fdd137973e31',
      version: '2.0',
      plugins: ['AMap.Map', 'AMap.Marker'],
    })

    map.value = new AMap.Map('map-picker-container', {
      zoom: 13,
      center: [114.026, 30.593],
    })

    // 点击地图添加标记
    map.value.on('click', (e: any) => {
      const lnglat = e.lnglat
      shopForm.longitude = lnglat.lng
      shopForm.latitude = lnglat.lat
      shopForm.locationText = `${lnglat.lat.toFixed(6)}, ${lnglat.lng.toFixed(6)}`

      if (marker.value) {
        marker.value.setPosition(lnglat)
      } else {
        marker.value = new AMap.Marker({
          position: lnglat,
          map: map.value,
        })
      }
    })

    mapInitialized.value = true
  } catch (error) {
    console.error('地图加载失败:', error)
    showToast('地图加载失败')
  }
}

// 地图弹窗打开时初始化地图
const onMapDialogOpen = async () => {
  await initMapPicker()
  // 延迟更新地图尺寸
  setTimeout(() => {
    if (map.value) {
      map.value.resize()
    }
  }, 300)
}

// 地图确定
const onMapConfirm = () => {
  if (!shopForm.latitude || !shopForm.longitude) {
    showToast('请选择店铺位置')
    return false
  }
  showMapDialog.value = false
  cleanupMap()
  return true
}

// 地图取消
const onMapCancel = () => {
  showMapDialog.value = false
  cleanupMap()
}

// 清理地图
const cleanupMap = () => {
  if (map.value) {
    map.value.destroy()
    map.value = null
    marker.value = null
    mapInitialized.value = false
  }
}

// 提交申请
const onSubmit = async () => {
  submitting.value = true

  try {
    const payload: any = {
      apply_type: applyType.value,
    }

    if (applyType.value === 'SHOP') {
      payload.shop_name = shopForm.name
      payload.shop_region_id = shopForm.regionId
      payload.shop_agent_id = shopForm.agentId
      payload.shop_latitude = shopForm.latitude
      payload.shop_longitude = shopForm.longitude
    } else {
      payload.agent_name = agentForm.name
      payload.agent_region_id = agentForm.regionId
      payload.referrer_id = agentForm.referrerId
    }

    await apiClient.post('/store-applications', payload)
    showSuccessToast('申请提交成功，请等待审核')
    router.push('/store-apply/records')
  } catch (error: any) {
    showFailToast(error.response?.data?.detail || '申请提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadRegions(), loadAgents()])
})
</script>

<style scoped>
.store-apply-page {
  min-height: 100vh;
  background-color: #F5F5F5;
  padding: 50px 0 0;
  position: relative;
}

/* 顶部毛玻璃效果 */
.store-apply-page::before {
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

/* 申请类型选择 */
.type-selector {
  margin: 15px;
  padding: 20px 15px;
  background-color: #FFFFFF;
  border-radius: 12px;
}

.type-options {
  display: flex;
  justify-content: space-around;
  gap: 20px;
}

.type-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 25px;
  border-radius: 12px;
  background-color: #F5F5F5;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 100px;
}

.type-option.active {
  background-color: #FF9500;
  color: #FFFFFF;
}

.option-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.option-text {
  font-size: 14px;
}

/* 表单 */
.apply-form {
  margin: 15px;
  background-color: #FFFFFF;
  border-radius: 12px;
  overflow: hidden;
}

/* 提交按钮 */
.submit-btn-wrapper {
  padding: 20px 15px 40px;
}

/* 地图弹窗 */
.map-dialog-content {
  padding: 0;
  overflow: hidden;
}

.map-picker-container {
  width: 100%;
  height: 400px;
  background-color: #f0f0f0;
}

.selected-location {
  padding: 15px;
  background-color: #F5F5F5;
  font-size: 14px;
  color: #666666;
}
</style>
