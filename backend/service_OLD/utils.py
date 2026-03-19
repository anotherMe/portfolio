

from lib.settings_manager import get_timezone


DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M"




def to_local(dt):
    if dt is None:
        return None
    return dt.astimezone(get_timezone()).strftime(DEFAULT_DATETIME_FORMAT)

def format_currency(amount, currency_symbol="€"):
    if amount is None:
        return "N/A"
    return f"{amount:.2f} {currency_symbol}"

def format_currency_color(amount, currency_symbol="€"):

    if amount < 0:
        color = "red"
    elif amount == 0:
        color = "gray"
    else:
        color = "green"

    if amount is None:
        return "N/A"
    return {"formatted": f"{amount:.2f} {currency_symbol}", "color": color}