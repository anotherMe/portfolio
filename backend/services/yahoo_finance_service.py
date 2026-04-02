
from datetime import datetime
import json
import logging
import yfinance as yf
from typing import Any, Tuple
from sqlalchemy.orm import Session

from db.models import Instrument
from repositories.instruments_repository import get_instrument_by_ticker
from repositories.ohlcvs_repository import load_ohlcv_from_symbol, load_ohlcv_from_yfinance_dataframe
from services.my_yahoo_finance_service import YahooSymbolParser

log = logging.getLogger(__name__)

DEFAULT_GRANULARITY = '1d'

class PortfolioException(Exception):
    def __init__(self, service_name: str, message: str):
        self.service_name = service_name
        self.message = message
        super().__init__(f"{service_name}: {message}")


def download_history(session: Session, instrument: Instrument, start_date: datetime) -> Tuple[bool, str]:

    try:
        yf_symbol = yf.Ticker(instrument.ticker)
        df = yf_symbol.history(start=start_date, interval=DEFAULT_GRANULARITY)
        load_ohlcv_from_yfinance_dataframe(session, df, DEFAULT_GRANULARITY, instrument)
        return True, f"Symbol {instrument.ticker} parsed correctly"
    
    except Exception:
        logging.exception("")
        return(False, f"Failed to parse symbol: {instrument.ticker}")


def parse_json_file_into_yahoo_symbol(uploaded_file: Any) -> YahooSymbolParser:
    try:
        data = json.load(uploaded_file)
        return YahooSymbolParser(data)
    except Exception:
        logging.exception("")
        raise PortfolioException("YahooFinanceService", f"Failed to parse file: {uploaded_file.name}")


def parse_file(session: Session, parser: YahooSymbolParser, create_instrument: bool):
    """For each uploaded file: 

        - parse the JSON into a YahooSymbolParser object
        - retrieve the Instrument if present ...
        - create the Instrument if not present
        - load Prices
        - load OHLCVs

    Args:
        uploaded_file (Any): _description_
        create_instrument (bool): _description_

    Raises:
        PortfolioException: _description_
    """

    try:
        instrument = get_instrument_by_ticker(session, parser.symbol.ticker)
    except Exception as ex:
        print(ex)
        raise PortfolioException("YahooFinanceService", f"Error while retrieving Instrument with ticker {parser.symbol.ticker}")
        
    if not instrument and not create_instrument:
        raise PortfolioException("YahooFinanceService", f"No Instrument found with ticker: {parser.symbol.ticker}")

    if not instrument and create_instrument:

        try:
            instrument = Instrument()
            instrument.ticker = parser.symbol.ticker
            instrument.name = parser.symbol.name
            instrument.name_long = parser.symbol.long_name
            instrument.currency = parser.symbol.currency
            session.add(instrument)
            session.commit()
        except Exception as ex:
            session.rollback()
            logging.exception("Error while creating instrument")
            raise PortfolioException("YahooFinanceService", "Error while parsing file") from ex

    try:
        load_ohlcv_from_symbol(session, parser.symbol, parser.symbol.data_granularity, instrument)
    except Exception as ex:
        logging.exception("Can't load data into OHLCVs")
        raise PortfolioException("YahooFinanceService", "Can't load data into OHLCVs") from ex
    