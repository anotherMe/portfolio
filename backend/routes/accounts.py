from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from services import accounts_service
from schemas.account import AccountCreate, AccountRead, AccountUpdate

router = APIRouter()

@router.post("/", response_model=AccountRead, status_code=201)
def create_account(data: AccountCreate, session: Session = Depends(get_db)):
    return accounts_service.create_account(session, data)


@router.get("/", response_model=List[AccountRead])
def get_accounts(session: Session = Depends(get_db)):
    """
    Retrieve all accounts.
    """
    return accounts_service.get_accounts(session)


@router.put("/{account_id}", response_model=AccountRead)
def update_account(account_id: int, data: AccountUpdate, session: Session = Depends(get_db)):
    result = accounts_service.update_account(session, account_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return result


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, session: Session = Depends(get_db)):
    deleted = accounts_service.delete_account(session, account_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Account not found")
