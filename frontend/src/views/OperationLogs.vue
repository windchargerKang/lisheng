<template>
  <div class="logs-container">
    <el-card>
      <div class="toolbar">
        <el-button @click="handleExport" :loading="exporting">
          <el-icon><Download /></el-icon>
          导出日志
        </el-button>
        <el-input
          v-model="filters.username"
          placeholder="用户名"
          clearable
          @change="fetchLogs"
          style="width: 150px; margin-left: 10px"
        />
        <el-select
          v-model="filters.action"
          placeholder="操作类型"
          clearable
          @change="fetchLogs"
          style="width: 120px; margin-left: 10px"
        >
          <el-option label="登录" value="LOGIN" />
          <el-option label="创建" value="CREATE" />
          <el-option label="删除" value="DELETE" />
          <el-option label="更新" value="UPDATE" />
        </el-select>
        <el-select
          v-model="filters.resource_type"
          placeholder="资源类型"
          clearable
          @change="fetchLogs"
          style="width: 120px; margin-left: 10px"
        >
          <el-option label="用户" value="USER" />
          <el-option label="角色" value="ROLE" />
          <el-option label="订单" value="ORDER" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleDateChange"
          style="width: 240px; margin-left: 10px"
        />
      </div>

      <el-table :data="logs" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="action" label="操作" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)">
              {{ getActionName(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_type" label="资源类型" width="100" />
        <el-table-column prop="resource_id" label="资源 ID" width="80" />
        <el-table-column prop="ip_address" label="IP 地址" width="140" />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ row.created_at ? new Date(row.created_at).toLocaleString() : '' }}
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="page_size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchLogs"
        @size-change="fetchLogs"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { getOperationLogs, exportOperationLogs } from '@/api/logs'

const loading = ref(false)
const exporting = ref(false)

const logs = ref<any[]>([])
const page = ref(1)
const page_size = ref(10)
const total = ref(0)

const filters = reactive({
  username: undefined as string | undefined,
  action: undefined as string | undefined,
  resource_type: undefined as string | undefined,
  start_date: undefined as string | undefined,
  end_date: undefined as string | undefined,
})

const dateRange = ref<[Date, Date] | null>(null)

const getActionName = (action: string) => {
  const actionMap: Record<string, string> = {
    LOGIN: '登录',
    CREATE: '创建',
    DELETE: '删除',
    UPDATE: '更新',
  }
  return actionMap[action] || action
}

const getActionType = (action: string) => {
  const typeMap: Record<string, any> = {
    LOGIN: 'info',
    CREATE: 'success',
    DELETE: 'danger',
    UPDATE: 'warning',
  }
  return typeMap[action] || 'info'
}

const handleDateChange = (dates: [Date, Date] | null) => {
  if (dates) {
    filters.start_date = dates[0].toISOString().split('T')[0]
    filters.end_date = dates[1].toISOString().split('T')[0]
  } else {
    filters.start_date = undefined
    filters.end_date = undefined
  }
  fetchLogs()
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await getOperationLogs({
      page: page.value,
      page_size: page_size.value,
      ...filters,
    })
    logs.value = res.items
    total.value = res.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载日志失败')
  } finally {
    loading.value = false
  }
}

const handleExport = async () => {
  exporting.value = true
  try {
    const blob = await exportOperationLogs(filters)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `operation_logs_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导出失败')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.logs-container {
  max-width: 1200px;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
