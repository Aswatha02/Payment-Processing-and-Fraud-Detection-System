from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .rules import evaluate_fraud

router = APIRouter(prefix="/fraud", tags=["Fraud"])

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
async def get_fraud_records():
    # Admin endpoint to list all records
    return {
        "total_records": len(fraud_db),
        "flagged_count": len([r for r in fraud_db if r["status"] == "FLAGGED"]),
        "records": fraud_db
    }

@router.get("/stats/{user_id}")
async def get_user_fraud_stats(user_id: int):
    # Frontend user endpoint for risk stats
    user_records = [r for r in fraud_db if r["user_id"] == user_id]
    flagged_count = len([r for r in user_records if r["status"] == "FLAGGED"])
    
    # Get latest risk score or default to 0
    latest_score = user_records[-1]["risk_score"] if user_records else 0
    
    return {
        "flagged_transactions": flagged_count,
        "current_risk_score": latest_score
    }
