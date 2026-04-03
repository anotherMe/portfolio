import client from './client'
import type { TradeRead } from '@/types'

export interface TradesParams {
  account_id?: number | null
  position_id?: number | null
}

export async function getTrades(params: TradesParams = {}): Promise<TradeRead[]> {
  const { data } = await client.get<TradeRead[]>('/trades/', { params })
  return data
}
