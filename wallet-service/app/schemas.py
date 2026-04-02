from pydantic import BaseModel

class WalletCreate(BaseModel):
    user_id: int

class TransactionRequest(BaseModel):
    user_id: int
    amount: float