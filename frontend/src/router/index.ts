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
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const isLogin = to.path === '/login'

  if (!token && !isLogin) {
    next('/login')
  } else if (token && isLogin) {
    next('/')
  } else {
    next()
  }
})

export default router
