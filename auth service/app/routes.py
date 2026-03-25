from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from .database import get_db
from .models import UserAuth
from .schemas import UserCreate, UserOut, LoginRequest, Token, TokenResponse, AdminRegisterRequest
from .auth import *
from sqlalchemy.exc import IntegrityError
import os

router = APIRouter(prefix="/auth", tags=["Auth"])


# ✅ REGISTER
@router.post("/register", response_model=TokenResponse)
def register(req: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_email = db.query(UserAuth).filter(UserAuth.email == req.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    existing_username = db.query(UserAuth).filter(UserAuth.username == req.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    try:
        user = UserAuth(
            username=req.username,
            email=req.email,
            password_hash=hash_password(req.password),
            role="USER"
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create BOTH access and refresh tokens
        payload = {"user_id": user.id, "role": user.role, "username": user.username}
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)
        
        # Return both tokens
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserOut.model_validate(user)
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Registration failed")


# 🛡️ ADMIN REGISTER
@router.post("/admin/register", response_model=TokenResponse)
def admin_register(req: AdminRegisterRequest, db: Session = Depends(get_db)):
    ADMIN_SECRET = os.getenv("ADMIN_SECRET", "super-secret-admin-key")
    if req.admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    existing_email = db.query(UserAuth).filter(UserAuth.email == req.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = db.query(UserAuth).filter(UserAuth.username == req.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    try:
        user = UserAuth(
            username=req.username,
            email=req.email,
            password_hash=hash_password(req.password),
            role="ADMIN"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        payload = {"user_id": user.id, "role": user.role, "username": user.username}
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "token_type": "bearer",
            "user": UserOut.model_validate(user)
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Registration failed")


# 🛡️ ADMIN LOGIN
@router.post("/admin/login", response_model=TokenResponse)
def admin_login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserAuth).filter(UserAuth.email == req.email).first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    if getattr(user, "is_suspended", False):
        raise HTTPException(status_code=403, detail="Account suspended")

    payload = {"user_id": user.id, "role": user.role, "username": user.username}
    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
        "token_type": "bearer",
        "user": UserOut.model_validate(user)
    }



# ✅ LOGIN
@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserAuth).filter(UserAuth.email == req.email).first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if getattr(user, "is_suspended", False):
        raise HTTPException(status_code=403, detail="Account suspended")

    payload = {"user_id": user.id, "role": user.role, "username": user.username}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserOut.model_validate(user)
    }


# 🔁 REFRESH
@router.post("/refresh")
def refresh_token(refresh_token: str):
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token({
        "user_id": payload["user_id"],
        "role": payload["role"],
        "username": payload.get("username")
    })

    return {"access_token": new_access, "token_type": "bearer"}


# 👤 ME
@router.get("/me", response_model=UserOut)
def get_me(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    user = db.query(UserAuth).filter(UserAuth.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserOut.model_validate(user)


# 🛡️ GET CURRENT ADMIN DEPENDENCY
def get_current_admin(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    user = db.query(UserAuth).filter(UserAuth.id == user_id).first()
    
    if not user or user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return UserOut.model_validate(user)


# 🔍 VALIDATE (INTERNAL) - FIXED to accept both query param and JSON body
@router.post("/validate")
def validate(
    token: str = None,  # Query parameter: ?token=xxx
    request: dict = None,  # Body parameter: {"token": "xxx"}
    db: Session = Depends(get_db)
):
    """Validate token - accepts either ?token=xxx or JSON body {"token": "xxx"}"""
    
    # Try to get token from body if provided
    if request and "token" in request:
        token = request.get("token")
    
    # If still no token, raise error
    if not token:
        raise HTTPException(status_code=400, detail="Token required")
    
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    user = db.query(UserAuth).filter(UserAuth.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists")

    return {"valid": True, "data": payload, "user": UserOut.model_validate(user)}


# 🚪 LOGOUT
@router.post("/logout")
def logout():
    return {"message": "Logout successful (client should delete token)"}


# Check username availability
@router.get("/check-username/{username}")
def check_username(username: str, db: Session = Depends(get_db)):
    user = db.query(UserAuth).filter(UserAuth.username == username).first()
    return {"available": user is None}


# Check email availability
@router.get("/check-email/{email}")
def check_email(email: str, db: Session = Depends(get_db)):
    user = db.query(UserAuth).filter(UserAuth.email == email).first()
    return {"available": user is None}


# 🛡️ ADMIN SUSPEND/UNSUSPEND USER
@router.patch("/admin/suspend/{user_id}")
def toggle_user_suspension(
    user_id: int, 
    suspend: bool, 
    db: Session = Depends(get_db), 
    admin=Depends(get_current_admin)
):
    user = db.query(UserAuth).filter(UserAuth.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == "ADMIN":
        raise HTTPException(status_code=400, detail="Cannot suspend an admin account")
        
    user.is_suspended = suspend
    db.commit()
    
    status = "suspended" if suspend else "unsuspended"
    return {"message": f"User {status} successfully"}