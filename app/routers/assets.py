from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import models, schemas
from app.config.database import get_db

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_assets(db: Session = Depends(get_db)):
    return db.query(models.Asset).all()

@router.post("/")
async def create_asset(asset: schemas.AssetCreate, db: Session = Depends(get_db)):
    new_asset = models.Asset(**asset.model_dump())
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    return new_asset

@router.get("/{asset_id}")
async def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.put("/{asset_id}")
async def update_asset(asset_id: int, asset: schemas.Asset, db: Session = Depends(get_db)):
    db.query(models.Asset).filter(models.Asset.id == asset_id).update(asset.model_dump())
    db.commit()
    updated_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not updated_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return updated_asset

@router.delete("/{asset_id}")
async def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db.delete(asset)
    db.commit()
    return {"message": "Asset deleted successfully"}


# ========= Asset Vendor Link ========= #
@router.get("/{asset_id}/vendor")
async def get_asset_vendors(asset_id: int, db: Session = Depends(get_db)):
    links = db.query(models.AssetVendorLink).filter(models.AssetVendorLink.asset_id == asset_id).all()
    return links

@router.post("/{asset_id}/vendor")
async def add_asset_vendor(asset_id: int, link: schemas.AssetVendorLinkCreate, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    vendor = db.query(models.Vendor).filter(models.Vendor.id == link.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Create new link using payload + route param
    new_link = models.AssetVendorLink(
        asset_id=asset_id,
        vendor_id=link.vendor_id,
        service_type=link.service_type,
        last_service_date=link.last_service_date
    )

    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link
