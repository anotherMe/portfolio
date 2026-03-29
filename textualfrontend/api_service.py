
import requests
from schemas import portfolio, instrument, trade, transaction, account


API_URL = "http://localhost:8000"

def get_positions(account_id: int = None, include_open: bool = True, include_closed: bool = True) -> list[portfolio.PositionSummary]:
    
    url = f"{API_URL}/positions"
    params = {}
    params["account_id"] = account_id
    params["include_open"] = include_open
    params["include_closed"] = include_closed
    response = requests.get(url, params=params)
    response.raise_for_status()
    return [portfolio.PositionSummary(**item) for item in response.json()]

def get_instruments() -> list[instrument.InstrumentRead]:

    response = requests.get(f"{API_URL}/instruments")
    response.raise_for_status()
    return [instrument.InstrumentRead(**item) for item in response.json()]

def get_instruments_with_last_price() -> list[instrument.InstrumentWithLastPrice]:

    response = requests.get(f"{API_URL}/instruments/with-last-price")
    response.raise_for_status()
    return [instrument.InstrumentWithLastPrice(**item) for item in response.json()]

def get_trades(account_id: str = None) -> list[trade.TradeRead]:
    url = f"{API_URL}/trades"
    if account_id and account_id != "all":
        url += f"?account_id={account_id}"
    response = requests.get(url)
    response.raise_for_status()
    return [trade.TradeRead(**item) for item in response.json()]

def get_transactions(account_id: str = None) -> list[transaction.TransactionRead]:
    url = f"{API_URL}/transactions"
    if account_id and account_id != "all":
        url += f"?account_id={account_id}"
    response = requests.get(url)
    response.raise_for_status()
    return [transaction.TransactionRead(**item) for item in response.json()]

def get_accounts() -> list[account.AccountRead]:
    response = requests.get(f"{API_URL}/accounts")
    response.raise_for_status()
    return [account.AccountRead(**item) for item in response.json()]

def load_prices_for_instrument(instrument_id: int):
    response = requests.post(f"{API_URL}/prices/load/{instrument_id}")
    response.raise_for_status()
    return response.json()