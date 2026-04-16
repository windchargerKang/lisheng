<template>
  <div class="page-container">
    <div class="page-header">
      <h2>区域管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增区域
      </el-button>
    </div>

    <el-card>
      <el-table
        :data="tableData"
        row-key="id"
        border
        default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="区域名称" />
        <el-table-column prop="level" label="层级" width="100">
          <template #default="{ row }">
            {{ levelText(row.level) }}
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路径" width="200" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="区域名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入区域名称" />
        </el-form-item>
        <el-form-item label="父级区域" prop="parent_id">
          <el-tree-select
            v-model="form.parent_id"
            :data="treeOptions"
            placeholder="选择父级区域（可选）"
            clearable
            check-strictly
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import apiClient from '@/api'

interface Region {
  id: number
  name: string
  level: number
  path: string
  parent_id: number | null
  children?: Region[]
}

const tableData = ref<Region[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增区域')
const submitting = ref(false)
const formRef = ref()

const form = reactive({
  id: null as number | null,
  name: '',
  parent_id: null as number | null,
})

const rules = {
  name: [{ required: true, message: '请输入区域名称', trigger: 'blur' }],
}

const treeOptions = ref<Region[]>([])

const levelText = (level: number) => {
  const map: Record<number, string> = { 1: '省级', 2: '市级', 3: '区级', 4: '县级', 5: '乡镇' }
  return map[level] || `L${level}`
}

const fetchRegions = async () => {
  try {
    const response = await apiClient.get('/regions')
    tableData.value = response.data.regions
    treeOptions.value = [{ id: 0, name: '顶级区域', level: 0, path: '', parent_id: null, children: response.data.regions }]
  } catch (error: any) {
    ElMessage.error('加载区域数据失败')
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增区域'
  form.id = null
  form.name = ''
  form.parent_id = null
  dialogVisible.value = true
}

const handleEdit = (row: Region) => {
  dialogTitle.value = '编辑区域'
  form.id = row.id
  form.name = row.name
  form.parent_id = row.parent_id
  dialogVisible.value = true
}

const handleDelete = async (row: Region) => {
  try {
    await ElMessageBox.confirm(`确定要删除区域"${row.name}"吗？`, '确认删除', {
      type: 'warning',
    })
    await apiClient.delete(`/regions/${row.id}`)
    ElMessage.success('删除成功')
    fetchRegions()
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
      // 编辑
      await apiClient.put(`/regions/${form.id}`, {
        name: form.name,
        level: form.parent_id ? null : 1,
      })
      ElMessage.success('更新成功')
    } else {
      // 新增
      await apiClient.post('/regions', {
        name: form.name,
        parent_id: form.parent_id || undefined,
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchRegions()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchRegions()
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
</style>
