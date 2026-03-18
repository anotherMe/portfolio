
import requests
from schemas import portfolio, instrument, trade, transaction, account


API_URL = "http://localhost:8000"

def get_positions(account_id: str = None) -> list[portfolio.PositionSummary]:
    url = f"{API_URL}/portfolio"
    if account_id and account_id != "all":
        url += f"?account_id={account_id}"
    response = requests.get(url)
    response.raise_for_status()
    return [portfolio.PositionSummary(**item) for item in response.json()]

def get_instruments() -> list[instrument.InstrumentRead]:

    response = requests.get(f"{API_URL}/instruments")
    response.raise_for_status()
    return [instrument.InstrumentRead(**item) for item in response.json()]

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