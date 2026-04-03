<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useAsyncData } from '@/composables/useAsyncData'
import { getAccounts } from '@/api/accounts'

const { data: accounts, isLoading } = useAsyncData(getAccounts)
</script>

<template>
  <DataTable
    :value="accounts ?? []"
    :loading="isLoading"
    striped-rows
    size="small"
    sort-mode="single"
    :row-hover="true"
  >
    <Column field="id" header="ID" />
    <Column field="name" header="Name" sortable />
    <Column field="description" header="Description" />
  </DataTable>
</template>
