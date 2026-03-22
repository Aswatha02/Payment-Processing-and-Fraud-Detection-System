from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from .database import get_db
from .models import Transaction, Wallet, Ledger
from .schemas import TransferRequest
from .service import debit_wallet, credit_wallet, get_user_name
import httpx
import os

router = APIRouter(prefix="/transactions", tags=["Transactions"])

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

async def validate_user_token(auth: str) -> dict:
    """Validate JWT token and return user data"""
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = auth.replace("Bearer ", "")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/auth/validate",
                json={"token": token}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            return response.json().get("data", {})
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service unavailable")


@router.post("/transfer")
async def transfer_money(
    req: TransferRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Transfer money to another user"""
    token_data = await validate_user_token(authorization)
    token_user_id = token_data.get("user_id")
    
    if token_user_id != req.sender_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if req.sender_id == req.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to self")
        
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # Start the transaction process
    transaction = Transaction(
        sender_id=req.sender_id,
        receiver_id=req.receiver_id,
        amount=req.amount,
        status="PENDING"
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    try:
        # Debit sender wallet
        await debit_wallet(req.sender_id, req.amount)
    except HTTPException as e:
        transaction.status = "FAILED"
        db.commit()
        raise e

    try:
        # Credit receiver wallet
        await credit_wallet(req.receiver_id, req.amount)
    except Exception as e:
        # Try rollback
        await credit_wallet(req.sender_id, req.amount) 
        transaction.status = "FAILED_AT_CREDIT"
        db.commit()
        raise HTTPException(status_code=500, detail="Transfer failed at credit, rollback initiated")

    transaction.status = "COMPLETED"
    db.commit()

    return {
        "message": "Transfer successful",
        "transaction_id": transaction.id,
        "amount": req.amount,
        "receiver_id": req.receiver_id
    }


@router.get("/{user_id}/history")
async def get_transaction_history(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get unified transaction history for a user"""
    token_data = await validate_user_token(authorization)
    token_user_id = token_data.get("user_id")
    
    if token_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    names_cache = {}
    async def resolve_name(uid: int):
        if not uid:
            return "System"
        if uid not in names_cache:
            names_cache[uid] = await get_user_name(uid)
        return names_cache[uid]
    
    # 1. Fetch P2P Transactions
    txs = db.query(Transaction)\
        .filter((Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id))\
        .all()
        
    unified_history = []
    
    for t in txs:
        unified_history.append({
            "id": f"tx_{t.id}",
            "type": "transfer",
            "amount": t.amount,
            "status": t.status,
            "timestamp": t.timestamp,
            "sender_id": t.sender_id,
            "receiver_id": t.receiver_id,
            "sender_name": await resolve_name(t.sender_id),
            "receiver_name": await resolve_name(t.receiver_id)
        })
        
    # 2. Fetch non-system Ledger items (deposits / withdrawals)
    user_wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if user_wallet:
        ledgers = db.query(Ledger)\
            .filter(Ledger.wallet_id == user_wallet.wallet_id, Ledger.source != "system")\
            .all()
            
        current_name = await resolve_name(user_id)
        
        for l in ledgers:
            # For deposits: sender is System, receiver is User
            # For withdrawals: sender is User, receiver is System
            is_credit = l.type == "credit"
            s_id = None if is_credit else user_id
            r_id = user_id if is_credit else None
            
            unified_history.append({
                "id": f"lg_{l.id}",
                "type": l.type, # 'credit' / 'debit'
                "amount": l.amount,
                "status": "COMPLETED",
                "timestamp": l.timestamp,
                "sender_id": s_id,
                "receiver_id": r_id,
                "sender_name": "System" if is_credit else current_name,
                "receiver_name": current_name if is_credit else "System",
                "description": l.description
            })
            
    # Sort unified history descending by timestamp
    unified_history.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Paginate
    total = len(unified_history)
    paginated = unified_history[skip : skip + limit]
    
    return {
        "transactions": paginated,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "transaction-service"}
