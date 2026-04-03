<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { RouterLink } from 'vue-router'
import { useAsyncData } from '@/composables/useAsyncData'
import { useFormatters } from '@/composables/useFormatters'
import { usePortfolioStore } from '@/stores/portfolio'
import { getTrades } from '@/api/trades'

const portfolioStore = usePortfolioStore()
const { formatDate } = useFormatters()

const { data: trades, isLoading } = useAsyncData(() =>
  getTrades({ account_id: portfolioStore.selectedAccountId }),
)
</script>

<template>
  <DataTable
    :value="trades ?? []"
    :loading="isLoading"
    striped-rows
    size="small"
    sort-mode="single"
    :row-hover="true"
  >
    <Column field="date" header="Date" sortable>
      <template #body="{ data }">{{ formatDate(data.date) }}</template>
    </Column>
    <Column field="type" header="Type">
      <template #body="{ data }">
        <span class="trade-badge" :class="`trade-badge--${data.type}`">{{ data.type.toUpperCase() }}</span>
      </template>
    </Column>
    <Column field="position_id" header="Position">
      <template #body="{ data }">
        <RouterLink :to="`/positions/${data.position_id}`" class="table-link">
          #{{ data.position_id }}
        </RouterLink>
      </template>
    </Column>
    <Column field="quantity" header="Qty" sortable>
      <template #body="{ data }"><span class="numeric">{{ data.quantity }}</span></template>
    </Column>
    <Column field="price" header="Price" sortable>
      <template #body="{ data }"><span class="numeric">{{ data.price.toFixed(4) }}</span></template>
    </Column>
    <Column field="description" header="Note" />
  </DataTable>
</template>

<style scoped>
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

.table-link {
  color: var(--p-primary-color);
  text-decoration: none;
}

.table-link:hover {
  text-decoration: underline;
}
</style>
