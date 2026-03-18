from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from services import transactions_service
from schemas.transaction import TransactionRead

router = APIRouter()

@router.get("/", response_model=List[TransactionRead])
def get_transactions(account_id: int = None, session: Session = Depends(get_db)):
    """
    Retrieve transactions. Optional account filter.
    """
    return transactions_service.get_transactions(session, account_id)
