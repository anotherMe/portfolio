from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from services import accounts_service
from schemas.account import AccountRead

router = APIRouter()

@router.get("/", response_model=List[AccountRead])
def get_accounts(session: Session = Depends(get_db)):
    """
    Retrieve all accounts.
    """
    return accounts_service.get_accounts(session)
