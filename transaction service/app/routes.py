from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks
from sqlalchemy.orm import Session
from .database import get_db
from .models import Transaction, Wallet, Ledger
from .schemas import TransferRequest
from .service import debit_wallet, credit_wallet, get_user_name, check_fraud
from .audit import log_audit
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
    background_tasks: BackgroundTasks,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Transfer money to another user"""
    token_data = await validate_user_token(authorization)
    token_user_id = token_data.get("user_id")
    token_role = token_data.get("role", "USER")
    
    if token_role == "ADMIN":
        raise HTTPException(status_code=403, detail="Admins cannot perform transactions")
        
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

    # Check for fraud
    fraud_result = await check_fraud(req.sender_id, req.amount)
    if fraud_result.get("status") == "FLAGGED":
        transaction.status = "FLAGGED"
        db.commit()
        background_tasks.add_task(log_audit, "Transaction Service", "Transaction Flagged", req.sender_id, f"Transfer of {req.amount} to {req.receiver_id} flagged for fraud")
        raise HTTPException(status_code=400, detail="Transaction flagged for suspicious activity")

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

    background_tasks.add_task(log_audit, "Transaction Service", "Transaction Completed", req.sender_id, f"Transferred {req.amount} to {req.receiver_id} (TX ID: {transaction.id})")

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
        # Hide FLAGGED transactions from regular users
        if t.status == "FLAGGED" and token_data.get("role") != "ADMIN":
            continue
            
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

@router.get("/{user_id}/dashboard")
async def get_user_dashboard(
    user_id: int,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get dashboard stats for a user"""
    token_data = await validate_user_token(authorization)
    token_user_id = token_data.get("user_id")
    
    if token_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    if token_data.get("role") == "ADMIN":
        raise HTTPException(status_code=403, detail="Admins do not have financial dashboards")

    # Fetch total transactions (excluding FLAGGED)
    total_txs = db.query(Transaction).filter(
        ((Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id)),
        Transaction.status != "FLAGGED"
    ).count()

    # Fetch successful transactions
    success_txs = db.query(Transaction).filter(
        ((Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id)),
        Transaction.status == "COMPLETED"
    ).count()
    
    # Let's get balance from Wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    balance = wallet.balance if wallet else 0

    return {
        "total_transactions": total_txs,
        "successful_transactions": success_txs,
        "wallet_balance": balance
    }

@router.get("/admin/flagged")
async def get_flagged_transactions(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all flagged transactions for admins"""
    token_data = await validate_user_token(authorization)
    
    if token_data.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")

    txs = db.query(Transaction).filter(Transaction.status == "FLAGGED").order_by(Transaction.timestamp.desc()).all()
    
    result = []
    for t in txs:
        result.append({
            "id": t.id,
            "amount": t.amount,
            "status": t.status,
            "timestamp": t.timestamp,
            "sender_id": t.sender_id,
            "receiver_id": t.receiver_id
        })
        
    return {"transactions": result}


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "transaction-service"}
