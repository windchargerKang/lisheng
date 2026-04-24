<template>
  <div class="users-container">
    <el-card>
      <div class="toolbar">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          创建用户
        </el-button>
        <el-select
          v-model="filters.role_id"
          placeholder="选择角色"
          clearable
          @change="fetchUsers"
          style="width: 150px; margin-left: 10px"
        >
          <el-option
            v-for="role in roles"
            :key="role.id"
            :label="role.name"
            :value="role.id"
          />
        </el-select>
        <el-select
          v-model="filters.status"
          placeholder="选择状态"
          clearable
          @change="fetchUsers"
          style="width: 120px; margin-left: 10px"
        >
          <el-option label="正常" value="ACTIVE" />
          <el-option label="已禁用" value="DISABLED" />
        </el-select>
        <el-input
          v-model="filters.username"
          placeholder="搜索用户名"
          clearable
          @change="fetchUsers"
          style="width: 200px; margin-left: 10px"
        />
      </div>

      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role_name" label="角色" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'danger'">
              {{ row.status === 'ACTIVE' ? '正常' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login_at" label="最后登录时间" width="180">
          <template #default="{ row }">
            {{ row.last_login_at ? new Date(row.last_login_at).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button
              link
              :type="row.status === 'ACTIVE' ? 'warning' : 'success'"
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 'ACTIVE' ? '禁用' : '启用' }}
            </el-button>
            <el-button link type="primary" @click="handleResetPassword(row)">重置密码</el-button>
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
        @current-change="fetchUsers"
        @size-change="fetchUsers"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingUser ? '编辑用户' : '创建用户'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :disabled="!!editingUser"
          />
        </el-form-item>
        <el-form-item
          label="密码"
          prop="password"
          :rules="editingUser ? [] : rules.password"
        >
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :disabled="!editingUser && false"
          />
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="form.role_id" placeholder="请选择角色" style="width: 100%">
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
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
import { getUsers, createUser, updateUser, deleteUser, disableUser, resetPassword, type User } from '@/api/users'
import { getRoles } from '@/api/roles'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingUser = ref<User | null>(null)
const formRef = ref()

const users = ref<User[]>([])
const roles = ref<any[]>([])
const page = ref(1)
const page_size = ref(10)
const total = ref(0)

const filters = reactive({
  role_id: undefined as number | undefined,
  status: undefined as string | undefined,
  username: undefined as string | undefined,
})

const form = reactive({
  username: '',
  password: '',
  role_id: undefined as number | undefined,
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await getUsers({
      page: page.value,
      page_size: page_size.value,
      ...filters,
    })
    users.value = res.items
    total.value = res.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const fetchRoles = async () => {
  try {
    const res = await getRoles({ page: 1, page_size: 100 })
    roles.value = res.items
  } catch (error: any) {
    console.error('加载角色列表失败', error)
  }
}

const handleCreate = () => {
  editingUser.value = null
  form.username = ''
  form.password = ''
  form.role_id = undefined
  dialogVisible.value = true
}

const handleEdit = (user: User) => {
  editingUser.value = user
  form.username = user.username
  form.password = ''
  form.role_id = user.role_id
  dialogVisible.value = true
}

const handleToggleStatus = (user: User) => {
  const newStatus = user.status === 'ACTIVE' ? 'DISABLED' : 'ACTIVE'
  const actionText = newStatus === 'DISABLED' ? '禁用' : '启用'

  ElMessageBox.confirm(`确定要${actionText}该用户吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await disableUser(user.id, user.status === 'ACTIVE')
      ElMessage.success(`${actionText}成功`)
      fetchUsers()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || `${actionText}失败`)
    }
  })
}

const handleResetPassword = (user: User) => {
  ElMessageBox.prompt('请输入新密码', '重置密码', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /.{6,}/,
    inputErrorMessage: '密码至少 6 位',
  }).then(async ({ value }) => {
    try {
      await resetPassword(user.id, value)
      ElMessage.success('密码重置成功')
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '密码重置失败')
    }
  })
}

const handleDelete = (user: User) => {
  ElMessageBox.confirm('确定要删除该用户吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteUser(user.id)
      ElMessage.success('删除成功')
      fetchUsers()
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
      if (editingUser.value) {
        const data: any = { role_id: form.role_id }
        if (form.password) {
          data.password = form.password
        }
        await updateUser(editingUser.value.id, data)
        ElMessage.success('更新成功')
      } else {
        await createUser({
          username: form.username,
          password: form.password,
          role_id: form.role_id,
        })
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchUsers()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  Promise.all([fetchUsers(), fetchRoles()])
})
</script>

<style scoped>
.users-container {
  max-width: 1200px;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
