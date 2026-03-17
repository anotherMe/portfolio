from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased
from db.models import Price, Instrument
from utils import write_to_db
import pytz

# Note: Dependency on YahooSymbol/DataFrame handling will be moved to service layer or adapted
# For now, porting core DB access logic

def get_latest_prices_for_instrument_list(session: Session, inst_ids: list[int]):
    if not inst_ids:
        return []

    subquery = (
        select(
            Price.instrument_id,
            func.max(Price.date).label("latest_date")
        )
        .where(Price.instrument_id.in_(inst_ids))
        .group_by(Price.instrument_id)
        .subquery()
    )

    stmt = (
        select(Price.instrument_id, Price.price, subquery.c.latest_date.label("date"))
        .join(
            subquery,
            (Price.instrument_id == subquery.c.instrument_id) &
            (Price.date == subquery.c.latest_date)
        )
    )

    return session.execute(stmt).all()

def get_latest_price(session: Session, inst_id: int):
    stmt = (
        select(Price.price)
        .where(Price.instrument_id == inst_id)
        .order_by(Price.date.desc())
        .limit(1)
    )
    return session.scalar(stmt)

def get_latest_prices(session: Session):
    subquery = (
        select(
            Price.instrument_id,
            func.max(Price.date).label("latest_date")
        )
        .group_by(Price.instrument_id)
        .subquery()
    )

    stmt = (
        select(Price.instrument_id, Price.price, subquery.c.latest_date.label("date"))
        .join(
            subquery,
            (Price.instrument_id == subquery.c.instrument_id) &
            (Price.date == subquery.c.latest_date)
        )
    )

    return session.execute(stmt).mappings().all()
