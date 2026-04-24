import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘' },
      },
      {
        path: 'regions',
        name: 'Regions',
        component: () => import('@/views/Regions.vue'),
        meta: { title: '区域管理' },
      },
      {
        path: 'shops',
        name: 'Shops',
        component: () => import('@/views/Shops.vue'),
        meta: { title: '店铺管理' },
      },
      {
        path: 'agents',
        name: 'Agents',
        component: () => import('@/views/Agents.vue'),
        meta: { title: '区代管理' },
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/Products.vue'),
        meta: { title: '产品管理' },
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('@/views/Suppliers.vue'),
        meta: { title: '供应商管理' },
      },
      {
        path: 'purchase-orders',
        name: 'PurchaseOrders',
        component: () => import('@/views/PurchaseOrders.vue'),
        meta: { title: '采购订单管理' },
      },
      {
        path: 'purchase-orders/create',
        name: 'PurchaseOrderCreate',
        component: () => import('@/views/PurchaseOrderDetail.vue'),
        meta: { title: '创建采购订单' },
      },
      {
        path: 'purchase-orders/:id',
        name: 'PurchaseOrderDetail',
        component: () => import('@/views/PurchaseOrderDetail.vue'),
        meta: { title: '采购订单详情' },
      },
      {
        path: 'inbounds',
        name: 'Inbounds',
        component: () => import('@/views/Inbounds.vue'),
        meta: { title: '入库管理' },
      },
      {
        path: 'settlements',
        name: 'Settlements',
        component: () => import('@/views/Settlements.vue'),
        meta: { title: '结算管理' },
      },
      // 权限管理路由
      {
        path: 'roles',
        name: 'Roles',
        component: () => import('@/views/Roles.vue'),
        meta: { title: '角色管理' },
      },
      {
        path: 'roles/:id',
        name: 'RoleDetail',
        component: () => import('@/views/RoleDetail.vue'),
        meta: { title: '配置权限' },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'store-applications',
        name: 'StoreApplications',
        component: () => import('@/views/StoreApplications.vue'),
        meta: { title: '店铺/区代申请' },
      },
      {
        path: 'wallet',
        name: 'Wallet',
        component: () => import('@/views/Wallet.vue'),
        meta: { title: '我的钱包' },
      },
      {
        path: 'wallet-admin',
        name: 'WalletAdmin',
        component: () => import('@/views/WalletAdmin.vue'),
        meta: { title: '钱包管理' },
      },
      {
        path: 'logs',
        name: 'OperationLogs',
        component: () => import('@/views/OperationLogs.vue'),
        meta: { title: '操作日志' },
      },
      // 订单管理路由
      {
        path: 'orders',
        name: 'Orders',
        redirect: '/orders/list',
        children: [
          {
            path: 'list',
            name: 'OrderList',
            component: () => import('@/views/orders/List.vue'),
            meta: { title: '订单管理' },
          },
          {
            path: ':id',
            name: 'OrderDetail',
            component: () => import('@/views/orders/Detail.vue'),
            meta: { title: '订单详情' },
          },
        ],
      },
      // 供应商门户路由
      {
        path: 'supplier-portal',
        name: 'SupplierPortal',
        redirect: '/supplier-portal/dashboard',
        children: [
          {
            path: 'dashboard',
            name: 'SupplierDashboard',
            component: () => import('@/views/supplier/Dashboard.vue'),
            meta: { title: '供应商门户' },
          },
          {
            path: 'orders',
            name: 'SupplierOrders',
            component: () => import('@/views/supplier/Orders.vue'),
            meta: { title: '订单管理' },
          },
          {
            path: 'orders/:id',
            name: 'SupplierOrderDetail',
            component: () => import('@/views/supplier/OrderDetail.vue'),
            meta: { title: '订单详情' },
          },
          {
            path: 'inbounds',
            name: 'SupplierInbounds',
            component: () => import('@/views/supplier/Inbounds.vue'),
            meta: { title: '入库记录' },
          },
          {
            path: 'settlements',
            name: 'SupplierSettlements',
            component: () => import('@/views/supplier/Settlements.vue'),
            meta: { title: '结算记录' },
          },
          {
            path: 'profile',
            name: 'SupplierProfile',
            component: () => import('@/views/supplier/Profile.vue'),
            meta: { title: '档案管理' },
          },
        ],
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const isLogin = to.path === '/login'

  if (!token && !isLogin) {
    next('/login')
  } else if (token && isLogin) {
    next('/admin/')
  } else {
    next()
  }
})

export default router
