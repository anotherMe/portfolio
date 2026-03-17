
import requests
from schemas import portfolio, instrument


API_URL = "http://localhost:8000"

def get_positions() -> list[portfolio.PositionSummary]:

    response = requests.get(f"{API_URL}/portfolio")
    response.raise_for_status()
    return [portfolio.PositionSummary(**item) for item in response.json()]

def get_instruments() -> list[instrument.InstrumentRead]:

    response = requests.get(f"{API_URL}/instruments")
    response.raise_for_status()
    return [instrument.InstrumentRead(**item) for item in response.json()]