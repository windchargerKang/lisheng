<template>
  <div class="page-container">
    <div class="page-header">
      <h2>区代管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增区代
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
          <el-button type="primary" @click="fetchAgents">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 区代列表 -->
    <el-card class="table-card">
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user_id" label="用户 ID" width="100" />
        <el-table-column prop="region_id" label="区域 ID" width="100" />
        <el-table-column prop="referrer_id" label="推荐区代 ID" width="120" />
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
          @change="fetchAgents"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用户 ID" prop="user_id">
          <el-input-number v-model="form.user_id" :min="1" placeholder="请输入用户 ID" style="width: 100%" />
        </el-form-item>
        <el-form-item label="区域 ID" prop="region_id">
          <el-input-number v-model="form.region_id" :min="1" placeholder="请输入区域 ID" style="width: 100%" />
        </el-form-item>
        <el-form-item label="推荐区代 ID" prop="referrer_id">
          <el-input-number v-model="form.referrer_id" :min="1" placeholder="请输入推荐区代 ID（可选）" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import apiClient from '@/api'

interface Agent {
  id: number
  user_id: number
  region_id: number
  referrer_id: number | null
  status: string
}

interface Region {
  id: number
  name: string
}

const loading = ref(false)
const tableData = ref<Agent[]>([])
const regions = ref<Region[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增区代')
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
  user_id: 0,
  region_id: 0,
  referrer_id: null as number | null,
})

const rules = {
  user_id: [{ required: true, message: '请输入用户 ID', trigger: 'blur' }],
  region_id: [{ required: true, message: '请输入区域 ID', trigger: 'blur' }],
}

const fetchAgents = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: pagination.page,
      page_size: pagination.page_size,
    }
    if (filterForm.region_id) params.region_id = filterForm.region_id
    if (filterForm.status) params.status = filterForm.status

    const response = await apiClient.get('/agents', { params })
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error('加载区代数据失败')
  } finally {
    loading.value = false
  }
}

const fetchRegions = async () => {
  try {
    const response = await apiClient.get('/regions')
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

const handleAdd = () => {
  dialogTitle.value = '新增区代'
  form.id = null
  form.user_id = 0
  form.region_id = 0
  form.referrer_id = null
  dialogVisible.value = true
}

const handleEdit = (row: Agent) => {
  dialogTitle.value = '编辑区代'
  form.id = row.id
  form.user_id = row.user_id
  form.region_id = row.region_id
  form.referrer_id = row.referrer_id
  dialogVisible.value = true
}

const handleDelete = async (row: Agent) => {
  try {
    await ElMessageBox.confirm(`确定要删除区代 ID:${row.id}吗？`, '确认删除', { type: 'warning' })
    await apiClient.delete(`/agents/${row.id}`)
    ElMessage.success('删除成功')
    fetchAgents()
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
      await apiClient.put(`/agents/${form.id}`, {
        region_id: form.region_id || undefined,
        status: 'active',
      })
      ElMessage.success('更新成功')
    } else {
      await apiClient.post('/agents', {
        user_id: form.user_id,
        region_id: form.region_id,
        referrer_id: form.referrer_id || undefined,
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchAgents()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchRegions()
  fetchAgents()
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
