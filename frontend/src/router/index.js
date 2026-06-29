import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/Products.vue')
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('../views/Suppliers.vue')
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('../views/Customers.vue')
      },
      {
        path: 'purchases',
        name: 'Purchases',
        component: () => import('../views/Purchases.vue')
      },
      {
        path: 'sales',
        name: 'Sales',
        component: () => import('../views/Sales.vue')
      },
      {
        path: 'sales/create',
        name: 'SalesCreate',
        component: () => import('../views/SalesOrderForm.vue')
      },
      {
        path: 'sales/:id/edit',
        name: 'SalesEdit',
        component: () => import('../views/SalesOrderForm.vue')
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('../views/Inventory.vue')
      },
      {
        path: 'invoices',
        name: 'Invoices',
        component: () => import('../views/Invoices.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
