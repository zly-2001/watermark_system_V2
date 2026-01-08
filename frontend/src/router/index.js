import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    meta: { requiresAuth: true },
    redirect: '/embedding',
    children: [
      {
        path: '/embedding',
        name: 'EmbeddingStudio',
        component: () => import('@/views/EmbeddingStudio.vue'),
        meta: { title: '嵌入工作台', requiresAuth: true }
      },
      {
        path: '/attack',
        name: 'AttackLab',
        component: () => import('@/views/AttackLab.vue'),
        meta: { title: '异构攻击实验室', requiresAuth: true }
      },
      {
        path: '/tracing',
        name: 'TracingCenter',
        component: () => import('@/views/TracingCenter.vue'),
        meta: { title: '智能溯源与报告', requiresAuth: true }
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '算法效能看板', requiresAuth: true }
      },
      {
        path: '/history',
        name: 'History',
        component: () => import('@/views/History.vue'),
        meta: { title: '历史记录', requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查登录状态
router.beforeEach((to, from, next) => {
  const token = getToken()
  
  console.log('路由守卫:', {
    from: from.path,
    to: to.path,
    hasToken: !!token,
    requiresAuth: to.meta.requiresAuth
  })
  
  if (to.meta.requiresAuth && !token) {
    console.log('未登录，跳转到登录页')
    next('/login')
  } else if (to.path === '/login' && token) {
    console.log('已登录，跳转到首页')
    next('/')
  } else {
    console.log('允许访问')
    next()
  }
})

export default router

