<template>
  <div class="page-container">
    <div class="page-header">
      <h2>档案管理</h2>
      <el-button type="primary" @click="handleEdit">
        <el-icon><Edit /></el-icon>
        编辑档案
      </el-button>
    </div>

    <el-card>
      <el-descriptions title="供应商信息" :column="2" border>
        <el-descriptions-item label="供应商名称">{{ profile.name }}</el-descriptions-item>
        <el-descriptions-item label="统一社会信用代码">{{ profile.credit_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ profile.contact_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ profile.contact_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ profile.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开户行">{{ profile.bank_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="银行账号">{{ profile.bank_account || '-' }}</el-descriptions-item>
        <el-descriptions-item label="结算方式">
          {{ profile.settlement_type === 'cash' ? '现款' : '账期' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="profile.status === 'active' ? 'success' : 'danger'">
            {{ profile.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑档案"
      width="500px"
    >
      <el-form :model="form" ref="formRef" label-width="100px">
        <el-form-item label="联系人">
          <el-input v-model="form.contact_name" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="开户行">
          <el-input v-model="form.bank_name" placeholder="请输入开户行" />
        </el-form-item>
        <el-form-item label="银行账号">
          <el-input v-model="form.bank_account" placeholder="请输入银行账号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api'

const profile = ref<any>({})
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref()

const form = reactive({
  contact_name: '',
  contact_phone: '',
  address: '',
  bank_name: '',
  bank_account: '',
})

const fetchProfile = async () => {
  try {
    const response = await apiClient.get('/supplier-portal/profile')
    profile.value = response.data
  } catch (error: any) {
    ElMessage.error('加载档案失败')
  }
}

const handleEdit = () => {
  form.contact_name = profile.value.contact_name || ''
  form.contact_phone = profile.value.contact_phone || ''
  form.address = profile.value.address || ''
  form.bank_name = profile.value.bank_name || ''
  form.bank_account = profile.value.bank_account || ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    await apiClient.put('/supplier-portal/profile', {
      contact_name: form.contact_name || undefined,
      contact_phone: form.contact_phone || undefined,
      address: form.address || undefined,
      bank_name: form.bank_name || undefined,
      bank_account: form.bank_account || undefined,
    })
    ElMessage.success('档案已更新')
    dialogVisible.value = false
    fetchProfile()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchProfile()
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
</style>
