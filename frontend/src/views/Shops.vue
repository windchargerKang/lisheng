<template>
  <div class="page-container">
    <div class="page-header">
      <h2>店铺管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增店铺
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="区域">
          <el-select v-model="filterForm.region_id" placeholder="全部区域" clearable>
            <el-option label="全部区域" value="" />
            <el-option v-for="region in regions" :key="region.id" :label="region.name" :value="region.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="全部状态" value="" />
            <el-option label="营业中" value="active" />
            <el-option label="已停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchShops">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 店铺列表 -->
    <el-card class="table-card">
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="店铺名称" width="150" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="region_name" label="区域" width="120" />
        <el-table-column prop="agent_name" label="绑定区代" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '营业中' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @change="fetchShops"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="店铺名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入店铺名称（可选）" style="width: 100%" />
        </el-form-item>
        <el-form-item label="用户" prop="user_id">
          <el-select v-model="form.user_id" placeholder="请选择用户" filterable style="width: 100%">
            <el-option v-for="user in users" :key="user.id" :label="user.username" :value="user.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="区域" prop="region_id">
          <el-select v-model="form.region_id" placeholder="请选择区域" filterable style="width: 100%">
            <el-option v-for="region in regions" :key="region.id" :label="region.name" :value="region.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="绑定区代" prop="agent_id">
          <el-select v-model="form.agent_id" placeholder="请选择绑定区代（可选）" filterable clearable style="width: 100%">
            <el-option v-for="agent in agents" :key="agent.id" :label="agent.name || `区代${agent.id}`" :value="agent.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="店铺坐标">
          <div style="display: flex; gap: 8px; align-items: center; width: 100%">
            <el-input
              v-model="form.latitude"
              placeholder="纬度"
              style="width: 45%"
              :readonly="true"
              @click="openMapPicker"
            />
            <el-input
              v-model="form.longitude"
              placeholder="经度"
              style="width: 45%"
              :readonly="true"
              @click="openMapPicker"
            />
            <el-button type="primary" @click="openMapPicker">选点</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 地图选点弹窗 -->
    <el-dialog v-model="mapDialogVisible" title="选择店铺位置" width="800px">
      <div id="map-container" style="width: 100%; height: 400px;"></div>
      <div style="margin-top: 16px; text-align: center;">
        <el-button type="primary" @click="confirmMapSelection">确认选择</el-button>
        <el-button @click="mapDialogVisible = false">取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import apiClient from '@/api'
import AMapLoader from '@amap/amap-jsapi-loader'

interface Shop {
  id: number
  name: string | null
  user_id: number
  username?: string
  region_id: number
  region_name?: string
  agent_id: number | null
  agent_name?: string
  status: string
  latitude?: number | null
  longitude?: number | null
}

interface Region {
  id: number
  name: string
}

interface User {
  id: number
  username: string
}

interface Agent {
  id: number
  name: string | null
}

const loading = ref(false)
const tableData = ref<Shop[]>([])
const regions = ref<Region[]>([])
const users = ref<User[]>([])
const agents = ref<Agent[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增店铺')
const submitting = ref(false)
const formRef = ref()

const filterForm = reactive({
  region_id: null as number | null,
  status: '',
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

const form = reactive({
  id: null as number | null,
  name: '',
  user_id: null as number | null,
  region_id: null as number | null,
  agent_id: null as number | null,
  latitude: null as number | null,
  longitude: null as number | null,
})

const mapDialogVisible = ref(false)
const map = ref<any>(null)
const marker = ref<any>(null)

const rules = {
  user_id: [{ required: true, message: '请输入用户 ID', trigger: 'blur' }],
  region_id: [{ required: true, message: '请输入区域 ID', trigger: 'blur' }],
}

const fetchShops = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: pagination.page,
      page_size: pagination.page_size,
    }
    if (filterForm.region_id) params.region_id = filterForm.region_id
    if (filterForm.status) params.status = filterForm.status

    const response = await apiClient.get('/shops', { params })
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error('加载店铺数据失败')
  } finally {
    loading.value = false
  }
}

