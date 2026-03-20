from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class UserCreate(BaseModel):
    user_id: int = Field(..., description="User ID from auth service")
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$')
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Full name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Full name must be less than 100 characters")
        return v
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v:
            # Remove any spaces or dashes
            v = re.sub(r'[\s\-]', '', v)
            if not re.match(r'^\+?[0-9]{10,15}$', v):
                raise ValueError("Phone must be 10-15 digits, optionally starting with +")
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$')
    address: Optional[str] = Field(None, max_length=255)
    dob: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Full name must be at least 2 characters")
            if len(v) > 100:
                raise ValueError("Full name must be less than 100 characters")
        return v
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = re.sub(r'[\s\-]', '', v)
            if not re.match(r'^\+?[0-9]{10,15}$', v):
                raise ValueError("Phone must be 10-15 digits, optionally starting with +")
        return v

class KYCUpdate(BaseModel):
    kyc_status: str = Field(..., pattern=r'^(PENDING|SUBMITTED|VERIFIED|REJECTED)$')
    
    @field_validator("kyc_status")
    @classmethod
    def validate_kyc_status(cls, v: str) -> str:
        v = v.upper()
        valid_statuses = ["PENDING", "SUBMITTED", "VERIFIED", "REJECTED"]
        if v not in valid_statuses:
            raise ValueError(f"KYC status must be one of: {', '.join(valid_statuses)}")
        return v

class UserProfileResponse(BaseModel):
    user_id: int
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    dob: Optional[str] = None
    kyc_status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class UserProfileListResponse(BaseModel):
    users: list[UserProfileResponse]
    total: int
    page: int
    per_page: int

class MessageResponse(BaseModel):
    message: str
    user_id: Optional[int] = None