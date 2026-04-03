<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useAsyncData } from '@/composables/useAsyncData'
import { useFormatters } from '@/composables/useFormatters'
import { getPositions } from '@/api/positions'
import { getTrades } from '@/api/trades'
import StatCard from '@/components/shared/StatCard.vue'

const route = useRoute()
const positionId = Number(route.params.id)
const { formatMoney, formatPercent, formatDate, getPnlClass } = useFormatters()

const { data: allPositions, isLoading: posLoading } = useAsyncData(() => getPositions())
const { data: trades, isLoading: tradesLoading } = useAsyncData(() =>
  getTrades({ position_id: positionId }),
)

const position = computed(() =>
  allPositions.value?.find((p) => p.position_id === positionId) ?? null,
)
</script>

<template>
  <div v-if="posLoading" class="loading-msg">Loading…</div>
  <div v-else-if="!position" class="loading-msg">Position not found.</div>
  <div v-else>
    <div class="pos-header">
      <div>
        <h2 class="pos-name">{{ position.instrument_name }}</h2>
        <span class="pos-ticker">{{ position.instrument_ticker }} · {{ position.instrument_currency }}</span>
      </div>
      <span class="pos-status" :class="position.position_closed === 'Closed' ? 'status-closed' : 'status-open'">
        {{ position.position_closed }}
      </span>
    </div>

    <div class="stats-grid">
      <StatCard label="Total Invested" :value="formatMoney(position.total_invested, position.instrument_currency)" />
      <StatCard label="Quantity" :value="String(position.remaining_quantity)" />
      <StatCard label="Last Price" :value="formatMoney(position.latest_price, position.instrument_currency)" :sub-label="formatDate(position.latest_price_date)" />
      <StatCard label="Realized P&L" :value="formatMoney(position.realized_pnl, position.instrument_currency)" :color-class="getPnlClass(position.realized_pnl)" />
      <StatCard label="Unrealized P&L" :value="formatMoney(position.unrealized_pnl, position.instrument_currency)" :color-class="getPnlClass(position.unrealized_pnl)" />
      <StatCard label="Total P&L" :value="`${formatMoney(position.pnl, position.instrument_currency)} (${formatPercent(position.pnl_percent)})`" :color-class="getPnlClass(position.pnl)" />
    </div>

    <div class="section">
      <h2 class="section-title">Trades</h2>
      <DataTable :value="trades ?? []" :loading="tradesLoading" striped-rows size="small" sort-mode="single">
        <Column field="date" header="Date" sortable>
          <template #body="{ data }">{{ formatDate(data.date) }}</template>
        </Column>
        <Column field="type" header="Type">
          <template #body="{ data }">
            <span class="trade-badge" :class="`trade-badge--${data.type}`">{{ data.type.toUpperCase() }}</span>
          </template>
        </Column>
        <Column field="quantity" header="Qty" sortable>
          <template #body="{ data }"><span class="numeric">{{ data.quantity }}</span></template>
        </Column>
        <Column field="price" header="Price" sortable>
          <template #body="{ data }">
            <span class="numeric">{{ formatMoney(data.price, position.instrument_currency) }}</span>
          </template>
        </Column>
        <Column field="description" header="Note" />
      </DataTable>
    </div>
  </div>
</template>

<style scoped>
.loading-msg {
  color: var(--p-text-muted-color);
  padding: 2rem;
  text-align: center;
}

.pos-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.pos-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--p-text-color);
  margin: 0 0 0.25rem;
}

.pos-ticker {
  font-size: 0.875rem;
  color: var(--p-text-muted-color);
}

.pos-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
}

.status-open {
  background-color: var(--p-green-100);
  color: var(--p-green-700);
}

.status-closed {
  background-color: var(--p-surface-200);
  color: var(--p-text-muted-color);
}

:global(.dark) .status-open {
  background-color: var(--p-green-900);
  color: var(--p-green-300);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0.75rem;
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

.trade-badge {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.trade-badge--buy {
  background-color: var(--p-green-100);
  color: var(--p-green-700);
}

.trade-badge--sell {
  background-color: var(--p-red-100);
  color: var(--p-red-700);
}

:global(.dark) .trade-badge--buy {
  background-color: var(--p-green-900);
  color: var(--p-green-300);
}

:global(.dark) .trade-badge--sell {
  background-color: var(--p-red-900);
  color: var(--p-red-300);
}
</style>
