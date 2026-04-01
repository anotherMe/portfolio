from typing import Optional
from sqlalchemy.orm import Session
from schemas.account import AccountCreate, AccountRead, AccountUpdate
from repositories import accounts_repository


def create_account(session: Session, data: AccountCreate) -> AccountRead:
    account = accounts_repository.create_account(session, data)
    return AccountRead.model_validate(account)


def get_accounts(session: Session) -> list[AccountRead]:
    accounts = accounts_repository.get_all_accounts(session)
    return [AccountRead.model_validate(a) for a in accounts]


def update_account(session: Session, account_id: int, data: AccountUpdate) -> Optional[AccountRead]:
    account = accounts_repository.update_account(session, account_id, data)
    if not account:
        return None
    return AccountRead.model_validate(account)


def delete_account(session: Session, account_id: int) -> bool:
    return accounts_repository.delete_account(session, account_id)
