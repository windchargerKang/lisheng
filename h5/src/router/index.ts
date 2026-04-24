import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('@/views/Checkout.vue'),
    meta: { requiresAuth: true, title: '确认订单' },
  },
  {
    path: '/payment',
    name: 'Payment',
    component: () => import('@/views/Payment.vue'),
    meta: { requiresAuth: true, title: '支付' },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/Products.vue'),
        meta: { title: '产品' },
      },
      {
        path: 'products/:id',
        name: 'ProductDetail',
        component: () => import('@/views/ProductDetail.vue'),
        meta: { title: '商品详情' },
      },
      {
        path: 'cart',
        name: 'Cart',
        component: () => import('@/views/Cart.vue'),
        meta: { title: '购物车' },
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/Orders.vue'),
        meta: { title: '订单' },
      },
      {
        path: 'orders/:id',
        name: 'OrderDetail',
        component: () => import('@/views/OrderDetail.vue'),
        meta: { title: '订单详情' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '我的' },
      },
      {
        path: 'addresses',
        name: 'Addresses',
        component: () => import('@/views/Addresses.vue'),
        meta: { requiresAuth: true, title: '收货地址' },
      },
      {
        path: 'addresses/edit',
        name: 'AddressEdit',
        component: () => import('@/views/AddressEdit.vue'),
        meta: { requiresAuth: true, title: '编辑地址' },
      },
      {
        path: 'wallet',
        name: 'Wallet',
        component: () => import('@/views/Wallet.vue'),
        meta: { title: '我的钱包' },
      },
      {
        path: 'referral',
        name: 'Referral',
        component: () => import('@/views/Referral.vue'),
        meta: { title: '分享中心' },
      },
      {
        path: 'referral/team',
        name: 'ReferralTeam',
        component: () => import('@/views/ReferralTeam.vue'),
        meta: { title: '我的团队' },
      },
      {
        path: 'referral/records',
        name: 'ReferralRecords',
        component: () => import('@/views/ReferralRecords.vue'),
        meta: { title: '分享记录' },
      },
      {
        path: 'verification',
        name: 'Verification',
        component: () => import('@/views/Verification.vue'),
        meta: { title: '订单核销' },
      },
      {
        path: 'nearby-shops',
        name: 'NearbyShops',
        component: () => import('@/views/NearbyShops.vue'),
        meta: { title: '附近店铺' },
      },
      {
        path: 'store-apply',
        name: 'StoreApply',
        component: () => import('@/views/StoreApply.vue'),
        meta: { title: '我想开店' },
      },
      {
        path: 'store-apply/records',
        name: 'StoreApplyRecords',
        component: () => import('@/views/StoreApplyRecords.vue'),
        meta: { title: '我的申请' },
      },
      {
        path: 'coupons',
        name: 'Coupons',
        component: () => import('@/views/Coupons.vue'),
        meta: { title: '我的优惠券' },
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
  const isAuthPath = to.path === '/login' || to.path === '/register'

  if (!token && !isAuthPath) {
    next('/login')
  } else if (token && isAuthPath) {
    next('/')
  } else {
    next()
  }
})

export default router
