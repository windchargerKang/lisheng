import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api'

export interface UserRole {
  id: number
  role_code: string  // 后端返回 role_code 字段
  role_name: string
  is_active: boolean
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<any>(null)
  const userRoles = ref<UserRole[]>([])
  const currentRoleId = ref<number | null>(null)

  const roleType = computed(() => {
    if (currentRoleId.value) {
      const currentRole = userRoles.value.find(r => r.id === currentRoleId.value)
      return currentRole?.role_code || userInfo.value?.role_code || ''
    }
    return userInfo.value?.role_code || ''
  })

  const currentRole = computed(() => {
    if (currentRoleId.value) {
      return userRoles.value.find(r => r.id === currentRoleId.value)
    }
    if (userInfo.value?.role_code) {
      return {
        id: 0,
        role_code: userInfo.value.role_code,
        role_name: getRoleText(userInfo.value.role_code),
        is_active: true,
      }
    }
    return null
  })

  const isLoggedIn = computed(() => !!token.value)

  function getRoleText(roleType: string): string {
    const textMap: Record<string, string> = {
      customer: '客户',
      shop: '店铺',
      agent: '区代',
      admin: '管理员',
    }
    return textMap[roleType] || '未知'
  }

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setUserInfo(info: any) {
    userInfo.value = info
  }

  function setUserRoles(roles: UserRole[], roleId?: number) {
    userRoles.value = roles
    currentRoleId.value = roleId || roles[0]?.id || null
    localStorage.setItem('currentRoleId', String(currentRoleId.value))
  }

  function switchRole(roleId: number) {
    currentRoleId.value = roleId
    localStorage.setItem('currentRoleId', String(roleId))
  }

  function logout() {
    token.value = null
    userInfo.value = null
    userRoles.value = []
    currentRoleId.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('currentRoleId')
  }

  // 获取用户角色列表
  async function fetchUserRoles() {
    try {
      const response = await apiClient.get('/auth/roles')
      const { roles, current_role_id } = response.data
      setUserRoles(roles, current_role_id || undefined)
      // 同时更新 userInfo 中的 role_code
      if (roles.length > 0) {
        const currentRole = roles.find(r => r.id === (current_role_id || roles[0].id))
        if (currentRole && userInfo.value) {
          userInfo.value.role_code = currentRole.role_code
        }
      }
      return roles
    } catch (error) {
      console.error('获取角色列表失败:', error)
      return []
    }
  }

  // 切换角色
  async function switchRoleApi(roleId: number) {
    try {
      await apiClient.post(`/auth/roles/switch?role_id=${roleId}`)
      switchRole(roleId)
      return true
    } catch (error) {
      console.error('切换角色失败:', error)
      throw error
    }
  }

  return {
    token,
    userInfo,
    userRoles,
    currentRoleId,
    roleType,
    currentRole,
    isLoggedIn,
    setToken,
    setUserInfo,
    setUserRoles,
    switchRole,
    switchRoleApi,
    fetchUserRoles,
    logout,
  }
})
