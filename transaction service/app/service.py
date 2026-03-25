import httpx
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

WALLET_URL = os.getenv("WALLET_SERVICE_URL", "http://localhost:8002")


async def debit_wallet(user_id: int, amount: float):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{WALLET_URL}/wallet/debit",
                json={"user_id": user_id, "amount": amount},
                headers={"Authorization": "system"}
            )
            if response.status_code != 200:
                detail = response.json().get("detail", "Wallet debit failed")
                raise HTTPException(status_code=response.status_code, detail=detail)
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Wallet service unavailable")


async def credit_wallet(user_id: int, amount: float):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{WALLET_URL}/wallet/credit",
                json={"user_id": user_id, "amount": amount},
                headers={"Authorization": "system"}
            )
            if response.status_code != 200:
                detail = response.json().get("detail", "Wallet credit failed")
                raise HTTPException(status_code=response.status_code, detail=detail)
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Wallet service unavailable")


USER_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")

async def get_user_name(user_id: int) -> str:
    """Fetch user name from User Service"""
    if not user_id:
        return "System"
        
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{USER_URL}/users/{user_id}",
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json().get("full_name", f"User {user_id}")
        except Exception:
            pass
            
    return f"User {user_id}"

FRAUD_URL = os.getenv("FRAUD_SERVICE_URL", "http://localhost:8004")

async def check_fraud(user_id: int, amount: float) -> dict:
    """Evaluate fraud risk using Fraud Service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{FRAUD_URL}/fraud/analyze",
                json={"user_id": user_id, "amount": amount},
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            # If fraud service is down, maybe we shouldn't block transactions completely,
            # or maybe we should. Let's return a safe default or log error.
            # Assuming returning APPROVED for now if service is unreachable.
            return {"status": "APPROVED", "risk_score": 0, "reasons": ["Fraud service unreachable"]}
            
    return {"status": "APPROVED", "risk_score": 0, "reasons": ["Default fallback"]}
