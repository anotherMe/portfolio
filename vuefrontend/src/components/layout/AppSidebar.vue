<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { LayoutDashboard, TrendingUp, ArrowLeftRight, Receipt, BarChart2, Wallet, Sun, Moon } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'
import { usePortfolioStore } from '@/stores/portfolio'
import { getAccounts } from '@/api/accounts'
import { ref } from 'vue'
import type { AccountRead } from '@/types'

const themeStore = useThemeStore()
const portfolioStore = usePortfolioStore()

const accounts = ref<AccountRead[]>([])

onMounted(async () => {
  accounts.value = await getAccounts()
})

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/positions', label: 'Positions', icon: TrendingUp },
  { to: '/trades', label: 'Trades', icon: ArrowLeftRight },
  { to: '/transactions', label: 'Transactions', icon: Receipt },
  { to: '/instruments', label: 'Instruments', icon: BarChart2 },
  { to: '/accounts', label: 'Accounts', icon: Wallet },
]
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-logo">
      <span class="logo-text">Portfolio</span>
    </div>

    <nav class="sidebar-nav">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        active-class="nav-item--active"
        exact-active-class="nav-item--active"
      >
        <component :is="item.icon" :size="18" />
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <div class="account-selector" v-if="accounts.length > 1">
        <select
          :value="portfolioStore.selectedAccountId ?? ''"
          @change="portfolioStore.setAccount(($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : null)"
          class="account-select"
        >
          <option value="">All accounts</option>
          <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
            {{ acc.name }}
          </option>
        </select>
      </div>

      <button class="theme-toggle" @click="themeStore.toggleTheme()" :title="`Switch to ${themeStore.theme === 'dark' ? 'light' : 'dark'} mode`">
        <Sun v-if="themeStore.theme === 'dark'" :size="18" />
        <Moon v-else :size="18" />
        <span>{{ themeStore.theme === 'dark' ? 'Light mode' : 'Dark mode' }}</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: sticky;
  top: 0;
  border-right: 1px solid var(--p-surface-border);
  background-color: var(--p-surface-ground);
}

.sidebar-logo {
  padding: 1.25rem 1rem;
  border-bottom: 1px solid var(--p-surface-border);
}

.logo-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--p-primary-color);
  letter-spacing: 0.02em;
}

.sidebar-nav {
  flex: 1;
  padding: 0.75rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  color: var(--p-text-muted-color);
  text-decoration: none;
  transition: background-color 0.15s, color 0.15s;
}

.nav-item:hover {
  background-color: var(--p-surface-hover);
  color: var(--p-text-color);
}

.nav-item--active {
  background-color: var(--p-primary-50);
  color: var(--p-primary-color);
  font-weight: 500;
}

:global(.dark) .nav-item--active {
  background-color: var(--p-primary-900);
}

.sidebar-footer {
  padding: 0.75rem 0.5rem;
  border-top: 1px solid var(--p-surface-border);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.account-select {
  width: 100%;
  padding: 0.375rem 0.5rem;
  font-size: 0.8125rem;
  border-radius: 6px;
  border: 1px solid var(--p-surface-border);
  background-color: var(--p-surface-card);
  color: var(--p-text-color);
  cursor: pointer;
}

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  color: var(--p-text-muted-color);
  background: none;
  border: none;
  cursor: pointer;
  width: 100%;
  transition: background-color 0.15s, color 0.15s;
}

.theme-toggle:hover {
  background-color: var(--p-surface-hover);
  color: var(--p-text-color);
}
</style>
