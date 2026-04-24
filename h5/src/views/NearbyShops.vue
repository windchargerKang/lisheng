<template>
  <div class="nearby-shops-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      title="附近店铺"
      left-arrow
      @click-left="$router.back()"
    />

    <!-- 半径选择 -->
    <van-cell-group :border="false" class="radius-group">
      <van-cell :border="false">
        <template #title>
          <div class="radius-selector">
            <span class="radius-label">筛选范围：</span>
            <van-radio-group v-model="selectedRadius" direction="horizontal">
              <van-radio name="3">3km</van-radio>
              <van-radio name="5">5km</van-radio>
              <van-radio name="10">10km</van-radio>
              <van-radio name="20">20km</van-radio>
            </van-radio-group>
          </div>
        </template>
        <template #right-icon>
          <van-button type="primary" size="small" @click="loadNearbyShops">刷新</van-button>
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 地图容器 -->
    <div id="map-container" class="map-container"></div>

    <!-- 店铺列表 -->
    <div class="shop-list" v-if="nearbyShops.length > 0">
      <div
        class="shop-item"
        v-for="(shop, index) in nearbyShops"
        :key="index"
        @click="showShopDetail(shop)"
      >
        <div class="shop-info">
          <span class="shop-name">{{ shop.name || `店铺${shop.id}` }}</span>
          <span class="shop-distance">{{ shop.distance }}km</span>
        </div>
        <div class="shop-address">{{ shop.address || '暂无地址信息' }}</div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-if="nearbyShops.length === 0 && !loading">
      <div class="empty-icon">📍</div>
      <div class="empty-text">附近暂无店铺</div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-state" v-if="loading">
      <van-loading color="#1989fa">正在加载附近店铺...</van-loading>
    </div>

    <!-- 店铺详情弹窗 -->
    <van-dialog
      v-model:show="shopDetailVisible"
      :title="currentShop?.name || '店铺详情'"
      show-cancel-button
      @confirm="handleNavigate"
    >
      <div class="shop-detail">
        <p><strong>地址：</strong>{{ currentShop?.address || '暂无' }}</p>
        <p><strong>距离：</strong>{{ currentShop?.distance }}km</p>
        <p v-if="currentShop?.phone"><strong>电话：</strong>{{ currentShop.phone }}</p>
      </div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showNotify } from 'vant'
import AMapLoader from '@amap/amap-jsapi-loader'
import apiClient from '@/api'

const router = useRouter()

// 地图相关
const map = ref<any>(null)
const shopMarkers = ref<any[]>([])

// 用户位置
const userLocation = reactive({
  latitude: 30.593,
  longitude: 114.026,
})

// 半径选择
const selectedRadius = ref('5')

// 店铺列表
const nearbyShops = ref<any[]>([])

// 店铺详情
const shopDetailVisible = ref(false)
const currentShop = ref<any>(null)

// 加载状态
const loading = ref(false)

// Haversine 公式计算距离（单位：km）
const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
  const R = 6371 // 地球半径（km）
  const dLat = ((lat2 - lat1) * Math.PI) / 180
  const dLon = ((lon2 - lon1) * Math.PI) / 180
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return parseFloat((R * c).toFixed(2))
}

// 初始化地图
const initMap = async () => {
  try {
    // 设置安全密钥（2021 年 12 月后注册的 Key 需要）
    window._AMapSecurityConfig = {
      securityJsCode: 'a4ffb9efc6af3053bd6ca94633d2fa40',
    }

    const AMap = await AMapLoader.load({
      key: 'aa44b61446e611d6aa60fdd137973e31',
      version: '2.0',
      plugins: ['AMap.Map', 'AMap.Marker', 'AMap.Geolocation'],
    })

    // 创建地图
    map.value = new AMap.Map('map-container', {
      zoom: 13,
      center: [114.026, 30.593], // 默认武汉
    })

    // 获取用户位置
    await getUserLocation(AMap)
  } catch (error) {
    console.error('地图加载失败:', error)
    showToast('地图加载失败')
  }
}

// 获取用户位置
const getUserLocation = async (AMap: any) => {
  return new Promise<void>((resolve) => {
    // 使用浏览器地理定位
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          userLocation.latitude = position.coords.latitude
          userLocation.longitude = position.coords.longitude

          // 更新地图中心
          map.value.setCenter([userLocation.longitude, userLocation.latitude])

          // 添加用户位置标记
          new AMap.Marker({
            position: [userLocation.longitude, userLocation.latitude],
            map: map.value,
            icon: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
          })

          // 加载附近店铺
          await loadNearbyShops()
          resolve()
        },
        (error) => {
          console.error('获取位置失败:', error)
          showToast('获取位置失败，使用默认位置')
          // 使用默认位置
          userLocation.latitude = 30.593
          userLocation.longitude = 114.026
          map.value.setCenter([114.026, 30.593])
          loadNearbyShops()
          resolve()
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        }
      )
    } else {
      showToast('浏览器不支持地理定位')
      userLocation.latitude = 30.593
      userLocation.longitude = 114.026
      map.value.setCenter([114.026, 30.593])
      loadNearbyShops()
      resolve()
    }
  })
}

