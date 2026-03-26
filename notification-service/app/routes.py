from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Notification
from .schemas import NotificationCreate

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# CREATE NOTIFICATION
@router.post("/")
def send_notification(req: NotificationCreate, db: Session = Depends(get_db)):

    data = req.dict() if hasattr(req, "dict") else req.model_dump()
    notif = Notification(**data)
    db.add(notif)
    db.commit()

    # simulate sending
    print(f"[NOTIFICATION] User {req.user_id}: {req.message}")

    return {"message": "Notification sent"}

# GET USER NOTIFICATIONS
@router.get("/{user_id}")
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.timestamp.desc()).all()
