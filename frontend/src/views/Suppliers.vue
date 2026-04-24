<template>
  <div class="page-container">
    <div class="page-header">
      <h2>供应商管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增供应商
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable>
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchSuppliers">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表 -->
    <el-card>
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="供应商名称" />
        <el-table-column prop="credit_code" label="统一社会信用代码" width="180" />
        <el-table-column prop="contact_name" label="联系人" width="100" />
        <el-table-column prop="contact_phone" label="联系电话" width="120" />
        <el-table-column prop="settlement_type" label="结算方式" width="100">
          <template #default="{ row }">
            {{ row.settlement_type === 'cash' ? '现款' : '账期' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchSuppliers"
        @size-change="fetchSuppliers"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="供应商名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="统一社会信用代码" prop="credit_code">
          <el-input v-model="form.credit_code" placeholder="请输入统一社会信用代码" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact_name">
          <el-input v-model="form.contact_name" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="开户行" prop="bank_name">
          <el-input v-model="form.bank_name" placeholder="请输入开户行" />
        </el-form-item>
        <el-form-item label="银行账号" prop="bank_account">
          <el-input v-model="form.bank_account" placeholder="请输入银行账号" />
        </el-form-item>
        <el-form-item label="结算方式" prop="settlement_type">
          <el-select v-model="form.settlement_type">
            <el-option label="现款" value="cash" />
            <el-option label="账期" value="credit" />
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
import apiClient from '@/api'

interface Supplier {
  id: number
  name: string
  credit_code: string | null
  contact_name: string | null
  contact_phone: string | null
  settlement_type: string
  status: string
  created_at: string
}

const tableData = ref<Supplier[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增供应商')
const submitting = ref(false)
const formRef = ref()

const filterForm = reactive({
  status: '',
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

const form = reactive({
  id: null as number | null,
  name: '',
  credit_code: '',
  contact_name: '',
  contact_phone: '',
  address: '',
  bank_name: '',
  bank_account: '',
  settlement_type: 'cash',
})

const rules = {
  name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
}

const fetchSuppliers = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/suppliers', {
      params: {
        page: pagination.page,
        page_size: pagination.page_size,
        status: filterForm.status || undefined,
      },
    })
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error('加载供应商数据失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增供应商'
  form.id = null
  form.name = ''
  form.credit_code = ''
  form.contact_name = ''
  form.contact_phone = ''
  form.address = ''
  form.bank_name = ''
  form.bank_account = ''
  form.settlement_type = 'cash'
  dialogVisible.value = true
}

const handleEdit = (row: Supplier) => {
  dialogTitle.value = '编辑供应商'
  form.id = row.id
  form.name = row.name
  form.credit_code = row.credit_code || ''
  form.contact_name = row.contact_name || ''
  form.contact_phone = row.contact_phone || ''
  form.settlement_type = row.settlement_type
  dialogVisible.value = true
}

const handleDelete = async (row: Supplier) => {
  try {
    await ElMessageBox.confirm(`确定要删除供应商"${row.name}"吗？`, '确认删除', {
      type: 'warning',
    })
    await apiClient.delete(`/suppliers/${row.id}`)
    ElMessage.success('删除成功')
    fetchSuppliers()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleSubmit = async () => {
  await formRef.value?.validate()
  submitting.value = true

  try {
    if (form.id) {
      await apiClient.put(`/suppliers/${form.id}`, {
        name: form.name,
        credit_code: form.credit_code || undefined,
        contact_name: form.contact_name || undefined,
        contact_phone: form.contact_phone || undefined,
        address: form.address || undefined,
        bank_name: form.bank_name || undefined,
        bank_account: form.bank_account || undefined,
        settlement_type: form.settlement_type,
      })
      ElMessage.success('更新成功')
    } else {
      await apiClient.post('/suppliers', {
        name: form.name,
        credit_code: form.credit_code || undefined,
        contact_name: form.contact_name || undefined,
        contact_phone: form.contact_phone || undefined,
        address: form.address || undefined,
        bank_name: form.bank_name || undefined,
        bank_account: form.bank_account || undefined,
        settlement_type: form.settlement_type,
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchSuppliers()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchSuppliers()
})
</script>

<style scoped>
.page-container {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  color: #303133;
  margin: 0;
}

.filter-card {
  margin-bottom: 20px;
}
</style>
