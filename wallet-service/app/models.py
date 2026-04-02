from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from .database import Base

class Wallet(Base):
    __tablename__ = "wallets"

    wallet_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Ledger(Base):
    __tablename__ = "ledger"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # credit / debit
    amount = Column(Float, nullable=False)
    balance_before = Column(Float, nullable=True)
    balance_after = Column(Float, nullable=True)
    source = Column(String, default="user")  # user / internal
    description = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)