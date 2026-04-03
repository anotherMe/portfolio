import client from './client'
import type { InstrumentRead } from '@/types'

export async function getInstruments(): Promise<InstrumentRead[]> {
  const { data } = await client.get<InstrumentRead[]>('/instruments/')
  return data
}
