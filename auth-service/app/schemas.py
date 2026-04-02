from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        if len(v) > 50:
            raise ValueError("Username must be at most 50 characters long.")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        # Only enforce minimum length, NO maximum length
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        # Optional: Keep strength requirements for security
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", v):
            raise ValueError(
                "Password must contain at least one special character (!@#$%^&* etc.)."
            )
        return v


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Optional[str] = "USER"
    is_suspended: Optional[bool] = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


# For backward compatibility
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class AdminRegisterRequest(UserCreate):
    admin_secret: str