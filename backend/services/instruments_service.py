
from typing import List, Optional
from sqlalchemy.orm import Session
from repositories import instruments_repository
from repositories import ohlcvs_repository
from schemas.instrument import InstrumentRead, InstrumentUpdate, InstrumentWithLastPrice

import logging

log = logging.getLogger(__name__)


def get_instruments(session: Session) -> List[InstrumentRead]:
    """
    Retrieve instruments.
    """
    all_instruments = instruments_repository.get_instruments(session)

    dtos = []
    for instrument in all_instruments:
        
        dto = InstrumentRead(
            id=instrument.id,
            name=instrument.name,
            ticker=instrument.ticker,
            isin=instrument.isin,   
            name_long=instrument.name_long,
            category=instrument.category,
            description=instrument.description,
            currency=instrument.currency,
        )

        dtos.append(dto)     
    
    return dtos


def update_instrument(session: Session, instrument_id: int, data: InstrumentUpdate) -> Optional[InstrumentRead]:
    instrument = instruments_repository.update_instrument(session, instrument_id, data)
    if not instrument:
        return None
    return InstrumentRead.model_validate(instrument)


def delete_instrument(session: Session, instrument_id: int) -> bool:
    return instruments_repository.delete_instrument(session, instrument_id)

def get_instruments_with_last_price(session: Session) -> List[InstrumentWithLastPrice]:
    """
    Retrieve instruments with last price date.
    """
    all_instruments = instruments_repository.get_instruments(session)

    dtos = []
    for instrument in all_instruments:
        
        last_price_date = ohlcvs_repository.get_latest_timestamp(session, instrument.id)
        
        dto = InstrumentWithLastPrice(
            id=instrument.id,
            name=instrument.name,
            ticker=instrument.ticker,
            isin=instrument.isin,   
            name_long=instrument.name_long,
            category=instrument.category,
            description=instrument.description,
            currency=instrument.currency,
            last_price_date=last_price_date,
        )

        dtos.append(dto)     
    
    return dtos
