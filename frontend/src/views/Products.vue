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
        <el-table-column label="产品图片" width="100">
          <template #default="{ row }">
            <el-image
              v-if="row.image_url || row.image"
              :src="row.image_url || row.image"
              :preview-src-list="[row.image_url || row.image]"
              fit="cover"
              style="width: 60px; height: 60px;"
            >
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <div v-else class="no-image">无图</div>
          </template>
        </el-table-column>
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
    <el-dialog v-model="productDialogVisible" :title="productDialogTitle" width="600px">
      <el-form :model="productForm" :rules="productRules" ref="productFormRef" label-width="100px">
        <el-form-item label="产品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="SKU 编码" prop="sku_code">
          <el-input v-model="productForm.sku_code" placeholder="请输入 SKU 编码" />
        </el-form-item>
        <el-form-item label="产品图片" prop="image_url">
          <el-upload
            v-model:file-list="imageFileList"
            :on-change="handleImageChange"
            :limit="1"
            list-type="picture-card"
            :on-remove="handleImageRemove"
            :before-upload="handleBeforeImageUpload"
            :auto-upload="false"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="form-tip">支持单张主图，点击可预览</div>
        </el-form-item>
        <el-form-item label="多图展示" prop="images">
          <el-upload
            v-model:file-list="multiImageFileList"
            :on-change="handleMultiImageChange"
            :limit="9"
            list-type="picture-card"
            :on-remove="handleMultiImageRemove"
            :before-upload="handleBeforeImageUpload"
            :auto-upload="false"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="form-tip">最多 9 张，用于 H5 端轮播展示</div>
        </el-form-item>
        <el-form-item label="产品详情" prop="detail">
          <el-input
            v-model="productForm.detail"
            type="textarea"
            :rows="6"
            placeholder="产品详情描述（支持 HTML 格式）"
          />
          <div class="form-tip">支持简单 HTML 标签，如 &lt;p&gt;、&lt;ul&gt;、&lt;li&gt; 等</div>
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
        <el-divider />
        <el-form-item label="分润配置">
          <div class="profit-rate-section">
            <el-form-item label="服务费比例" label-width="100px">
              <el-input-number
                v-model="priceForm.service_fee_rate"
                :min="0"
                :max="100"
                :precision="2"
                :step="0.1"
                :controls="true"
                style="width: 150px"
              />
              <span class="unit">%</span>
            </el-form-item>
            <el-form-item label="区代利润比例" label-width="100px">
              <el-input-number
                v-model="priceForm.agent_profit_rate"
                :min="0"
                :max="100"
                :precision="2"
                :step="0.1"
                :controls="true"
                style="width: 150px"
              />
              <span class="unit">%</span>
            </el-form-item>
            <div class="form-tip">留空表示使用全局默认值（服务费 30%、区代利润 10%）</div>
          </div>
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
import { Picture } from '@element-plus/icons-vue'
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
  image_url?: string | null
  image?: string | null
  images?: string[]
  prices?: Price[]
  service_fee_rate?: number | null
  agent_profit_rate?: number | null
}

const loading = ref(false)
const tableData = ref<Product[]>([])
const productDialogVisible = ref(false)
const productDialogTitle = ref('新增产品')
const priceDialogVisible = ref(false)
const submitting = ref(false)
const productFormRef = ref()
const priceFormRef = ref()

// 图片上传相关
const imageFileList = ref<any[]>([])
const multiImageFileList = ref<any[]>([])

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
})

const productForm = reactive({
  id: null as number | null,
  name: '',
  sku_code: '',
  image_url: '' as string | null,
  images: [] as string[],
  detail: '' as string | null,
})

