import apiClient from './index'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: {
    id: number
    username: string
    role_type: string
  }
}

export interface UserProfile {
  id: number
  username: string
  role_type: string
}

/**
 * 用户登录
 */
export async function login(params: LoginParams): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/login', params)
  return response.data
}

/**
 * 获取当前用户信息
 */
export async function getProfile(): Promise<UserProfile> {
  const response = await apiClient.get<UserProfile>('/auth/profile')
  return response.data
}

/**
 * 退出登录
 */
export function logout() {
  localStorage.removeItem('token')
}
