from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .database import get_db
from .models import AuditLog
from .schemas import AuditCreate, AuditResponse

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.post("/", response_model=dict)
def create_log(req: AuditCreate, db: Session = Depends(get_db)):
    """Create an audit log entry"""
    log_data = req.model_dump() if hasattr(req, "model_dump") else req.dict()
    log = AuditLog(**log_data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "Log recorded", "id": log.id}

@router.get("/", response_model=List[AuditResponse])
def get_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all audit logs with pagination"""
    query = db.query(AuditLog)
    if service_name:
        query = query.filter(AuditLog.service_name == service_name)
    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/user/{user_id}", response_model=List[AuditResponse])
def get_user_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get audit logs for a specific user"""
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(
        AuditLog.timestamp.desc()
    ).offset(skip).limit(limit).all()
    return logs