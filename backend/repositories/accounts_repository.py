from typing import Optional
from sqlalchemy.orm import Session
from db.models import Account
from schemas.account import AccountUpdate


def get_all_accounts(session: Session):
    return session.query(Account).all()


def get_account_by_id(session: Session, account_id: int) -> Optional[Account]:
    return session.get(Account, account_id)


def update_account(session: Session, account_id: int, data: AccountUpdate) -> Optional[Account]:
    account = session.get(Account, account_id)
    if not account:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(account, field, value)
    session.flush()
    return account


def delete_account(session: Session, account_id: int) -> bool:
    account = session.get(Account, account_id)
    if account:
        session.delete(account)
        session.flush()
        return True
    return False