const priceForm = reactive({
  product_id: null as number | null,
  retail: 0,
  shop: 0,
  agent: 0,
  service_fee_rate: null as number | null,
  agent_profit_rate: null as number | null,
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
  productForm.image_url = null
  productForm.images = []
  productForm.detail = ''
  imageFileList.value = []
  multiImageFileList.value = []
  productDialogVisible.value = true
}

const handleEdit = (row: Product) => {
  productDialogTitle.value = '编辑产品'
  productForm.id = row.id
  productForm.name = row.name
  productForm.sku_code = row.sku_code
  productForm.image_url = row.image_url || null
  productForm.images = row.images || []
  productForm.detail = row.detail || ''

  // 设置图片列表
  if (row.image_url) {
    imageFileList.value = [{
      url: row.image_url,
      name: '主图'
    }]
  } else {
    imageFileList.value = []
  }

  if (row.images && row.images.length > 0) {
    multiImageFileList.value = row.images.map((url, index) => ({
      url,
      name: `图片${index + 1}`
    }))
  } else {
    multiImageFileList.value = []
  }

  productDialogVisible.value = true
}

const handleSetPrice = (row: Product) => {
  priceForm.product_id = row.id
  if (row.prices) {
    priceForm.retail = getPrice(row.prices, 'retail') || 0
    priceForm.shop = getPrice(row.prices, 'shop') || 0
    priceForm.agent = getPrice(row.prices, 'agent') || 0
  }
  // 加载分润比例配置
  priceForm.service_fee_rate = row.service_fee_rate ? parseFloat((row.service_fee_rate * 100).toFixed(2)) : null
  priceForm.agent_profit_rate = row.agent_profit_rate ? parseFloat((row.agent_profit_rate * 100).toFixed(2)) : null
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
    const submitData: any = {
      name: productForm.name,
      sku_code: productForm.sku_code,
      image_url: productForm.image_url,
      images: productForm.images,  // 空数组也要发送，以便后端清空多图
      detail: productForm.detail,
    }

    if (productForm.id) {
      await apiClient.put(`/products/${productForm.id}`, submitData)
      ElMessage.success('更新成功')
    } else {
      submitData.prices = [
        { tier_type: 'retail', price: 0 },
        { tier_type: 'shop', price: 0 },
        { tier_type: 'agent', price: 0 },
      ]
      await apiClient.post('/products', submitData)
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

// 图片上传处理函数
interface UploadFile {
  raw?: File
  url?: string
  name?: string
}

const handleBeforeImageUpload = (file: File) => {
  const isValidType = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isValidType) {
    ElMessage.error('只能上传 JPG/PNG/GIF/WebP 格式的图片!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

const handleImageChange = async (file: UploadFile) => {
  if (file.raw) {
    try {
      // 调用上传 API
      const formData = new FormData()
      formData.append('file', file.raw)
      const response = await apiClient.post('/products/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      productForm.image_url = response.data.url
      // 更新当前 file 对象的 url，让 el-upload 组件显示预览
      file.url = response.data.url
      file.name = response.data.filename
      // 更新文件列表
      imageFileList.value = [{
        url: response.data.url,
        name: response.data.filename
      }]
    } catch (error: any) {
      ElMessage.error('图片上传失败')
      throw error
    }
  } else if (file.url && !file.url.startsWith('blob:')) {
    productForm.image_url = file.url
  }
}

const handleImageRemove = () => {
  productForm.image_url = null
}

const handleMultiImageChange = async (file: UploadFile & { uid?: number | string }) => {
  if (file.raw) {
    try {
      const formData = new FormData()
      formData.append('file', file.raw)
      const response = await apiClient.post('/products/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      const uploadedUrl = response.data.url as string
      const uploadedName = response.data.filename as string

      // 用 uid 精确替换当前文件，避免重复和不同步
      multiImageFileList.value = multiImageFileList.value.map((f: any) => {
        if (f.uid === file.uid) {
          return {
            ...f,
            url: uploadedUrl,
            name: uploadedName,
          }
        }
        return f
      })

      // 双保险：如果未找到对应 uid，补入一条
      if (!multiImageFileList.value.some((f: any) => f.url === uploadedUrl)) {
        multiImageFileList.value.push({
          uid: file.uid,
          url: uploadedUrl,
          name: uploadedName,
        })
      }

      // 同步表单值（过滤 blob 并去重）
      productForm.images = Array.from(
        new Set(
          multiImageFileList.value
            .map((f: any) => f.url)
            .filter((url): url is string => !!url && !url.startsWith('blob:'))
        )
      )
    } catch (error: any) {
      ElMessage.error('图片上传失败')
      throw error
    }
  } else {
    // 回显或移除后，统一从 fileList 同步一次
    productForm.images = Array.from(
      new Set(
        multiImageFileList.value
          .map((f: any) => f.url)
          .filter((url): url is string => !!url && !url.startsWith('blob:'))
      )
    )
  }
}

const handleMultiImageRemove = (file: UploadFile) => {
  const url = file.url
  if (url) {
    // 从表单数据中移除（创建新数组以触发响应式更新）
    productForm.images = [...productForm.images.filter(img => img !== url)]
    // 从文件列表中移除，保持 UI 同步
    multiImageFileList.value = [...multiImageFileList.value.filter(f => f.url !== url)]
  }
}

const handlePriceSubmit = async () => {
  submitting.value = true

  try {
    // 将百分比转换为小数（0.30 = 30%）
    const serviceFeeRate = priceForm.service_fee_rate !== null && priceForm.service_fee_rate !== undefined
      ? parseFloat((priceForm.service_fee_rate / 100).toFixed(4))
      : null
    const agentProfitRate = priceForm.agent_profit_rate !== null && priceForm.agent_profit_rate !== undefined
      ? parseFloat((priceForm.agent_profit_rate / 100).toFixed(4))
      : null

    await apiClient.post(`/products/${priceForm.product_id}/prices`, {
      prices: [
        { tier_type: 'retail', price: priceForm.retail },
        { tier_type: 'shop', price: priceForm.shop },
        { tier_type: 'agent', price: priceForm.agent },
      ],
      service_fee_rate: serviceFeeRate,
      agent_profit_rate: agentProfitRate,
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

.no-image {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 12px;
  border-radius: 4px;
}

.image-error {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  color: #909399;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.profit-rate-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.profit-rate-section .unit {
  margin-left: 8px;
  color: #909399;
}

.profit-rate-section .form-tip {
  margin-top: 8px;
  color: #909399;
}

:deep(.el-upload-list--picture-card) {
  margin-top: 8px;
}
</style>
