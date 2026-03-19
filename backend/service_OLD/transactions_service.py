from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from lib.database import read_from_db
from lib.repo.transactions_repository import get_all_transactions as repo_get_all_transactions


class TransactionDTO(BaseModel):
    id: int
    date: datetime
    type: str
    amount: float
    description: Optional[str] = None
    account_id: int
    position_id: Optional[int] = None

    class Config:
        from_attributes = True


def _apply_conversions(transaction):
    transaction.amount = read_from_db(transaction.amount)
    return transaction


def get_all_transactions(session: Session, account=None) -> list[TransactionDTO]:
    transactions = repo_get_all_transactions(session, account=account)
    converted = [_apply_conversions(t) for t in transactions]
    return [TransactionDTO.model_validate(t) for t in converted]
