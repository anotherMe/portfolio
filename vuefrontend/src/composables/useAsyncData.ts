import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'

interface AsyncDataResult<T> {
  data: Ref<T | null>
  isLoading: Ref<boolean>
  error: Ref<string | null>
  reload: () => void
}

export function useAsyncData<T>(fetcher: () => Promise<T>): AsyncDataResult<T> {
  const data = ref<T | null>(null) as Ref<T | null>
  const isLoading = ref(true)
  const error = ref<string | null>(null)

  async function load() {
    isLoading.value = true
    error.value = null
    try {
      data.value = await fetcher()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An error occurred'
    } finally {
      isLoading.value = false
    }
  }

  onMounted(load)

  return { data, isLoading, error, reload: load }
}