// 加载附近店铺
const loadNearbyShops = async () => {
  loading.value = true
  try {
    // 获取所有店铺
    const response = await apiClient.get('/shops', {
      params: { page: 1, page_size: 100 },
    })

    const radius = parseFloat(selectedRadius.value)

    // 前端计算距离并筛选
    const shopsWithDistance = response.data.items
      .filter((shop: any) => shop.latitude && shop.longitude)
      .map((shop: any) => {
        const distance = calculateDistance(
          userLocation.latitude,
          userLocation.longitude,
          shop.latitude,
          shop.longitude
        )
        return { ...shop, distance }
      })
      .filter((shop: any) => shop.distance <= radius)
      .sort((a: any, b: any) => a.distance - b.distance)

    nearbyShops.value = shopsWithDistance

    // 更新地图标记
    updateShopMarkers(AMap, shopsWithDistance)

    if (shopsWithDistance.length === 0) {
      showToast('附近暂无店铺')
    }
  } catch (error: any) {
    console.error('加载店铺失败:', error)
    showToast('加载店铺失败')
  } finally {
    loading.value = false
  }
}

// 更新店铺标记
const updateShopMarkers = (AMap: any, shops: any[]) => {
  // 清除旧标记
  shopMarkers.value.forEach((m) => m.setMap(null))
  shopMarkers.value = []

  // 添加新标记
  shops.forEach((shop: any) => {
    const shopMarker = new AMap.Marker({
      position: [shop.longitude, shop.latitude],
      map: map.value,
      title: shop.name || `店铺${shop.id}`,
    })

    // 点击标记显示详情
    shopMarker.on('click', () => {
      currentShop.value = shop
      shopDetailVisible.value = true
    })

    shopMarkers.value.push(shopMarker)
  })
}

// 显示店铺详情
const showShopDetail = (shop: any) => {
  currentShop.value = shop
  shopDetailVisible.value = true
}

// 导航到店
const handleNavigate = async () => {
  if (!currentShop.value?.latitude || !currentShop.value?.longitude) {
    showToast('店铺位置信息不完整')
    return
  }

  // 打开高德地图导航
  const url = `https://uri.amap.com/marker?position=${currentShop.value.longitude},${currentShop.value.latitude}&name=${encodeURIComponent(currentShop.value.name || '店铺')}`

  if (/Android/.test(navigator.userAgent)) {
    window.location.href = `androidamap://navi?sourceApplication=力生大健康&lat=${currentShop.value.latitude}&lon=${currentShop.value.longitude}&dev=0`
  } else if (/iPhone/.test(navigator.userAgent)) {
    window.location.href = `iosamap://navi?sourceApplication=力生大健康&lat=${currentShop.value.latitude}&lon=${currentShop.value.longitude}&dev=0`
  } else {
    window.open(url, '_blank')
  }
}

onMounted(async () => {
  await nextTick()
  await initMap()
})
</script>

<style scoped>
.nearby-shops-page {
  min-height: 100vh;
  background-color: #F5F5F5;
  padding-top: 46px;
  position: relative;
}

.radius-group {
  margin-bottom: 10px;
}

.radius-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.radius-label {
  font-size: 14px;
  color: #666666;
}

.radius-selector :deep(.van-radio-group) {
  flex: 1;
}

.map-container {
  width: 100%;
  height: calc(100vh - 200px);
}

.shop-list {
  background-color: #FFFFFF;
  margin: 10px 15px;
  border-radius: 12px;
  overflow: hidden;
}

.shop-item {
  padding: 15px;
  border-bottom: 1px solid #F0F0F0;
  cursor: pointer;
}

.shop-item:last-child {
  border-bottom: none;
}

.shop-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.shop-name {
  font-size: 15px;
  font-weight: bold;
  color: #333333;
}

.shop-distance {
  font-size: 13px;
  color: #FF9500;
  font-weight: bold;
}

.shop-address {
  font-size: 12px;
  color: #999999;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.empty-text {
  font-size: 14px;
  color: #999999;
}

.loading-state {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(0, 0, 0, 0.7);
  color: #FFFFFF;
  padding: 15px 25px;
  border-radius: 8px;
  z-index: 1000;
}

.shop-detail {
  padding: 16px;
}

.shop-detail p {
  margin: 8px 0;
  font-size: 14px;
}
</style>
