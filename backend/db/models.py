
from datetime import timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    Integer,
    ForeignKey,
    Text,
    TypeDecorator,
    UniqueConstraint
)


# ==========================================================
# Base
# ==========================================================

class Base(DeclarativeBase):
    pass


# ==========================================================
# Enums
# ==========================================================

# Enums are imported from enums.py


# ==========================================================
# Type decorators
# ==========================================================

class UTCDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if value.tzinfo is None:
            raise ValueError("naive datetime")
        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return value.replace(tzinfo=timezone.utc)


# ==========================================================
# Models
# ==========================================================

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)

    transactions = relationship("Transaction", back_populates="account", cascade="all")
    positions = relationship("Position", back_populates="account", cascade="all")

    def __repr__(self):
        return f"<Account id={self.id} name={self.name!r}>"


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    isin = Column(String, unique=True)
    ticker = Column(String)
    name = Column(String, nullable=False)
    name_long = Column(String)
    category = Column(String, nullable=False)
    description = Column(Text)
    currency = Column(String, nullable=False)

    prices = relationship("Price", back_populates="instrument", cascade="all")
    ohlcvs = relationship("OHLCV", back_populates="instrument", cascade="all")
    positions = relationship("Position", back_populates="instrument", cascade="all")

    def __repr__(self):
        return f"<Instrument id={self.id} name={self.name!r} currency={self.currency}>"


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    closed = Column(Boolean, nullable=False, default=False)
    closing_date = Column(UTCDateTime)

    account = relationship("Account", back_populates="positions")
    instrument = relationship("Instrument", back_populates="positions")
    transactions = relationship("Transaction", back_populates="position", cascade="all")
    trades = relationship("Trade", back_populates="position", cascade="all")

    def __repr__(self):
        return (
            f"<Position id={self.id} account_id={self.account_id} "
            f"instrument_id={self.instrument_id} closed={self.closed}>"
        )


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)
    date = Column(UTCDateTime, nullable=False)
    type = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(Text)

    position = relationship("Position", back_populates="trades")

    def __repr__(self):
        return (
            f"<Trade id={self.id} position_id={self.position_id} "
            f"type={self.type} quantity={self.quantity} price={self.price}>"
        )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"))
    date = Column(UTCDateTime, nullable=False)
    type = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(Text)

    account = relationship("Account", back_populates="transactions")
    position = relationship("Position", back_populates="transactions")

    def __repr__(self):
        return (
            f"<Transaction id={self.id} account_id={self.account_id} "
            f"type={self.type} amount={self.amount}>"
        )


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    date = Column(UTCDateTime, nullable=False)
    price = Column(Integer, nullable=False)
    granularity = Column(String, nullable=False)

    instrument = relationship("Instrument", back_populates="prices")

    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "date",
            "granularity",
            name="_instrument_date_uc",
        ),
    )

    def __repr__(self):
        return (
            f"<Price id={self.id} instrument_id={self.instrument_id} "
            f"date={self.date} price={self.price} granularity={self.granularity}>"
        )


class OHLCV(Base):
    __tablename__ = "ohlcvs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    timestamp = Column(UTCDateTime, nullable=False)
    granularity = Column(String, nullable=False)
    open = Column(Integer)
    high = Column(Integer)
    low = Column(Integer)
    close = Column(Integer)
    volume = Column(Integer)

    instrument = relationship("Instrument", back_populates="ohlcvs")

    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "timestamp",
            "granularity",
            name="_instrument_timestamp_uc",
        ),
    )

    def __repr__(self):
        return (
            f"<OHLCV id={self.id} instrument_id={self.instrument_id} "
            f"timestamp={self.timestamp} granularity={self.granularity}>"
        )
