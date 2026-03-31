from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from db.models import Transaction, Position, Trade
from utils import write_to_db
from schemas.transaction import TransactionCreate, TransactionUpdate

def add_transaction(session: Session, trans_type, amount, account_id, trade_id=None, description=None):
    tr = Transaction(
        account_id=account_id,
        trade_id=trade_id,
        date=datetime.now(),
        type=trans_type,
        amount=write_to_db(amount),
        description=description,
    )
    session.add(tr)
    session.flush()
    return tr

def get_all_transactions(session: Session, account_id: int = None):
    if account_id:
        return session.query(Transaction).filter_by(account_id=account_id).order_by(Transaction.date.desc()).all()
    else:
        return session.query(Transaction).all()

def get_transactions_for_position_list(session: Session, position_ids: list[int]) -> list[Transaction]:
    if not position_ids:
        return []

    return (
        session.query(Transaction)
        .join(Position, Transaction.position_id == Position.id)
        .filter(Position.id.in_(position_ids))
        .all()
    )

def create_transaction(session: Session, data: TransactionCreate) -> Transaction:
    tr = Transaction(
        account_id=data.account_id,
        position_id=data.position_id,
        date=data.date,
        type=data.type.value,
        amount=write_to_db(data.amount),
        description=data.description,
    )
    session.add(tr)
    session.flush()
    return tr


def update_transaction(session: Session, transaction_id: int, data: TransactionUpdate) -> Optional[Transaction]:
    tr = session.get(Transaction, transaction_id)
    if not tr:
        return None
    if data.date is not None:
        tr.date = data.date
    if data.type is not None:
        tr.type = data.type.value
    if data.amount is not None:
        tr.amount = write_to_db(data.amount)
    if data.description is not None:
        tr.description = data.description
    session.flush()
    return tr


def delete_transaction(session: Session, transaction_id: int):
    transaction = session.get(Transaction, transaction_id)
    if transaction:
        try:
            session.delete(transaction)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
    return False
