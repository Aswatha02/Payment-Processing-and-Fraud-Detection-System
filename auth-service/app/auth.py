from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Use Argon2 - no password length limitations, more secure
pwd_context = CryptContext(
    schemes=["argon2"], 
    deprecated="auto",
    argon2__memory_cost=1024,      # Memory cost (default: 1024)
    argon2__time_cost=3,            # Time cost (default: 3)
    argon2__parallelism=1           # Parallelism (default: 1)
)

def hash_password(password: str):
    """Hash password with Argon2 - supports any length password."""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    """Verify password against hash."""
    return pwd_context.verify(password, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
