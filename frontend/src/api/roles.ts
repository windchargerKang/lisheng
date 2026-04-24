/**
 * 角色管理 API
 */
import request from '@/utils/request'

export interface Role {
  id: number
  name: string
  code: string
  description: string
  created_at?: string
}

export interface Permission {
  id: number
  code: string
  name: string
  type: 'MENU' | 'BUTTON' | 'DATA'
  parent_id?: number
}

export interface RoleListResponse {
  items: Role[]
  total: number
  page: number
  page_size: number
}

export interface PermissionGroup {
  [key: string]: Permission[]
}

/**
 * 获取角色列表
 */
export function getRoles(params?: { page?: number; page_size?: number }) {
  return request<RoleListResponse>({
    url: '/roles',
    method: 'get',
    params,
  })
}

/**
 * 获取角色详情
 */
export function getRole(id: number) {
  return request<Role & { permissions: Permission[] }>({
    url: `/roles/${id}`,
    method: 'get',
  })
}

/**
 * 创建角色
 */
export function createRole(data: { name: string; code: string; description?: string }) {
  return request<{ id: number; message: string }>({
    url: '/roles',
    method: 'post',
    data,
  })
}

/**
 * 更新角色
 */
export function updateRole(id: number, data: { name?: string; description?: string }) {
  return request<{ id: number; message: string }>({
    url: `/roles/${id}`,
    method: 'put',
    data,
  })
}

/**
 * 删除角色
 */
export function deleteRole(id: number) {
  return request<{ message: string }>({
    url: `/roles/${id}`,
    method: 'delete',
  })
}

/**
 * 获取角色权限
 */
export function getRolePermissions(id: number) {
  return request<{ role_id: number; permissions: Permission[] }>({
    url: `/roles/${id}/permissions`,
    method: 'get',
  })
}

/**
 * 配置角色权限
 */
export function updateRolePermissions(id: number, permissionIds: number[]) {
  return request<{ message: string }>({
    url: `/roles/${id}/permissions`,
    method: 'put',
    data: permissionIds,
  })
}

/**
 * 获取所有权限列表
 */
export function getPermissions() {
  return request<PermissionGroup>({
    url: '/permissions',
    method: 'get',
  })
}

/**
 * 获取当前用户权限
 */
export function getMyPermissions() {
  return request<{ permissions: Permission[] }>({
    url: '/permissions/my',
    method: 'get',
  })
}
