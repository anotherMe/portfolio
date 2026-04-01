from datetime import datetime
from rich.text import Text
from enums import Currency


def format_date(value: datetime | None) -> str:
    """Return a formatted date string or an em-dash if the value is None."""
    return value.strftime("%Y-%m-%d %H:%M") if value else "—"


def format_currency_color(value: float, currency_code: str) -> Text:
    """Return a Rich Text with currency symbol, thousands separator, and green/red color."""
    color = "green" if value >= 0 else "red"
    currency = Currency.from_code(currency_code)
    symbol = currency.symbol if currency else ""
    return Text(f"{value:,.2f}{symbol}", style=color)

def format_currency(value: float, currency_code: str) -> Text:
    """Return a Rich Text with currency symbol, thousands separator"""
    currency = Currency.from_code(currency_code)
    symbol = currency.symbol if currency else ""
    return Text(f"{value:,.2f}{symbol}")


def format_percent_color(value: float) -> Text:
    """Return a Rich Text with a percentage and green/red color."""
    color = "green" if value >= 0 else "red"
    return Text(f"{value:.1%}", style=color)
