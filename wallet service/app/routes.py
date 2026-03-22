from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from .database import get_db
from .models import Wallet, Ledger
from .schemas import WalletCreate, TransactionRequest, TransferRequest
import httpx
import os

router = APIRouter(prefix="/wallet", tags=["Wallet"])

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")

# ============================================
# HELPER FUNCTIONS
# ============================================

async def validate_user_token(auth: str) -> dict:
    """Validate JWT token and return user data"""
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = auth.replace("Bearer ", "")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/auth/validate",
            json={"token": token}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return response.json().get("data", {})


def check_system_token(auth: str):
    """Validate system token (for internal calls)"""
    if not auth or "system" not in auth.lower():
        raise HTTPException(status_code=403, detail="System access required")


async def check_kyc_status(user_id: int):
    """Verify user has completed KYC"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{USER_SERVICE_URL}/users/{user_id}"
            )
            if response.status_code == 200:
                user_data = response.json()
                kyc_status = user_data.get("kyc_status", "PENDING")
                
                if kyc_status != "VERIFIED":
                    raise HTTPException(
                        status_code=403,
                        detail=f"KYC verification required. Current status: {kyc_status}"
                    )
            else:
                raise HTTPException(status_code=404, detail="User profile not found")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User service unavailable")


# ============================================
# ENDPOINTS
# ============================================

# ✅ CREATE WALLET (SYSTEM - called after user registration)
@router.post("")
async def create_wallet(
    req: WalletCreate,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Create wallet for new user - SYSTEM ONLY"""
    check_system_token(authorization)

    # Check if wallet already exists
    existing = db.query(Wallet).filter(Wallet.user_id == req.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Wallet already exists")

    wallet = Wallet(user_id=req.user_id, balance=0.0)
    db.add(wallet)
    db.commit()

    return {"message": "Wallet created", "wallet_id": wallet.wallet_id}


# ✅ GET WALLET DETAILS
@router.get("/{user_id}")
async def get_wallet(
    user_id: int,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get wallet details - USER ONLY"""
    # Validate token and get user info
    token_data = await validate_user_token(authorization)
    token_user_id = token_data.get("user_id")
    
    # Check ownership
    if token_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return {
        "wallet_id": wallet.wallet_id,
        "user_id": wallet.user_id,
        "balance": wallet.balance
    }


# ✅ GET BALANCE
@router.get("/{user_id}/balance")
async def get_balance(
    user_id: int,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get current balance - USER ONLY"""
    # Validate token and check ownership
    token_data = await validate_user_token(authorization)
    token_user_id = token_data.get("user_id")
    
    if token_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return {"user_id": user_id, "balance": wallet.balance}


# 💰 DEPOSIT MONEY
@router.post("/deposit")
async def deposit(
    req: TransactionRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Deposit money into wallet - USER ONLY"""
    # Validate token and check ownership
    token_data = await validate_user_token(authorization)
    token_user_id = token_data.get("user_id")
    
    if token_user_id != req.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check KYC status before allowing deposit
    await check_kyc_status(req.user_id)
    
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    wallet = db.query(Wallet).filter(Wallet.user_id == req.user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Update balance
    old_balance = wallet.balance
    wallet.balance += req.amount
    
    # Record transaction
    ledger = Ledger(
        wallet_id=wallet.wallet_id,
        type="credit",
        amount=req.amount,
        balance_before=old_balance,
        balance_after=wallet.balance
    )
    db.add(ledger)
    db.commit()

    return {
        "message": "Deposit successful",
        "balance": wallet.balance,
        "amount": req.amount
    }


# 💸 WITHDRAW MONEY
@router.post("/withdraw")
async def withdraw(
    req: TransactionRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Withdraw money from wallet - USER ONLY"""
    # Validate token and check ownership
    token_data = await validate_user_token(authorization)
    token_user_id = token_data.get("user_id")
    
    if token_user_id != req.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check KYC status before allowing withdrawal
    await check_kyc_status(req.user_id)
    
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    wallet = db.query(Wallet).filter(Wallet.user_id == req.user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Update balance
    old_balance = wallet.balance
    wallet.balance -= req.amount
    
    # Record transaction
    ledger = Ledger(
        wallet_id=wallet.wallet_id,
        type="debit",
        amount=req.amount,
        balance_before=old_balance,
        balance_after=wallet.balance
    )
    db.add(ledger)
    db.commit()

    return {
        "message": "Withdrawal successful",
        "balance": wallet.balance,
        "amount": req.amount
    }


# 💸 TRANSFER MONEY (P2P)
@router.post("/transfer")
async def transfer(
    req: TransferRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Transfer money to another user (P2P)"""
    token_data = await validate_user_token(authorization)
    token_user_id = token_data.get("user_id")
    
    if token_user_id != req.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if req.user_id == req.recipient_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to self")
        
    await check_kyc_status(req.user_id)
    
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # Lock rows in deterministic order to prevent deadlocks
    user_ids = sorted([req.user_id, req.recipient_id])
    wallets = db.query(Wallet).filter(Wallet.user_id.in_(user_ids)).with_for_update().all()
    
    if len(wallets) != 2:
        raise HTTPException(status_code=404, detail="One or both wallets not found")
        
    sender_wallet = next((w for w in wallets if w.user_id == req.user_id), None)
    receiver_wallet = next((w for w in wallets if w.user_id == req.recipient_id), None)

    if sender_wallet.balance < req.amount:
        # Rollback the lock simply implicitly by raising
        raise HTTPException(status_code=400, detail="Insufficient balance")

    sender_old_balance = sender_wallet.balance
    receiver_old_balance = receiver_wallet.balance

    sender_wallet.balance -= req.amount
    receiver_wallet.balance += req.amount
    
    # Record sender ledger
    ledger_debit = Ledger(
        wallet_id=sender_wallet.wallet_id,
        type="debit",
        amount=req.amount,
        balance_before=sender_old_balance,
        balance_after=sender_wallet.balance,
        description=f"Transfer to user {req.recipient_id}"
    )
    
    # Record receiver ledger
    ledger_credit = Ledger(
        wallet_id=receiver_wallet.wallet_id,
        type="credit",
        amount=req.amount,
        balance_before=receiver_old_balance,
        balance_after=receiver_wallet.balance,
        description=f"Transfer from user {req.user_id}"
    )
    
    db.add_all([ledger_debit, ledger_credit])
    db.commit()

    return {
        "message": "Transfer successful",
        "balance": sender_wallet.balance,
        "amount": req.amount,
        "recipient_id": req.recipient_id
    }






# 📊 GET TRANSACTION HISTORY
@router.get("/{user_id}/transactions")
async def get_transactions(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get transaction history - USER ONLY"""
    token_data = await validate_user_token(authorization)
    token_user_id = token_data.get("user_id")
    
    if token_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    transactions = db.query(Ledger)\
        .filter(Ledger.wallet_id == wallet.wallet_id)\
        .order_by(Ledger.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "transactions": transactions,
        "total": db.query(Ledger).filter(Ledger.wallet_id == wallet.wallet_id).count(),
        "skip": skip,
        "limit": limit
    }


# ✅ HEALTH CHECK
@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "wallet-service"}