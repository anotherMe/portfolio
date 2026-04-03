<script setup lang="ts">
import { computed } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useAsyncData } from '@/composables/useAsyncData'
import { useFormatters } from '@/composables/useFormatters'
import { usePortfolioStore } from '@/stores/portfolio'
import { getPositions, getPositionTotals } from '@/api/positions'
import StatCard from '@/components/shared/StatCard.vue'

const portfolioStore = usePortfolioStore()
const { formatMoney, formatPercent, formatDate, getPnlClass } = useFormatters()

const { data: totals, isLoading: totalsLoading } = useAsyncData(() =>
  getPositionTotals({ account_id: portfolioStore.selectedAccountId }),
)

const { data: positions, isLoading: positionsLoading } = useAsyncData(() =>
  getPositions({
    account_id: portfolioStore.selectedAccountId,
    include_open: true,
    include_closed: false,
  }),
)

const totalInvested = computed(() => {
  if (!totals.value?.length) return null
  return totals.value.map((t) => formatMoney(t.total_invested, t.currency)).join(' / ')
})

const totalPnl = computed(() => {
  if (!totals.value?.length) return null
  return totals.value.map((t) => formatMoney(t.total_pnl, t.currency)).join(' / ')
})

const totalPnlClass = computed(() => {
  if (!totals.value?.length) return ''
  const sum = totals.value.reduce((acc, t) => acc + t.total_pnl, 0)
  return getPnlClass(sum)
})
</script>

<template>
  <div>
    <!-- Summary cards -->
    <div class="stats-grid">
      <StatCard
        label="Total Invested"
        :value="totalsLoading ? '…' : (totalInvested ?? '—')"
      />
      <StatCard
        label="Total P&L"
        :value="totalsLoading ? '…' : (totalPnl ?? '—')"
        :color-class="totalPnlClass"
      />
      <StatCard
        label="Open Positions"
        :value="positionsLoading ? '…' : String(positions?.length ?? 0)"
      />
    </div>

    <!-- Open positions table -->
    <div class="section">
      <h2 class="section-title">Open Positions</h2>
      <DataTable
        :value="positions ?? []"
        :loading="positionsLoading"
        striped-rows
        size="small"
        sort-mode="single"
        :row-hover="true"
      >
        <Column field="instrument_name" header="Name" sortable />
        <Column field="instrument_ticker" header="Ticker" sortable />
        <Column field="instrument_currency" header="CCY" />
        <Column field="remaining_quantity" header="Qty" class="numeric" sortable />
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
        <Column field="unrealized_pnl" header="Unreal. P&L" sortable>
          <template #body="{ data }">
            <span class="numeric" :class="getPnlClass(data.unrealized_pnl)">
              {{ formatMoney(data.unrealized_pnl, data.instrument_currency) }}
            </span>
          </template>
        </Column>
        <Column field="unrealized_pnl_percent" header="%" sortable>
          <template #body="{ data }">
            <span class="numeric" :class="getPnlClass(data.unrealized_pnl_percent)">
              {{ formatPercent(data.unrealized_pnl_percent) }}
            </span>
          </template>
        </Column>
        <Column field="latest_price_date" header="Price Date">
          <template #body="{ data }">{{ formatDate(data.latest_price_date) }}</template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--p-text-muted-color);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}
</style>
