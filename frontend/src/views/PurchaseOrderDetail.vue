<template>
  <div class="page-container">
    <div class="page-header">
      <h2>{{ isCreateMode ? '创建采购订单' : '采购订单详情' }}</h2>
      <el-button @click="goBack">返回</el-button>
    </div>

    <!-- 创建模式：表单 -->
    <el-card v-if="isCreateMode">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="供应商" prop="supplier_id">
          <el-select
            v-model="form.supplier_id"
            placeholder="请选择供应商"
            style="width: 100%"
            @change="onSupplierChange"
          >
            <el-option
              v-for="s in suppliers"
              :key="s.id"
              :label="s.name"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" placeholder="请输入备注（可选）" />
        </el-form-item>

        <el-divider>订单明细</el-divider>

        <el-table :data="form.items" border style="margin-bottom: 10px">
          <el-table-column label="商品" width="300">
            <template #default="{ row, $index }">
              <el-select
                v-model="row.product_id"
                placeholder="选择商品"
                style="width: 100%"
                @change="onProductChange($index)"
              >
                <el-option
                  v-for="p in products"
                  :key="p.id"
                  :label="p.name"
                  :value="p.id"
                  :disabled="isProductSelected(p.id, $index)"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="150">
            <template #default="{ row, $index }">
              <el-input-number
                v-model="row.quantity"
                :min="1"
                :max="9999"
                @change="calculateTotal"
              />
            </template>
          </el-table-column>
          <el-table-column label="采购单价" width="150">
            <template #default="{ row, $index }">
              <el-input-number
                v-model="row.cost_price"
                :min="0"
                :precision="2"
                :step="0.01"
                @change="calculateTotal"
              />
            </template>
          </el-table-column>
          <el-table-column label="小计" width="120">
            <template #default="{ row }">
              ¥{{ (row.quantity * row.cost_price).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button
                link
                type="danger"
                @click="removeItem($index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-button type="primary" plain @click="addItem" style="margin-bottom: 20px">
          <el-icon><Plus /></el-icon>
          添加商品
        </el-button>

        <el-alert
          v-if="totalAmount > 0"
          title="订单总计"
          type="info"
          :closable="false"
          show-icon
        >
          <template #title>
            <span style="font-size: 18px; font-weight: bold">¥{{ totalAmount.toFixed(2) }}</span>
          </template>
        </el-alert>

        <el-form-item style="margin-top: 30px">
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            提交订单
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 详情模式：展示 -->
    <div v-else>
      <el-card>
        <el-descriptions title="订单信息" :column="2" border>
          <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ order.supplier_name }}</el-descriptions-item>
          <el-descriptions-item label="订单金额">¥{{ order.total_amount?.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(order.status)">
              {{ getStatusText(order.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ order.created_at }}</el-descriptions-item>
          <el-descriptions-item label="确认时间">{{ order.confirmed_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ order.remark || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card style="margin-top: 20px">
        <template #header>订单明细</template>
        <el-table :data="order.items" border>
          <el-table-column prop="product_name" label="商品名称" />
          <el-table-column prop="quantity" label="数量" width="100" />
          <el-table-column prop="cost_price" label="采购单价" width="120">
            <template #default="{ row }">¥{{ row.cost_price?.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="subtotal" label="小计" width="120">
            <template #default="{ row }">¥{{ row.subtotal?.toFixed(2) }}</template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 操作按钮 -->
      <el-card style="margin-top: 20px">
        <el-button
          v-if="order.status === 'pending'"
          type="success"
          @click="handleConfirm"
        >
          确认订单
        </el-button>
        <el-button
          v-if="['pending', 'confirmed'].includes(order.status)"
          type="danger"
          @click="handleCancel"
        >
          取消订单
        </el-button>
        <el-button
          v-if="order.status === 'confirmed' && !hasInbound"
          type="primary"
          @click="handleInbound"
        >
          采购入库
        </el-button>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import apiClient from '@/api'

interface Product {
  id: number
  name: string
  sku_code: string
}

interface Supplier {
  id: number
  name: string
}

interface OrderItem {
  product_id: number | null
  product_name?: string
  quantity: number
  cost_price: number
  subtotal?: number
}

const route = useRoute()
const router = useRouter()
const isCreateMode = computed(() => route.path.includes('/create'))
const formRef = ref()

const suppliers = ref<Supplier[]>([])
const products = ref<Product[]>([])
const loading = ref(false)
const submitting = ref(false)
const totalAmount = ref(0)
const hasInbound = ref(false)

const form = reactive({
  supplier_id: null as number | null,
  remark: '',
  items: [] as OrderItem[],
})

const order = ref<any>({
  id: 0,
  order_no: '',
  supplier_id: 0,
  supplier_name: '',
  total_amount: 0,
  status: '',
  remark: '',
  created_at: '',
  confirmed_at: '',
  items: [],
})

const rules = {
  supplier_id: [{ required: true, message: '请选择供应商', trigger: 'change' }],
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'warning',
    confirmed: 'success',
    completed: '',
    cancelled: 'danger',
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消',
  }
  return map[status] || status
}

const fetchSuppliers = async () => {
  try {
    const response = await apiClient.get('/suppliers', {
      params: { page: 1, page_size: 100, status: 'active' },
    })
    suppliers.value = response.data.items
  } catch (error: any) {
    ElMessage.error('加载供应商失败')
  }
}

const fetchProducts = async () => {
  try {
    const response = await apiClient.get('/products', {
      params: { page: 1, page_size: 100 },
    })
    products.value = response.data.items
  } catch (error: any) {
    ElMessage.error('加载商品失败')
  }
}

const fetchOrder = async () => {
  const orderId = route.params.id
  if (!orderId) return

  try {
    const response = await apiClient.get(`/purchase-orders/${orderId}`)
    order.value = response.data
    hasInbound.value = response.data.inbounds?.length > 0
  } catch (error: any) {
    ElMessage.error('加载订单详情失败')
  }
}

const onSupplierChange = () => {
  form.items = []
  addItem()
}

const onProductChange = (index: number) => {
  const item = form.items[index]
  const product = products.value.find(p => p.id === item.product_id)
  if (product) {
    item.product_name = product.name
  }
  calculateTotal()
}

const isProductSelected = (productId: number, currentIndex: number) => {
  return form.items.some((item, index) =>
    index !== currentIndex && item.product_id === productId
  )
}

const addItem = () => {
  form.items.push({
    product_id: null,
    quantity: 1,
    cost_price: 0,
  })
}

const removeItem = (index: number) => {
  form.items.splice(index, 1)
  calculateTotal()
}

const calculateTotal = () => {
  totalAmount.value = form.items.reduce(
    (sum, item) => sum + item.quantity * item.cost_price,
    0
  )
}

const handleSubmit = async () => {
  await formRef.value?.validate()

  if (form.items.length === 0 || !form.items[0].product_id) {
    ElMessage.warning('请至少添加一个商品')
    return
  }

  submitting.value = true
  try {
    const response = await apiClient.post('/purchase-orders', {
      supplier_id: form.supplier_id,
      remark: form.remark,
      items: form.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        cost_price: item.cost_price,
      })),
    })
    ElMessage.success('订单创建成功')
    router.push(`/purchase-orders/${response.data.id}`)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

const handleConfirm = async () => {
  try {
    await ElMessageBox.confirm('确定要确认此订单吗？', '确认订单', {
      type: 'warning',
    })
    await apiClient.put(`/purchase-orders/${order.value.id}/confirm`)
    ElMessage.success('订单已确认')
    fetchOrder()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '确认失败')
    }
  }
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm('确定要取消此订单吗？', '取消订单', {
      type: 'warning',
    })
    await apiClient.post(`/purchase-orders/${order.value.id}/cancel`)
    ElMessage.success('订单已取消')
    fetchOrder()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '取消失败')
    }
  }
}

const handleInbound = () => {
  router.push(`/inbounds/create?order_id=${order.value.id}`)
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchSuppliers()
  fetchProducts()
  if (!isCreateMode.value) {
    fetchOrder()
  } else {
    addItem()
  }
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
