from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class UserAuth(Base):
    __tablename__ = "users_auth"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)  # Make username unique
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="USER")
    created_at = Column(DateTime(timezone=True), server_default=func.now())