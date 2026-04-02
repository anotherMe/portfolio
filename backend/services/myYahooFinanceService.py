import traceback
import datetime
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

def unix_to_datetime(ts):
    """Convert Unix timestamp to UTC datetime object."""
    try:
        ts = int(ts)
        return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    except (TypeError, ValueError):
        return None

# ---------------------------------------------------------------------
# Symbol Dataclass (Clean Python Dicts/Lists)
# ---------------------------------------------------------------------

@dataclass
class YahooSymbol:
    """Represent a Yahoo Finance symbol with metadata, price data, and events."""

    ticker: str
    name: str
    long_name: str
    currency: str
    data_granularity: str
    exchange_name: str
    full_exchange_name: str
    instrument_type: str
    gmtoffset: int
    timezone: str
    timezone_name: str
    ochlv: list[dict] = field(default_factory=list)
    events: Optional[list[dict]] = None

    def to_dict(self) -> dict:
        """Convert the Symbol to a dictionary."""
        return {
            "ticker": self.ticker,
            "name": self.name,
            "long_name": self.long_name,
            "currency": self.currency,
            "data_granularity": self.data_granularity,
            "exchange_name": self.exchange_name,
            "full_exchange_name": self.full_exchange_name,
            "instrument_type": self.instrument_type,
            "gmtoffset": self.gmtoffset,
            "timezone": self.timezone,
            "timezone_name": self.timezone_name,
            "ochlv": self.ochlv,
            "events": self.events,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "YahooSymbol":
        """Rebuild a Symbol object from a dictionary."""
        return cls(
            ticker=data["ticker"],
            name=data["name"],
            long_name=data["long_name"],
            currency=data["currency"],
            data_granularity=data["data_granularity"],
            exchange_name=data["exchange_name"],
            full_exchange_name=data["full_exchange_name"],
            instrument_type=data["instrument_type"],
            gmtoffset=data["gmtoffset"],
            timezone=data["timezone"],
            timezone_name=data["timezone_name"],
            ochlv=data.get("ochlv", []),
            events=data.get("events"),
        )

# ---------------------------------------------------------------------
# YahooSymbolParser (auto-loads on init)
# ---------------------------------------------------------------------

class YahooSymbolParser:
    """Load and parse a Yahoo Finance JSON file into a Symbol object on initialization."""

    def __init__(self, data: dict):
        self.data = data
        self.symbol: Optional[YahooSymbol] = None
        self._load()

    def _load(self):
        """Internal: load and parse the JSON dict into a Symbol dataclass."""

        if self.data["chart"]["error"] is not None:
            logger.error(f"Error in response: {self.data['chart']['error']}")
            return

        results = self.data["chart"].get("result", [])
        if len(results) != 1:
            logger.error("Wrong number of results found in the response.")
            return

        try:
            result = results[0]
            meta = result["meta"]

            # --- Build OCHLV List of dicts ---
            timestamps = [unix_to_datetime(ts) for ts in result.get("timestamp", [])]
            quote = result["indicators"]["quote"][0]
            opens = quote.get("open", [])
            highs = quote.get("high", [])
            lows = quote.get("low", [])
            closes = quote.get("close", [])
            volumes = quote.get("volume", [])
            
            adjcloses = []
            if result["indicators"].get("adjclose"):
                adjcloses = result["indicators"]["adjclose"][0].get("adjclose", [])

            ochlv_list = []
            for i in range(len(timestamps)):
                ochlv_list.append({
                    "timestamp": timestamps[i],
                    "open": opens[i] if i < len(opens) else None,
                    "high": highs[i] if i < len(highs) else None,
                    "low": lows[i] if i < len(lows) else None,
                    "close": closes[i] if i < len(closes) else None,
                    "volume": volumes[i] if i < len(volumes) else None,
                    "adjclose": adjcloses[i] if i < len(adjcloses) else None
                })

            # --- Parse events (Dividends) ---
            events_list = None
            dividends_data = self.safe_get(result, ["events", "dividends"])
            if dividends_data:
                events_list = []
                for ts_str, div_info in dividends_data.items():
                    events_list.append({
                        "timestamp": unix_to_datetime(ts_str),
                        "date": unix_to_datetime(div_info["date"]),
                        "amount": div_info["amount"]
                    })

            # --- Store Symbol object ---
            self.symbol = YahooSymbol(
                ticker=meta["symbol"],
                name=meta["shortName"],
                long_name=meta["longName"],
                currency=meta["currency"],
                data_granularity=meta["dataGranularity"],
                exchange_name=meta["exchangeName"],
                full_exchange_name=meta["fullExchangeName"],
                instrument_type=meta["instrumentType"],
                gmtoffset=meta["gmtoffset"],
                timezone=meta["timezone"],
                timezone_name=meta["exchangeTimezoneName"],
                ochlv=ochlv_list,
                events=events_list,
            )

        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            print(traceback.format_exc())

    def safe_get(self, d, path, default=None):
        """Safely get nested dictionary/list values by following a path list."""
        current = d
        for p in path:
            if isinstance(current, dict):
                current = current.get(p, default)
            elif isinstance(current, list):
                try:
                    current = current[p]
                except (IndexError, TypeError):
                    return default
            else:
                return default
        return current