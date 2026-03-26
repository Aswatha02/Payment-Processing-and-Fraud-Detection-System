from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import AuditLog
from .schemas import AuditCreate

router = APIRouter(prefix="/audit", tags=["Audit"])

# CREATE LOG
@router.post("/")
def create_log(req: AuditCreate, db: Session = Depends(get_db)):
    # req.model_dump() for pydantic v2, dict() for v1
    # assuming v1/v2 compatibility
    log_data = req.dict() if hasattr(req, "dict") else req.model_dump()
    log = AuditLog(**log_data)
    db.add(log)
    db.commit()
    return {"message": "Log recorded"}

# GET ALL LOGS
@router.get("/")
def get_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

# GET BY USER
@router.get("/{user_id}")
def get_user_logs(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(AuditLog).filter(AuditLog.user_id == user_id).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
