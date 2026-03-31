
import requests
from schemas import portfolio, instrument, trade, transaction, account
from schemas.trade import TradeCreate, TradeUpdate, TradeRead
from schemas.transaction import TransactionCreate, TransactionUpdate, TransactionRead
from schemas.instrument import InstrumentRead, InstrumentUpdate
from schemas.account import AccountRead, AccountUpdate


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

def get_trades_for_position(position_id: int) -> list[trade.TradeRead]:
    response = requests.get(f"{API_URL}/trades", params={"position_id": position_id})
    response.raise_for_status()
    return [trade.TradeRead(**item) for item in response.json()]

def get_transactions_for_position(position_id: int) -> list[transaction.TransactionRead]:
    response = requests.get(f"{API_URL}/transactions", params={"position_id": position_id})
    response.raise_for_status()
    return [transaction.TransactionRead(**item) for item in response.json()]

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


def create_trade(data: TradeCreate) -> TradeRead:
    response = requests.post(f"{API_URL}/trades/", json=data.model_dump(mode="json"))
    response.raise_for_status()
    return TradeRead(**response.json())


def update_trade(trade_id: int, data: TradeUpdate) -> TradeRead:
    payload = {k: v for k, v in data.model_dump(mode="json").items() if v is not None}
    response = requests.put(f"{API_URL}/trades/{trade_id}", json=payload)
    response.raise_for_status()
    return TradeRead(**response.json())


def delete_trade(trade_id: int) -> None:
    response = requests.delete(f"{API_URL}/trades/{trade_id}")
    response.raise_for_status()


def create_transaction(data: TransactionCreate) -> TransactionRead:
    response = requests.post(f"{API_URL}/transactions/", json=data.model_dump(mode="json"))
    response.raise_for_status()
    return TransactionRead(**response.json())


def update_transaction(transaction_id: int, data: TransactionUpdate) -> TransactionRead:
    payload = {k: v for k, v in data.model_dump(mode="json").items() if v is not None}
    response = requests.put(f"{API_URL}/transactions/{transaction_id}", json=payload)
    response.raise_for_status()
    return TransactionRead(**response.json())


def delete_transaction(transaction_id: int) -> None:
    response = requests.delete(f"{API_URL}/transactions/{transaction_id}")
    response.raise_for_status()


def update_instrument(instrument_id: int, data: InstrumentUpdate) -> InstrumentRead:
    payload = {k: v for k, v in data.model_dump(mode="json").items() if v is not None}
    response = requests.put(f"{API_URL}/instruments/{instrument_id}", json=payload)
    response.raise_for_status()
    return InstrumentRead(**response.json())


def delete_instrument(instrument_id: int) -> None:
    response = requests.delete(f"{API_URL}/instruments/{instrument_id}")
    response.raise_for_status()


def update_account(account_id: int, data: AccountUpdate) -> AccountRead:
    payload = {k: v for k, v in data.model_dump(mode="json").items() if v is not None}
    response = requests.put(f"{API_URL}/accounts/{account_id}", json=payload)
    response.raise_for_status()
    return AccountRead(**response.json())


def delete_account(account_id: int) -> None:
    response = requests.delete(f"{API_URL}/accounts/{account_id}")
    response.raise_for_status()