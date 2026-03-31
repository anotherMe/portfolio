from typing import Optional
from sqlalchemy.orm import Session
from schemas.transaction import TransactionRead, TransactionCreate, TransactionUpdate
from repositories import transactions_repository
from utils import read_from_db

def get_transactions(session: Session, account_id: int = None) -> list[TransactionRead]:
    """Retrieve all transactions and map them to read schemas."""
    transactions = transactions_repository.get_all_transactions(session, account_id=account_id)

    result = []
    for t in transactions:
        tx_data = TransactionRead.model_validate(t)
        tx_data.amount = read_from_db(t.amount)
        result.append(tx_data)

    return result


def get_transactions_by_position(session: Session, position_id: int) -> list[TransactionRead]:
    """Retrieve all transactions for a specific position."""
    transactions = transactions_repository.get_transactions_for_position_list(session, [position_id])
    result = []
    for t in transactions:
        tx_data = TransactionRead.model_validate(t)
        tx_data.amount = read_from_db(t.amount)
        result.append(tx_data)
    return result


def create_transaction(session: Session, data: TransactionCreate) -> TransactionRead:
    tr = transactions_repository.create_transaction(session, data)
    session.commit()
    result = TransactionRead.model_validate(tr)
    result.amount = read_from_db(tr.amount)
    return result


def update_transaction(session: Session, transaction_id: int, data: TransactionUpdate) -> Optional[TransactionRead]:
    tr = transactions_repository.update_transaction(session, transaction_id, data)
    if tr is None:
        return None
    session.commit()
    result = TransactionRead.model_validate(tr)
    result.amount = read_from_db(tr.amount)
    return result


def delete_transaction(session: Session, transaction_id: int) -> bool:
    deleted = transactions_repository.delete_transaction(session, transaction_id)
    return deleted
