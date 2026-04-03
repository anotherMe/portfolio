import client from './client'
import type { TransactionRead } from '@/types'

export interface TransactionsParams {
  account_id?: number | null
  position_id?: number | null
}

export async function getTransactions(params: TransactionsParams = {}): Promise<TransactionRead[]> {
  const { data } = await client.get<TransactionRead[]>('/transactions/', { params })
  return data
}
