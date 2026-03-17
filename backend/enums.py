from enum import Enum

class TradeType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class TransactionType(str, Enum):
    DIVIDEND = "div"
    TAX = "tax"
    FEE = "fee"

class InstrumentCategory(str, Enum):
    ACC = "acc"
    DIST = "dist"
    NONE = "-"

class PriceGranularity(str, Enum):
    DAILY = "1d"
    WEEKLY = "1w"
    MONTHLY = "1m"

class Currency(Enum):
    EUR = ("Euro", "€")
    USD = ("US Dollar", "$")
    GBP = ("British Pound", "£")
    JPY = ("Japanese Yen", "¥")

    def __init__(self, name, symbol):
        self.full_name = name
        self.symbol = symbol

    @classmethod
    def from_code(cls, code: str):
        try:
            return cls[code]
        except KeyError:
            return None
