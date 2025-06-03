from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils import schemas
from app.config.database import get_db
from app.models import models

router = APIRouter(
    prefix="/batches",
    tags=["batches"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_batches(db: Session = Depends(get_db)):
    batches = db.query(models.Batch).all()
    return batches

@router.post("/")
async def create_batch(batch: schemas.BatchCreate, db: Session = Depends(get_db)):
    new_batch = models.Batch(**batch.model_dump())
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch

@router.get("/{batch_id}")
async def get_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

@router.put("/{batch_id}")
async def update_batch(batch_id: int, batch: schemas.Batch, db: Session = Depends(get_db)):
    db.query(models.Batch).filter(models.Batch.id == batch_id).update(batch.model_dump())
    db.commit()
    updated_batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not updated_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return updated_batch

@router.delete("/{batch_id}")
async def delete_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    db.delete(batch)
    db.commit()
    return {"message": "Batch deleted successfully"}


# ========== batch tracking ==========

@router.get("/{batch_id}/trackings")
async def get_batch_trackings(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch.tracking_records

@router.post("/{batch_id}/trackings")
async def create_batch_tracking(batch_id: int, tracking: schemas.BatchTrackingCreate, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    new_tracking = models.BatchTracking(**tracking.model_dump())
    new_tracking.batch = batch
    db.add(new_tracking)
    db.commit()
    db.refresh(new_tracking)
    return new_tracking

@router.get("/{batch_id}/trackings/{tracking_id}")
async def get_batch_tracking(batch_id: int, tracking_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    tracking = db.query(models.BatchTracking).filter(models.BatchTracking.id == tracking_id).first()
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")
    return tracking

@router.delete("/{batch_id}/trackings/{tracking_id}")
async def delete_batch_tracking(batch_id: int, tracking_id: int, db: Session = Depends(get_db)):
    tracking = db.query(models.BatchTracking).filter(models.BatchTracking.id == tracking_id).first()
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")
    
    db.delete(tracking)
    db.commit()
    return {"message": "Tracking deleted successfully"}