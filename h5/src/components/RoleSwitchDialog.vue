<template>
  <van-dialog
    v-model:show="visible"
    title="选择角色"
    :show-confirm-button="false"
    :close-on-click-overlay="true"
  >
    <div class="role-options">
      <div
        v-for="role in roles"
        :key="role.id"
        class="role-item"
        :class="{ active: currentRoleId === role.id }"
        @click="handleSelectRole(role.id)"
      >
        <div class="role-info">
          <div class="role-name">{{ role.role_name }}</div>
          <div class="role-type">{{ getRoleTypeText(role.role_type) }}</div>
        </div>
        <van-icon
          :name="currentRoleId === role.id ? 'checked' : 'circle'"
          :color="currentRoleId === role.id ? '#1989fa' : '#dcdee0'"
          size="20"
        />
      </div>
    </div>
  </van-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { showDialog, showToast } from 'vant'
import type { UserRole } from '@/stores'

const props = defineProps<{
  roles: UserRole[]
  currentRoleId: number | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'switch', roleId: number): void
}>()

const visible = ref(false)

watch(
  () => props.currentRoleId,
  (val) => {
    if (val !== null && visible.value === false) {
      visible.value = true
    }
  }
)

const handleSelectRole = (roleId: number) => {
  if (roleId === props.currentRoleId) {
    visible.value = false
    return
  }

  showDialog({
    title: '确认切换',
    message: `确定要切换到"${getRoleName(roleId)}"角色吗？`,
  })
    .then(() => {
      emit('switch', roleId)
      visible.value = false
      showToast('角色已切换')
    })
    .catch(() => {
      // 用户取消
    })
}

const getRoleName = (roleId: number): string => {
  const role = props.roles.find(r => r.id === roleId)
  return role?.role_name || ''
}

const getRoleTypeText = (roleType: string): string => {
  const textMap: Record<string, string> = {
    customer: '客户',
    shop: '店铺',
    agent: '区代',
    admin: '管理员',
  }
  return textMap[roleType] || roleType
}
</script>

<style scoped>
.role-options {
  padding: 16px;
}

.role-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-radius: 8px;
  background-color: #f7f8fa;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.role-item.active {
  background-color: #e8f3ff;
  border: 1px solid #1989fa;
}

.role-info {
  flex: 1;
}

.role-name {
  font-size: 16px;
  font-weight: 500;
  color: #323233;
  margin-bottom: 4px;
}

.role-type {
  font-size: 13px;
  color: #969799;
}
</style>
