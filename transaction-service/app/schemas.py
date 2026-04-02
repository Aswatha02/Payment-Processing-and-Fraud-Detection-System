from pydantic import BaseModel

class TransferRequest(BaseModel):
    sender_id: int
    receiver_id: int
    amount: float
