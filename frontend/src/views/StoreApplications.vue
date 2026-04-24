<template>
  <div class="page-container">
    <div class="page-header">
      <h2>店铺/区代申请审核</h2>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="申请类型">
          <el-select v-model="filterForm.apply_type" placeholder="全部类型" clearable>
            <el-option label="全部类型" value="" />
            <el-option label="店铺申请" value="SHOP" />
            <el-option label="区代申请" value="AGENT" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="全部状态" value="" />
            <el-option label="待审核" value="PENDING" />
            <el-option label="已通过" value="APPROVED" />
            <el-option label="已拒绝" value="REJECTED" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchApplications">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 申请列表 -->
    <el-card class="table-card">
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="申请人" width="120" />
        <el-table-column prop="apply_type" label="申请类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.apply_type === 'SHOP' ? 'success' : 'warning'">
              {{ row.apply_type === 'SHOP' ? '店铺' : '区代' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="shop_name" label="店铺名称" width="150" v-if="filterForm.apply_type !== 'AGENT'">
          <template #default="{ row }">
            {{ row.shop_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="agent_name" label="区代名称" width="150" v-if="filterForm.apply_type !== 'SHOP'">
          <template #default="{ row }">
            {{ row.agent_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reject_reason" label="拒绝原因" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.reject_reason || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">详情</el-button>
            <el-button
              v-if="row.status === 'PENDING'"
              link
              type="success"
              @click="handleApprove(row)"
            >
              通过
            </el-button>
            <el-button
              v-if="row.status === 'PENDING'"
              link
              type="danger"
              @click="handleReject(row)"
            >
              拒绝
            </el-button>
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
          @change="fetchApplications"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="申请详情" width="600px">
      <el-descriptions :column="2" border v-if="currentApplication">
        <el-descriptions-item label="申请人">{{ currentApplication.username }}</el-descriptions-item>
        <el-descriptions-item label="申请类型">
          {{ currentApplication.apply_type === 'SHOP' ? '店铺申请' : '区代申请' }}
        </el-descriptions-item>

        <template v-if="currentApplication.apply_type === 'SHOP'">
          <el-descriptions-item label="店铺名称">{{ currentApplication.shop_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="店铺坐标">
            {{ currentApplication.shop_latitude }}, {{ currentApplication.shop_longitude }}
          </el-descriptions-item>
        </template>

        <template v-else>
          <el-descriptions-item label="区代名称">{{ currentApplication.agent_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="推荐区代">
            {{ currentApplication.referrer_name || '无' }}
          </el-descriptions-item>
        </template>

        <el-descriptions-item label="申请区域" :span="2">
          {{ currentApplication.region_name || '-' }}
        </el-descriptions-item>

        <el-descriptions-item label="状态" :span="2">
          <el-tag :type="getStatusType(currentApplication.status)">
            {{ getStatusText(currentApplication.status) }}
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="拒绝原因" :span="2" v-if="currentApplication.reject_reason">
          {{ currentApplication.reject_reason }}
        </el-descriptions-item>

        <el-descriptions-item label="申请时间" :span="2">
          {{ formatDate(currentApplication.created_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 拒绝原因对话框 -->
    <el-dialog v-model="rejectVisible" title="拒绝申请" width="400px">
      <el-form :model="rejectForm" label-width="80px">
        <el-form-item label="拒绝原因" required>
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject" :loading="rejecting">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import apiClient from '@/api'

const loading = ref(false)
const rejecting = ref(false)
const detailVisible = ref(false)
const rejectVisible = ref(false)

const filterForm = reactive({
  apply_type: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

const tableData = ref<any[]>([])
const currentApplication = ref<any>(null)
const rejectForm = reactive({
  application_id: 0,
  reason: '',
})

const fetchApplications = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.page_size,
    }
    if (filterForm.apply_type) params.apply_type = filterForm.apply_type
    if (filterForm.status) params.status = filterForm.status

    const res = await apiClient.get('/store-applications', { params })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载申请列表失败')
  } finally {
    loading.value = false
  }
}

const handleView = (row: any) => {
  currentApplication.value = row
  detailVisible.value = true
}

const handleApprove = async (row: any) => {
  try {
    await ElMessageBox.confirm('确认通过该申请吗？通过后用户将自动升级角色。', '审核通过', {
      type: 'success',
    })

    await apiClient.post(`/store-applications/${row.id}/approve`)
    ElMessage.success('审核通过')
    fetchApplications()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '审核失败')
    }
  }
}

const handleReject = (row: any) => {
  rejectForm.application_id = row.id
  rejectForm.reason = ''
  rejectVisible.value = true
}

const confirmReject = async () => {
  if (!rejectForm.reason.trim()) {
    ElMessage.warning('请输入拒绝原因')
    return
  }

  rejecting.value = true
  try {
    await apiClient.post(`/store-applications/${rejectForm.application_id}/reject`, null, {
      params: { reject_reason: rejectForm.reason },
    })
    ElMessage.success('已拒绝申请')
    rejectVisible.value = false
    fetchApplications()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '拒绝失败')
  } finally {
    rejecting.value = false
  }
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    PENDING: 'warning',
    APPROVED: 'success',
    REJECTED: 'danger',
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    PENDING: '待审核',
    APPROVED: '已通过',
    REJECTED: '已拒绝',
  }
  return texts[status] || status
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchApplications()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  min-height: 400px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