const fetchRegions = async () => {
  try {
    const response = await apiClient.get('/regions')
    // 扁平化区域树
    const flattenRegions = (list: Region[]): Region[] => {
      let result: Region[] = []
      for (const item of list) {
        result.push({ id: item.id, name: item.name })
        if (item.children) {
          result = result.concat(flattenRegions(item.children))
        }
      }
      return result
    }
    regions.value = flattenRegions(response.data.regions)
  } catch (error: any) {
    console.error('加载区域失败', error)
  }
}

const fetchUsers = async () => {
  try {
    const response = await apiClient.get('/users', { params: { page: 1, page_size: 100 } })
    users.value = response.data.items.map((item: any) => ({
      id: item.id,
      username: item.username,
    }))
  } catch (error: any) {
    console.error('加载用户失败', error)
  }
}

const fetchAgentsList = async () => {
  try {
    const response = await apiClient.get('/agents', { params: { page: 1, page_size: 100 } })
    agents.value = response.data.items
  } catch (error: any) {
    console.error('加载区代列表失败', error)
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增店铺'
  form.id = null
  form.name = ''
  form.user_id = null
  form.region_id = null
  form.agent_id = null
  dialogVisible.value = true
}

const handleEdit = (row: Shop) => {
  dialogTitle.value = '编辑店铺'
  form.id = row.id
  form.name = row.name || ''
  form.user_id = row.user_id
  form.region_id = row.region_id
  form.agent_id = row.agent_id
  form.latitude = row.latitude
  form.longitude = row.longitude
  dialogVisible.value = true
}

// 打开地图选点
const openMapPicker = async () => {
  mapDialogVisible.value = true
  await nextTick()

  // 加载高德地图
  window._AMapSecurityConfig = {
    securityJsCode: 'a4ffb9efc6af3053bd6ca94633d2fa40',
  }

  const AMap = await AMapLoader.load({
    key: 'aa44b61446e611d6aa60fdd137973e31',
    version: '2.0',
    plugins: ['AMap.Map', 'AMap.Marker'],
  })

  // 初始化地图
  map.value = new AMap.Map('map-container', {
    zoom: 11,
    center: form.latitude && form.longitude ? [form.longitude, form.latitude] : [114.026, 30.593], // 默认武汉
  })

  // 创建标记
  if (form.latitude && form.longitude) {
    marker.value = new AMap.Marker({
      position: [form.longitude, form.latitude],
      map: map.value,
      draggable: true,
    })
  } else {
    marker.value = new AMap.Marker({
      position: [114.026, 30.593],
      map: map.value,
      draggable: true,
    })
  }

  // 点击地图更新标记位置
  map.value.on('click', (e: any) => {
    const lnglat = e.lnglat
    marker.value.setPosition(lnglat)
    form.longitude = lnglat.lng
    form.latitude = lnglat.lat
  })
}

// 确认地图选择
const confirmMapSelection = () => {
  if (marker.value) {
    const position = marker.value.getPosition()
    form.longitude = position.lng
    form.latitude = position.lat
  }
  mapDialogVisible.value = false
}

const handleDelete = async (row: Shop) => {
  try {
    await ElMessageBox.confirm(`确定要删除店铺 ID:${row.id}吗？`, '确认删除', { type: 'warning' })
    await apiClient.delete(`/shops/${row.id}`)
    ElMessage.success('删除成功')
    fetchShops()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleSubmit = async () => {
  await formRef.value?.validate()
  submitting.value = true

  try {
    if (form.id) {
      const updateData: Record<string, any> = {
        name: form.name || undefined,
        user_id: form.user_id || undefined,
        region_id: form.region_id || undefined,
        agent_id: form.agent_id || undefined,
        status: 'active',
        latitude: form.latitude || undefined,
        longitude: form.longitude || undefined,
      }
      await apiClient.put(`/shops/${form.id}`, updateData)
      ElMessage.success('更新成功')
    } else {
      await apiClient.post('/shops', {
        user_id: form.user_id,
        region_id: form.region_id,
        name: form.name || undefined,
        agent_id: form.agent_id || undefined,
        latitude: form.latitude || undefined,
        longitude: form.longitude || undefined,
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchShops()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchRegions()
  fetchUsers()
  fetchAgentsList()
  fetchShops()
})
</script>

<style scoped>
.page-container {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  color: #303133;
  margin: 0;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
