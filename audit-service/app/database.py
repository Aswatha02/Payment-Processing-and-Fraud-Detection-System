from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL found, raise error
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file")

# For PostgreSQL, we don't need the check_same_thread parameter (that's SQLite specific)
# PostgreSQL handles connections differently
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()