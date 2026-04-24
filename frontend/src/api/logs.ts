/**
 * 操作日志 API
 */
import request from '@/utils/request'

export interface OperationLog {
  id: number
  user_id: number
  username?: string
  action: string
  resource_type: string
  resource_id?: number
  ip_address?: string
  created_at?: string
}

export interface OperationLogListResponse {
  items: OperationLog[]
  total: number
  page: number
  page_size: number
}

/**
 * 获取操作日志列表
 */
export function getOperationLogs(params?: {
  page?: number
  page_size?: number
  user_id?: number
  action?: string
  resource_type?: string
  start_date?: string
  end_date?: string
}) {
  return request<OperationLogListResponse>({
    url: '/operation-logs',
    method: 'get',
    params,
  })
}

/**
 * 导出操作日志
 */
export function exportOperationLogs(params?: {
  user_id?: number
  action?: string
  resource_type?: string
  start_date?: string
  end_date?: string
}) {
  return request<Blob>({
    url: '/operation-logs/export',
    method: 'get',
    params,
    responseType: 'blob',
  })
}
