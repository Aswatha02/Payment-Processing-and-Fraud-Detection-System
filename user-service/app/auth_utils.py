from jose import jwt, JWTError
from fastapi import HTTPException, Header
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def decode_token(token: str):
    """Decode JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(authorization: str = Header(...), db: Session = None):
    """Get current user from token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    role = payload.get("role")
    
    return {"id": user_id, "role": role, "username": payload.get("username")}
