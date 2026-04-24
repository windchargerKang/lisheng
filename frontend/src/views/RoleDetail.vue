<template>
  <div class="role-detail-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <span>配置角色权限 - {{ roleName }}</span>
        </div>
      </template>

      <div v-loading="loading">
        <el-alert
          title="权限配置说明"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          勾选需要授予该角色的权限，然后点击保存按钮。
        </el-alert>

        <div class="permission-groups" v-if="Object.keys(permissionGroups).length">
          <el-card
            v-for="(permissions, type) in permissionGroups"
            :key="type"
            class="permission-group"
          >
            <template #header>
              <span class="group-title">{{ getTypeName(type) }}</span>
            </template>
            <el-checkbox-group v-model="selectedPermissions">
              <div
                v-for="perm in permissions"
                :key="perm.id"
                class="permission-item"
              >
                <el-checkbox :label="perm.id">
                  <span class="perm-code">{{ perm.code }}</span>
                  <span class="perm-name">{{ perm.name }}</span>
                </el-checkbox>
              </div>
            </el-checkbox-group>
          </el-card>
        </div>

        <div class="actions" style="margin-top: 20px">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="saving">
            保存配置
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getRole, getRolePermissions, updateRolePermissions, getPermissions } from '@/api/roles'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const roleName = ref('')
const selectedPermissions = ref<number[]>([])
const permissionGroups = ref<Record<string, any[]>>({})
const rolePermissions = ref<number[]>([])

const roleId = computed(() => Number(route.params.id))

const getTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    MENU: '菜单权限',
    BUTTON: '按钮权限',
    DATA: '数据权限',
  }
  return typeMap[type] || type
}

const fetchRole = async () => {
  try {
    const res = await getRole(roleId.value)
    roleName.value = res.name
    rolePermissions.value = res.permissions.map(p => p.id)
    selectedPermissions.value = res.permissions.map(p => p.id)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载角色信息失败')
  }
}

const fetchPermissions = async () => {
  try {
    const res = await getPermissions()
    permissionGroups.value = res
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载权限列表失败')
  }
}

const handleSave = async () => {
  saving.value = true
  try {
    await updateRolePermissions(roleId.value, selectedPermissions.value)
    ElMessage.success('权限配置已保存')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  Promise.all([fetchRole(), fetchPermissions()])
})
</script>

<style scoped>
.role-detail-container {
  max-width: 1200px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.permission-groups {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.permission-group {
  height: fit-content;
}

.group-title {
  font-weight: bold;
}

.permission-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.permission-item:last-child {
  border-bottom: none;
}

.perm-code {
  font-family: monospace;
  font-size: 13px;
  color: #666;
  margin-right: 8px;
}

.perm-name {
  color: #333;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
