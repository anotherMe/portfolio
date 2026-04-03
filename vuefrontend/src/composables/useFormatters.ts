export function useFormatters() {
  function formatMoney(value: number, currency: string = 'EUR'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value)
  }

  function formatPercent(value: number): string {
    const sign = value > 0 ? '+' : ''
    return `${sign}${value.toFixed(2)}%`
  }

  function formatDate(dateStr: string | null): string {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }

  function getPnlClass(value: number): string {
    if (value > 0) return 'positive'
    if (value < 0) return 'negative'
    return ''
  }

  return { formatMoney, formatPercent, formatDate, getPnlClass }
}
