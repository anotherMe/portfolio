<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useAsyncData } from '@/composables/useAsyncData'
import { useFormatters } from '@/composables/useFormatters'
import { usePortfolioStore } from '@/stores/portfolio'
import { getTransactions } from '@/api/transactions'

const portfolioStore = usePortfolioStore()
const { formatDate, formatMoney, getPnlClass } = useFormatters()

const { data: transactions, isLoading } = useAsyncData(() =>
  getTransactions({ account_id: portfolioStore.selectedAccountId }),
)

const typeLabels: Record<string, string> = {
  div: 'Dividend',
  tax: 'Tax',
  fee: 'Fee',
}
</script>

<template>
  <DataTable
    :value="transactions ?? []"
    :loading="isLoading"
    striped-rows
    size="small"
    sort-mode="single"
    :row-hover="true"
  >
    <Column field="date" header="Date" sortable>
      <template #body="{ data }">{{ formatDate(data.date) }}</template>
    </Column>
    <Column field="type" header="Type" sortable>
      <template #body="{ data }">
        <span class="type-badge" :class="`type-badge--${data.type}`">
          {{ typeLabels[data.type] ?? data.type }}
        </span>
      </template>
    </Column>
    <Column field="amount" header="Amount" sortable>
      <template #body="{ data }">
        <span class="numeric" :class="getPnlClass(data.amount)">
          {{ formatMoney(data.amount) }}
        </span>
      </template>
    </Column>
    <Column field="account_id" header="Account" />
    <Column field="description" header="Note" />
  </DataTable>
</template>

<style scoped>
.type-badge {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.type-badge--div {
  background-color: var(--p-blue-100);
  color: var(--p-blue-700);
}

.type-badge--tax {
  background-color: var(--p-orange-100);
  color: var(--p-orange-700);
}

.type-badge--fee {
  background-color: var(--p-surface-200);
  color: var(--p-text-muted-color);
}

:global(.dark) .type-badge--div {
  background-color: var(--p-blue-900);
  color: var(--p-blue-300);
}

:global(.dark) .type-badge--tax {
  background-color: var(--p-orange-900);
  color: var(--p-orange-300);
}
</style>
