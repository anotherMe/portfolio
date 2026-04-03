<script setup lang="ts">
defineProps<{
  label: string
  value: string
  colorClass?: string
  subLabel?: string
}>()
</script>

<template>
  <div class="stat-card">
    <span class="stat-label">{{ label }}</span>
    <span class="stat-value" :class="colorClass">{{ value }}</span>
    <span v-if="subLabel" class="stat-sub">{{ subLabel }}</span>
  </div>
</template>

<style scoped>
.stat-card {
  background-color: var(--p-surface-card);
  border: 1px solid var(--p-surface-border);
  border-radius: 8px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--p-text-muted-color);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--p-text-color);
}

.stat-sub {
  font-size: 0.8125rem;
  color: var(--p-text-muted-color);
}
</style>
