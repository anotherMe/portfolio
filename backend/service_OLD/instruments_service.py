from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from lib.repo.instruments_repository import get_all_instruments as repo_get_all_instruments


class InstrumentDTO(BaseModel):
    id: int
    isin: Optional[str] = None
    ticker: Optional[str] = None
    name: str
    name_long: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    currency: str

    class Config:
        from_attributes = True


def get_all_instruments(session: Session) -> list[InstrumentDTO]:
    instruments = repo_get_all_instruments(session)
    return [InstrumentDTO.model_validate(i) for i in instruments]
