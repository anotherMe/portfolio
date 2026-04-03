import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { title: 'Dashboard' },
        },
        {
          path: 'positions',
          name: 'positions',
          component: () => import('@/views/PositionsView.vue'),
          meta: { title: 'Positions' },
        },
        {
          path: 'positions/:id',
          name: 'position-detail',
          component: () => import('@/views/PositionDetailView.vue'),
          meta: { title: 'Position Detail' },
        },
        {
          path: 'trades',
          name: 'trades',
          component: () => import('@/views/TradesView.vue'),
          meta: { title: 'Trades' },
        },
        {
          path: 'transactions',
          name: 'transactions',
          component: () => import('@/views/TransactionsView.vue'),
          meta: { title: 'Transactions' },
        },
        {
          path: 'instruments',
          name: 'instruments',
          component: () => import('@/views/InstrumentsView.vue'),
          meta: { title: 'Instruments' },
        },
        {
          path: 'accounts',
          name: 'accounts',
          component: () => import('@/views/AccountsView.vue'),
          meta: { title: 'Accounts' },
        },
      ],
    },
  ],
})

export default router
