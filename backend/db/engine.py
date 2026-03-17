
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./portfolio.db"

'''

Why check_same_thread=False

- FastAPI serves requests in multiple threads
- SQLite by default forbids cross-thread connections
- SQLAlchemy handles concurrency at the session level

'''

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # REQUIRED for FastAPI
    future=True,
)
