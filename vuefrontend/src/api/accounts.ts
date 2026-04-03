import client from './client'
import type { AccountRead } from '@/types'

export async function getAccounts(): Promise<AccountRead[]> {
  const { data } = await client.get<AccountRead[]>('/accounts/')
  return data
}
