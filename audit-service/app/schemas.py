from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuditCreate(BaseModel):
    service_name: str
    action: str
    user_id: Optional[int] = None
    details: Optional[str] = None

class AuditResponse(AuditCreate):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True