<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useAsyncData } from '@/composables/useAsyncData'
import { getInstruments } from '@/api/instruments'

const { data: instruments, isLoading } = useAsyncData(getInstruments)
</script>

<template>
  <DataTable
    :value="instruments ?? []"
    :loading="isLoading"
    striped-rows
    size="small"
    sort-mode="single"
    :row-hover="true"
  >
    <Column field="name" header="Name" sortable />
    <Column field="ticker" header="Ticker" sortable />
    <Column field="isin" header="ISIN" />
    <Column field="currency" header="CCY" sortable />
    <Column field="category" header="Category" sortable />
  </DataTable>
</template>
