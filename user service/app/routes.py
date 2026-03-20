from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import httpx
import os
from .database import get_db
from .models import UserProfile
from .schemas import (
    UserCreate, UserUpdate, KYCUpdate, 
    UserProfileResponse, MessageResponse,
    UserProfileListResponse
)

router = APIRouter(prefix="/users", tags=["Users"])

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

async def validate_token(token: str) -> dict:
    """Validate token and return user data including role"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/auth/validate",
            json={"token": token}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        return response.json()

def check_admin_role(token_data: dict):
    """Check if user has admin role"""
    user_role = token_data.get("data", {}).get("role", "USER")
    if user_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")


# ✅ CREATE USER PROFILE - THIS ENDPOINT WAS MISSING!
@router.post("/", response_model=MessageResponse, status_code=201)
async def create_user_profile(
    user: UserCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(...)
):
    """Create user profile (authenticated users only)"""
    token = authorization.replace("Bearer ", "")
    token_data = await validate_token(token)
    
    # Get user info from token
    token_user_id = token_data.get("data", {}).get("user_id")
    token_role = token_data.get("data", {}).get("role", "USER")
    
    # Users can only create their own profile
    if token_user_id != user.user_id and token_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Cannot create profile for another user")
    
    # Check if profile already exists
    existing = db.query(UserProfile).filter(UserProfile.user_id == user.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User profile already exists")
    
    try:
        new_user = UserProfile(
            user_id=user.user_id,
            full_name=user.full_name,
            phone=getattr(user, 'phone', None),
            address=getattr(user, 'address', None),
            dob=getattr(user, 'dob', None),
            kyc_status="PENDING"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return MessageResponse(
            message="User profile created successfully",
            user_id=new_user.user_id
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User profile already exists")


# ✅ GET CURRENT USER PROFILE
@router.get("/me", response_model=UserProfileResponse)
async def get_current_user(
    db: Session = Depends(get_db),
    authorization: str = Header(...)
):
    """Get current user profile using token"""
    token = authorization.replace("Bearer ", "")
    token_data = await validate_token(token)
    
    user_id = token_data.get("data", {}).get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token data")
    
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User profile not found. Please complete your profile."
        )
    
    return user


# ✅ GET ALL USERS (ADMIN only)
@router.get("/", response_model=UserProfileListResponse)
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    kyc_status: Optional[str] = Query(None, pattern=r'^(PENDING|SUBMITTED|VERIFIED|REJECTED)$'),
    db: Session = Depends(get_db),
    authorization: str = Header(...)
):
    """Get all users with pagination - ADMIN ONLY"""
    token = authorization.replace("Bearer ", "")
    token_data = await validate_token(token)
    
    # Check admin role
    check_admin_role(token_data)
    
    query = db.query(UserProfile)
    
    if kyc_status:
        query = query.filter(UserProfile.kyc_status == kyc_status.upper())
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return UserProfileListResponse(
        users=users,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        per_page=limit
    )


# ✅ GET USER PROFILE BY ID
@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Get user profile by ID"""
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if authorization:
        token = authorization.replace("Bearer ", "")
        await validate_token(token)
    
    return user


# ✅ UPDATE USER PROFILE
@router.put("/{user_id}", response_model=MessageResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    authorization: str = Header(...)
):
    """Update user profile (owner only)"""
    token = authorization.replace("Bearer ", "")
    token_data = await validate_token(token)
    
    token_user_id = token_data.get("data", {}).get("user_id")
    token_role = token_data.get("data", {}).get("role", "USER")
    
    if token_user_id != user_id and token_role != "ADMIN":
        raise HTTPException(status_code=403, detail="You can only update your own profile")
    
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    return MessageResponse(message="User profile updated successfully")


# ✅ UPDATE KYC STATUS (ADMIN only)
@router.patch("/{user_id}/kyc", response_model=MessageResponse)
async def update_kyc(
    user_id: int,
    data: KYCUpdate,
    db: Session = Depends(get_db),
    authorization: str = Header(...)
):
    """Update user's KYC status - ADMIN ONLY"""
    token = authorization.replace("Bearer ", "")
    token_data = await validate_token(token)
    
    check_admin_role(token_data)
    
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.kyc_status = data.kyc_status.upper()
    db.commit()
    
    return MessageResponse(
        message=f"KYC status updated to {user.kyc_status}",
        user_id=user_id
    )


# ✅ DELETE USER PROFILE (ADMIN only)
@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(...)
):
    """Delete user profile - ADMIN ONLY"""
    token = authorization.replace("Bearer ", "")
    token_data = await validate_token(token)
    
    check_admin_role(token_data)
    
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return MessageResponse(message="User profile deleted successfully")


# ✅ HEALTH CHECK
@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "user-service"}