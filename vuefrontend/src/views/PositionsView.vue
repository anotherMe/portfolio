<script setup lang="ts">
import { ref, computed } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { RouterLink } from 'vue-router'
import { useAsyncData } from '@/composables/useAsyncData'
import { useFormatters } from '@/composables/useFormatters'
import { usePortfolioStore } from '@/stores/portfolio'
import { getPositions } from '@/api/positions'

const portfolioStore = usePortfolioStore()
const { formatMoney, formatPercent, formatDate, getPnlClass } = useFormatters()

type StatusFilter = 'open' | 'closed' | 'all'
const statusFilter = ref<StatusFilter>('open')

const { data: positions, isLoading } = useAsyncData(() =>
  getPositions({ account_id: portfolioStore.selectedAccountId }),
)

const filtered = computed(() => {
  if (!positions.value) return []
  if (statusFilter.value === 'all') return positions.value
  const closed = statusFilter.value === 'closed'
  return positions.value.filter((p) => p.position_closed === (closed ? 'Closed' : 'Open'))
})
</script>

<template>
  <div>
    <div class="toolbar">
      <div class="filter-tabs">
        <button
          v-for="opt in (['open', 'closed', 'all'] as StatusFilter[])"
          :key="opt"
          class="filter-tab"
          :class="{ 'filter-tab--active': statusFilter === opt }"
          @click="statusFilter = opt"
        >
          {{ opt.charAt(0).toUpperCase() + opt.slice(1) }}
        </button>
      </div>
    </div>

    <DataTable
      :value="filtered"
      :loading="isLoading"
      striped-rows
      size="small"
      sort-mode="single"
      :row-hover="true"
    >
      <Column field="instrument_name" header="Name" sortable>
        <template #body="{ data }">
          <RouterLink :to="`/positions/${data.position_id}`" class="table-link">
            {{ data.instrument_name }}
          </RouterLink>
        </template>
      </Column>
      <Column field="instrument_ticker" header="Ticker" sortable />
      <Column field="instrument_currency" header="CCY" />
      <Column field="remaining_quantity" header="Qty" sortable>
        <template #body="{ data }"><span class="numeric">{{ data.remaining_quantity }}</span></template>
      </Column>
      <Column field="total_invested" header="Invested" sortable>
        <template #body="{ data }">
          <span class="numeric">{{ formatMoney(data.total_invested, data.instrument_currency) }}</span>
        </template>
      </Column>
      <Column field="latest_price" header="Last Price" sortable>
        <template #body="{ data }">
          <span class="numeric">{{ formatMoney(data.latest_price, data.instrument_currency) }}</span>
        </template>
      </Column>
      <Column field="realized_pnl" header="Real. P&L" sortable>
        <template #body="{ data }">
          <span class="numeric" :class="getPnlClass(data.realized_pnl)">
            {{ formatMoney(data.realized_pnl, data.instrument_currency) }}
          </span>
        </template>
      </Column>
      <Column field="unrealized_pnl" header="Unreal. P&L" sortable>
        <template #body="{ data }">
          <span class="numeric" :class="getPnlClass(data.unrealized_pnl)">
            {{ formatMoney(data.unrealized_pnl, data.instrument_currency) }}
          </span>
        </template>
      </Column>
      <Column field="pnl" header="Total P&L" sortable>
        <template #body="{ data }">
          <span class="numeric" :class="getPnlClass(data.pnl)">
            {{ formatMoney(data.pnl, data.instrument_currency) }}
          </span>
        </template>
      </Column>
      <Column field="pnl_percent" header="%" sortable>
        <template #body="{ data }">
          <span class="numeric" :class="getPnlClass(data.pnl_percent)">
            {{ formatPercent(data.pnl_percent) }}
          </span>
        </template>
      </Column>
      <Column field="opening_date" header="Opened" sortable>
        <template #body="{ data }">{{ formatDate(data.opening_date) }}</template>
      </Column>
      <Column field="closing_date" header="Closed" sortable>
        <template #body="{ data }">{{ formatDate(data.closing_date) }}</template>
      </Column>
    </DataTable>
  </div>
</template>

<style scoped>
.toolbar {
  margin-bottom: 1rem;
}

.filter-tabs {
  display: flex;
  gap: 4px;
}

.filter-tab {
  padding: 0.375rem 0.875rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  border: 1px solid var(--p-surface-border);
  background: none;
  color: var(--p-text-muted-color);
  cursor: pointer;
  transition: all 0.15s;
}

.filter-tab:hover {
  background-color: var(--p-surface-hover);
  color: var(--p-text-color);
}

.filter-tab--active {
  background-color: var(--p-primary-color);
  border-color: var(--p-primary-color);
  color: white;
}

.table-link {
  color: var(--p-primary-color);
  text-decoration: none;
}

.table-link:hover {
  text-decoration: underline;
}
</style>
