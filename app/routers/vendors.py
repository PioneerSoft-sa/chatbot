from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils import schemas
from app.config.database import get_db
from app.models import models

router = APIRouter(
    prefix="/vendors",
    tags=["vendors"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_vendors(db: Session = Depends(get_db)):
    return db.query(models.Vendor).all()

@router.post("/")
async def create_vendor(vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    new_vendor = models.Vendor(**vendor.model_dump())
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return new_vendor

@router.get("/{vendor_id}")
async def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

@router.put("/{vendor_id}")
async def update_vendor(vendor_id: int, vendor: schemas.Vendor, db: Session = Depends(get_db)):
    db.query(models.Vendor).filter(models.Vendor.id == vendor_id).update(vendor.model_dump())
    db.commit()
    updated_vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if not updated_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return updated_vendor

@router.delete("/{vendor_id}")
async def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    db.delete(vendor)
    db.commit()
    return {"message": "Vendor deleted successfully"}

