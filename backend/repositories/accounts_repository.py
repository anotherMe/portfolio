from sqlalchemy.orm import Session
from db.models import Account

def get_all_accounts(session: Session):
    return session.query(Account).all()
