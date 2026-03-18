from sqlalchemy.orm import Session
from schemas.transaction import TransactionRead
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
