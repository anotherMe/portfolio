from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from services import transactions_service
from schemas.transaction import TransactionRead, TransactionCreate, TransactionUpdate

router = APIRouter()

@router.get("/", response_model=List[TransactionRead])
def get_transactions(account_id: int = None, position_id: int = None, session: Session = Depends(get_db)):
    """
    Retrieve transactions. Optional account or position filter.
    """
    if position_id is not None:
        return transactions_service.get_transactions_by_position(session, position_id)
    return transactions_service.get_transactions(session, account_id)


@router.post("/", response_model=TransactionRead, status_code=201)
def create_transaction(data: TransactionCreate, session: Session = Depends(get_db)):
    return transactions_service.create_transaction(session, data)


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: int, data: TransactionUpdate, session: Session = Depends(get_db)):
    result = transactions_service.update_transaction(session, transaction_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, session: Session = Depends(get_db)):
    deleted = transactions_service.delete_transaction(session, transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
