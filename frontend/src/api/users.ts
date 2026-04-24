/**
 * 用户管理 API
 */
import request from '@/utils/request'

export interface User {
  id: number
  username: string
  role_id?: number
  role_name?: string
  role_code?: string
  status: 'ACTIVE' | 'DISABLED'
  last_login_at?: string
  last_login_ip?: string
  created_at?: string
}

export interface UserListResponse {
  items: User[]
  total: number
  page: number
  page_size: number
}

/**
 * 获取用户列表
 */
export function getUsers(params?: {
  page?: number
  page_size?: number
  role_id?: number
  status?: string
  username?: string
}) {
  return request<UserListResponse>({
    url: '/users',
    method: 'get',
    params,
  })
}

/**
 * 获取用户详情
 */
export function getUser(id: number) {
  return request<User>({
    url: `/users/${id}`,
    method: 'get',
  })
}

/**
 * 创建用户
 */
export function createUser(data: { username: string; password: string; role_id?: number }) {
  return request<{ id: number; message: string }>({
    url: '/users',
    method: 'post',
    data,
  })
}

/**
 * 更新用户
 */
export function updateUser(id: number, data: { role_id?: number; password?: string }) {
  return request<{ id: number; message: string }>({
    url: `/users/${id}`,
    method: 'put',
    data,
  })
}

/**
 * 删除用户
 */
export function deleteUser(id: number) {
  return request<{ message: string }>({
    url: `/users/${id}`,
    method: 'delete',
  })
}

/**
 * 禁用/启用用户
 */
export function disableUser(id: number, disable: boolean) {
  return request<{ message: string }>({
    url: `/users/${id}/disable`,
    method: 'post',
    data: { disable },
  })
}

/**
 * 重置密码
 */
export function resetPassword(id: number, password: string) {
  return request<{ message: string }>({
    url: `/users/${id}/reset-password`,
    method: 'post',
    data: { password },
  })
}
