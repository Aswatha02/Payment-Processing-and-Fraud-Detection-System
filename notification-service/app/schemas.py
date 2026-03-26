from pydantic import BaseModel

class NotificationCreate(BaseModel):
    user_id: int
    message: str
    type: str
