from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import httpx
import os
from .rules import evaluate_fraud

router = APIRouter(prefix="/fraud", tags=["Fraud"])

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

async def validate_admin_token(authorization: str = Header(...)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/auth/validate",
                json={"token": token}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            data = response.json().get("data", {})
            if data.get("role") != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
                
            return data
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

class FraudRequest(BaseModel):
    user_id: int
    amount: float

class FraudRecord(BaseModel):
    id: str
    user_id: int
    amount: float
    risk_score: int
    status: str
    reasons: List[str]
    timestamp: datetime

# In-memory storage for fraud records mapping
fraud_db = []

@router.post("/analyze")
async def analyze_fraud(req: FraudRequest):
    # Evaluate risk
    result = evaluate_fraud(req.user_id, req.amount)
    
    # Store record
    record = FraudRecord(
        id=f"frd_{len(fraud_db) + 1}",
        user_id=req.user_id,
        amount=req.amount,
        risk_score=result["risk_score"],
        status=result["status"],
        reasons=result["reasons"],
        timestamp=datetime.utcnow()
    )
    fraud_db.append(record.dict())
    
    return result

@router.get("/")
async def get_fraud_records(admin_data: dict = Depends(validate_admin_token)):
    # Admin endpoint to list all records
    return {
        "total_records": len(fraud_db),
        "flagged_count": len([r for r in fraud_db if r["status"] == "FLAGGED"]),
        "records": fraud_db
    }

@router.get("/stats/{user_id}")
async def get_user_fraud_stats(user_id: int, admin_data: dict = Depends(validate_admin_token)):
    # Admin endpoint for risk stats for a specific user
    user_records = [r for r in fraud_db if r["user_id"] == user_id]
    flagged_count = len([r for r in user_records if r["status"] == "FLAGGED"])
    
    # Get latest risk score or default to 0
    latest_score = user_records[-1]["risk_score"] if user_records else 0
    
    return {
        "flagged_transactions": flagged_count,
        "current_risk_score": latest_score
    }
