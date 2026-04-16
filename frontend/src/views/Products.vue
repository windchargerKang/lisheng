<template>
  <div class="page-container">
    <div class="page-header">
      <h2>产品管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增产品
      </el-button>
    </div>

    <!-- 产品列表 -->
    <el-card class="table-card">
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="产品名称" />
        <el-table-column prop="sku_code" label="SKU 编码" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '上架中' : '已下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="价格" width="300">
          <template #default="{ row }">
            <div class="price-info" v-if="row.prices">
              <el-tag size="small" type="warning" v-if="getPrice(row.prices, 'retail')">
                零售：¥{{ getPrice(row.prices, 'retail') }}
              </el-tag>
              <el-tag size="small" type="success" v-if="getPrice(row.prices, 'shop')">
                店铺：¥{{ getPrice(row.prices, 'shop') }}
              </el-tag>
              <el-tag size="small" type="primary" v-if="getPrice(row.prices, 'agent')">
                区代：¥{{ getPrice(row.prices, 'agent') }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleSetPrice(row)">定价</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @change="fetchProducts"
        />
      </div>
    </el-card>

    <!-- 新增/编辑产品对话框 -->
    <el-dialog v-model="productDialogVisible" :title="productDialogTitle" width="500px">
      <el-form :model="productForm" :rules="productRules" ref="productFormRef" label-width="100px">
        <el-form-item label="产品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="SKU 编码" prop="sku_code">
          <el-input v-model="productForm.sku_code" placeholder="请输入 SKU 编码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="productDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleProductSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 定价对话框 -->
    <el-dialog v-model="priceDialogVisible" title="设置产品价格" width="500px">
      <el-form :model="priceForm" ref="priceFormRef" label-width="100px">
        <el-form-item label="零售价格">
          <el-input-number v-model="priceForm.retail" :min="0" :precision="2" :step="0.1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="店铺价格">
          <el-input-number v-model="priceForm.shop" :min="0" :precision="2" :step="0.1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="区代价格">
          <el-input-number v-model="priceForm.agent" :min="0" :precision="2" :step="0.1" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="priceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePriceSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import apiClient from '@/api'

interface Price {
  tier_type: string
  price: number
}

interface Product {
  id: number
  name: string
  sku_code: string
  status: string
  prices?: Price[]
}

const loading = ref(false)
const tableData = ref<Product[]>([])
const productDialogVisible = ref(false)
const productDialogTitle = ref('新增产品')
const priceDialogVisible = ref(false)
const submitting = ref(false)
const productFormRef = ref()
const priceFormRef = ref()

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

const productForm = reactive({
  id: null as number | null,
  name: '',
  sku_code: '',
})

const priceForm = reactive({
  product_id: null as number | null,
  retail: 0,
  shop: 0,
  agent: 0,
})

const productRules = {
  name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  sku_code: [{ required: true, message: '请输入 SKU 编码', trigger: 'blur' }],
}

const getPrice = (prices: Price[], tier_type: string): number | null => {
  const p = prices?.find((item) => item.tier_type === tier_type)
  return p ? p.price : null
}

const fetchProducts = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/products', {
      params: { page: pagination.page, page_size: pagination.page_size },
    })
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error('加载产品数据失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  productDialogTitle.value = '新增产品'
  productForm.id = null
  productForm.name = ''
  productForm.sku_code = ''
  productDialogVisible.value = true
}

const handleEdit = (row: Product) => {
  productDialogTitle.value = '编辑产品'
  productForm.id = row.id
  productForm.name = row.name
  productForm.sku_code = row.sku_code
  productDialogVisible.value = true
}

const handleSetPrice = (row: Product) => {
  priceForm.product_id = row.id
  if (row.prices) {
    priceForm.retail = getPrice(row.prices, 'retail') || 0
    priceForm.shop = getPrice(row.prices, 'shop') || 0
    priceForm.agent = getPrice(row.prices, 'agent') || 0
  }
  priceDialogVisible.value = true
}

const handleDelete = async (row: Product) => {
  try {
    await ElMessageBox.confirm(`确定要删除产品"${row.name}"吗？`, '确认删除', { type: 'warning' })
    await apiClient.delete(`/products/${row.id}`)
    ElMessage.success('删除成功')
    fetchProducts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleProductSubmit = async () => {
  await productFormRef.value?.validate()
  submitting.value = true

  try {
    if (productForm.id) {
      await apiClient.put(`/products/${productForm.id}`, {
        name: productForm.name,
        sku_code: productForm.sku_code,
      })
      ElMessage.success('更新成功')
    } else {
      await apiClient.post('/products', {
        name: productForm.name,
        sku_code: productForm.sku_code,
        prices: [
          { tier_type: 'retail', price: 0 },
          { tier_type: 'shop', price: 0 },
          { tier_type: 'agent', price: 0 },
        ],
      })
      ElMessage.success('创建成功')
    }
    productDialogVisible.value = false
    fetchProducts()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handlePriceSubmit = async () => {
  submitting.value = true

  try {
    await apiClient.post(`/products/${priceForm.product_id}/prices`, {
      prices: [
        { tier_type: 'retail', price: priceForm.retail },
        { tier_type: 'shop', price: priceForm.shop },
        { tier_type: 'agent', price: priceForm.agent },
      ],
    })
    ElMessage.success('价格设置成功')
    priceDialogVisible.value = false
    fetchProducts()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchProducts()
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

.table-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.price-info {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
