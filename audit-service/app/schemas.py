from pydantic import BaseModel

class AuditCreate(BaseModel):
    service_name: str
    action: str
    user_id: int | None = None
    details: str | None = None
