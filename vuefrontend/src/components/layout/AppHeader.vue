<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <header class="app-header">
    <h1 class="page-title">{{ route.meta.title ?? '' }}</h1>
  </header>
</template>

<style scoped>
.app-header {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  border-bottom: 1px solid var(--p-surface-border);
  background-color: var(--p-surface-ground);
  flex-shrink: 0;
}

.page-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--p-text-color);
  margin: 0;
}
</style>
