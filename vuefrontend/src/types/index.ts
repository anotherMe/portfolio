export type TradeType = 'buy' | 'sell'
export type TransactionType = 'div' | 'tax' | 'fee'
export type PriceGranularity = '1d' | '1w' | '1m'

export interface AccountRead {
  id: number
  name: string
  description: string | null
}

export interface InstrumentRead {
  id: number
  isin: string | null
  ticker: string | null
  name: string
  name_long: string | null
  category: string | null
  description: string | null
  currency: string
}

export interface InstrumentWithLastPrice extends InstrumentRead {
  last_price_date: string | null
}

export interface PositionSummary {
  position_id: number
  account_id: number
  instrument_id: number
  instrument_name: string
  instrument_isin: string
  instrument_ticker: string
  instrument_currency: string
  opening_date: string | null
  total_invested: number
  latest_price: number
  latest_price_date: string | null
  transactions_amount: number
  closing_date: string | null
  remaining_quantity: number
  remaining_cost_basis: number
  realized_pnl: number
  unrealized_pnl: number
  realized_pnl_percent: number
  unrealized_pnl_percent: number
  pnl: number
  pnl_percent: number
  position_closed: string
}

export interface PositionTotals {
  currency: string
  symbol: string
  total_invested: number
  total_pnl: number
}

export interface TradeRead {
  id: number
  position_id: number
  date: string
  type: TradeType
  quantity: number
  price: number
  description: string | null
}

export interface TransactionRead {
  id: number
  account_id: number
  position_id: number | null
  date: string
  type: TransactionType
  amount: number
  description: string | null
}
