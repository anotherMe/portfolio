
from collections.abc import Generator
from sqlalchemy.orm import Session

from db.session import SessionLocal

'''

One session per request
Automatic commit on success
Automatic rollback on error
Guaranteed close

'''

def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()
    
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
