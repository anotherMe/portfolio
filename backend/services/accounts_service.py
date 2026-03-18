from sqlalchemy.orm import Session
from schemas.account import AccountRead
from repositories import accounts_repository

def get_accounts(session: Session) -> list[AccountRead]:
    accounts = accounts_repository.get_all_accounts(session)
    return [AccountRead.model_validate(a) for a in accounts]
