<template>
  <div class="roles-container">
    <el-card>
      <div class="toolbar">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          创建角色
        </el-button>
      </div>

      <el-table :data="roles" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" />
        <el-table-column prop="code" label="角色代码" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ row.created_at ? new Date(row.created_at).toLocaleString() : '' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handlePermissions(row)">权限</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="page_size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchRoles"
        @size-change="fetchRoles"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建/编辑角色对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingRole ? '编辑角色' : '创建角色'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色代码" prop="code">
          <el-input
            v-model="form.code"
            placeholder="请输入角色代码"
            :disabled="!!editingRole"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
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
import { Plus } from '@element-plus/icons-vue'
import { getRoles, createRole, updateRole, deleteRole, type Role } from '@/api/roles'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingRole = ref<Role | null>(null)
const formRef = ref()

const roles = ref<Role[]>([])
const page = ref(1)
const page_size = ref(10)
const total = ref(0)

const form = reactive({
  name: '',
  code: '',
  description: '',
})

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色代码', trigger: 'blur' }],
}

const fetchRoles = async () => {
  loading.value = true
  try {
    const res = await getRoles({ page: page.value, page_size: page_size.value })
    roles.value = res.items
    total.value = res.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载角色列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  editingRole.value = null
  form.name = ''
  form.code = ''
  form.description = ''
  dialogVisible.value = true
}

const handleEdit = (role: Role) => {
  editingRole.value = role
  form.name = role.name
  form.code = role.code
  form.description = role.description || ''
  dialogVisible.value = true
}

const handlePermissions = (role: Role) => {
  router.push(`/roles/${role.id}`)
}

const handleDelete = (role: Role) => {
  ElMessageBox.confirm('确定要删除该角色吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteRole(role.id)
      ElMessage.success('删除成功')
      fetchRoles()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    submitting.value = true
    try {
      if (editingRole.value) {
        await updateRole(editingRole.value.id, {
          name: form.name,
          description: form.description,
        })
        ElMessage.success('更新成功')
      } else {
        await createRole({
          name: form.name,
          code: form.code,
          description: form.description,
        })
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchRoles()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  fetchRoles()
})
</script>

<style scoped>
.roles-container {
  max-width: 1200px;
}

.toolbar {
  margin-bottom: 20px;
}
</style>
