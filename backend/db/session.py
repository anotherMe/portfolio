
from sqlalchemy.orm import sessionmaker

from db.engine import engine

'''

Key decisions:

- autocommit=False: explicit transaction control
- autoflush=False: predictable writes
- future=True: SQLAlchemy 2.0 semantics

'''

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)
