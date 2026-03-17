
from typing import List
from sqlalchemy.orm import Session
from repositories import instruments_repository
from schemas.instrument import InstrumentRead

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
