from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import models, schemas
from app.config.database import get_db

router = APIRouter(
    prefix="/maintenance",
    tags=["maintenance"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_maintenance(db: Session = Depends(get_db)):
    return db.query(models.MaintenanceLog).all()

@router.post("/")
async def create_maintenance(maintenance: schemas.MaintenanceLogCreate, db: Session = Depends(get_db)):
    new_maintenance = models.MaintenanceLog(**maintenance.model_dump())
    db.add(new_maintenance)
    db.commit()
    db.refresh(new_maintenance)
    return new_maintenance

@router.get("/{maintenance_id}")
async def get_maintenance(maintenance_id: int, db: Session = Depends(get_db)):
    maintenance = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.id == maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance not found")
    return maintenance

@router.put("/{maintenance_id}")
async def update_maintenance(maintenance_id: int, maintenance: schemas.MaintenanceLog, db: Session = Depends(get_db)):
    db.query(models.MaintenanceLog).filter(models.MaintenanceLog.id == maintenance_id).update(maintenance.model_dump())
    db.commit()
    updated_maintenance = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.id == maintenance_id).first()
    if not updated_maintenance:
        raise HTTPException(status_code=404, detail="Maintenance not found")
    return updated_maintenance