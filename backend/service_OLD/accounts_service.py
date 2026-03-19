from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from lib.repo.accounts_repository import get_all_accounts as repo_get_all_accounts


class AccountDTO(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


def get_all_accounts(session: Session) -> list[AccountDTO]:
    accounts = repo_get_all_accounts(session)
    return [AccountDTO.model_validate(a) for a in accounts]
