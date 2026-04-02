
from pandas import DataFrame
import math
import pytz
from sqlalchemy import desc, select, func
from sqlalchemy.orm import Session, aliased

from db.models import OHLCV, Instrument
from utils import write_to_db, read_from_db

DEFAULT_TIMEZONE = "Europe/Rome"


def add_price(session: Session, instrument, timestamp, granularity, open, close, high=0.0, low=0.0, volume=0.0):

    ohlcv = OHLCV(
        instrument_id=instrument.id, 
        timestamp=timestamp, 
        granularity=granularity,
        open=write_to_db(open),
        high=write_to_db(high),
        low=write_to_db(low),
        close=write_to_db(close),
        volume=write_to_db(volume)
    )
    session.add(ohlcv)
    session.flush() # ensures IDs and defaults are populated
    print(f"💰 Added OHLCV for {instrument.name}")
    return ohlcv

def get_latest_price(session: Session, inst_id):
    """Return the latest market price for an instrument, or None."""
    
    stmt = (
        select(OHLCV.close)
        .where(OHLCV.instrument_id == inst_id)
        .order_by(OHLCV.timestamp.desc())
        .limit(1)
    )
    return session.scalar(stmt)


def get_latest_timestamp(session: Session, inst_id):
    """Return the latest timestamp for an instrument's OHLCV, or None."""
    
    stmt = (
        select(OHLCV.timestamp)
        .where(OHLCV.instrument_id == inst_id)
        .order_by(OHLCV.timestamp.desc())
        .limit(1)
    )
    return session.scalar(stmt)

def get_latest_prices(session: Session):

    ohlcv_alias = aliased(OHLCV)

    subq = (
        select(
            ohlcv_alias.id,
            ohlcv_alias.instrument_id,
            ohlcv_alias.timestamp,
            func.row_number().over(
                partition_by=ohlcv_alias.instrument_id,
                order_by=ohlcv_alias.timestamp.desc()
            ).label("rnk")
        )
        .subquery()
    )

    stmt = (
        select(OHLCV)
        .join(subq, OHLCV.id == subq.c.id)
        .where(subq.c.rnk == 1)
    )

    return session.scalars(stmt).all()

def get_latest_prices_for_instrument_list(session: Session, inst_ids: list[int]):
    
    subquery = (
        select(
            OHLCV.instrument_id,
            func.max(OHLCV.timestamp).label("latest_date")
        )
        .where(OHLCV.instrument_id.in_(inst_ids))
        .group_by(OHLCV.instrument_id)
        .subquery()
    )

    stmt = (
        select(OHLCV.instrument_id, OHLCV.close, subquery.c.latest_date.label("date"))
        .join(
            subquery,
            (OHLCV.instrument_id == subquery.c.instrument_id) &
            (OHLCV.timestamp == subquery.c.latest_date)
        )
    )

    return session.execute(stmt).all()

def get_latest_closing_price(session: Session, instrument_id: int):
    
    last_price_row = (
        session.query(OHLCV)
        .filter(OHLCV.instrument_id == instrument_id)
        .order_by(desc(OHLCV.timestamp))
        .first()
    )
    
    return read_from_db(last_price_row.close) if last_price_row else None


def load_ohlcv_from_symbol(session: Session, symbol, granularity: str, instrument: Instrument):

    dataframe = symbol.ochlv_df
    if dataframe.empty:
        print("No OHLCV data to insert.")
        return
    
    inserted = 0
    skipped = 0

    # Pre-fetch existing timestamps for this symbol
    existing_timestamps = set(
        session.scalars(
            select(OHLCV.timestamp).where(OHLCV.instrument_id == instrument.id)
        ).all()
    )

    tz = pytz.timezone(symbol.timezone_name)
    for _, row in dataframe.iterrows():
        ts = row["timestamp"]
        dt = tz.localize(ts.to_pydatetime())
        if dt in existing_timestamps:
            skipped += 1
            continue

        if any(math.isnan(row[col]) for col in ("open", "high", "low", "close") if row[col] is not None):
            skipped += 1
            continue

        entry = OHLCV(
            instrument_id=instrument.id,
            timestamp=dt,
            granularity=granularity,
            open=write_to_db(row["open"]),
            high=write_to_db(row["high"]),
            low=write_to_db(row["low"]),
            close=write_to_db(row["close"]),
            volume=int(row["volume"] or 0),
        )

        session.add(entry)
        inserted += 1

    print(f"Inserted {inserted} new OHLCV rows, skipped {skipped} existing.")


def load_ohlcv_from_yfinance_dataframe(session: Session, dataframe: DataFrame, granularity: str, instrument: Instrument):

    if dataframe.empty:
        print("No OHLCV data to insert.")
        return
    
    inserted = 0
    skipped = 0

    # Pre-fetch existing timestamps for this symbol
    existing_timestamps = set(
        session.scalars(
            select(OHLCV.timestamp).where(OHLCV.instrument_id == instrument.id)
        ).all()
    )

    for ts, row in dataframe.iterrows():
        
        if ts.to_pydatetime() in existing_timestamps:
            skipped += 1
            continue

        entry = OHLCV(
            instrument_id=instrument.id,
            timestamp=ts,
            granularity=granularity,
            open=write_to_db(row["Open"]),
            high=write_to_db(row["High"]),
            low=write_to_db(row["Low"]),
            close=write_to_db(row["Close"]),
            volume=int(row["Volume"] or 0),
        )

        session.add(entry)
        inserted += 1

    print(f"Inserted {inserted} new OHLCV rows, skipped {skipped} existing.")
