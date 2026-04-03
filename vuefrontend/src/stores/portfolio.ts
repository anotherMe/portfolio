import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePortfolioStore = defineStore('portfolio', () => {
  const selectedAccountId = ref<number | null>(null)

  function setAccount(id: number | null) {
    selectedAccountId.value = id
  }

  return { selectedAccountId, setAccount }
})
