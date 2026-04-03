import client from './client'
import type { PositionSummary, PositionTotals } from '@/types'

export interface PositionsParams {
  account_id?: number | null
  include_open?: boolean
  include_closed?: boolean
}

export async function getPositions(params: PositionsParams = {}): Promise<PositionSummary[]> {
  const { data } = await client.get<PositionSummary[]>('/positions/', { params })
  return data
}

export async function getPositionTotals(params: PositionsParams = {}): Promise<PositionTotals[]> {
  const { data } = await client.get<PositionTotals[]>('/positions/totals', { params })
  return data
}
