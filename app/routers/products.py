from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import models, schemas
from app.config.database import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/")
async def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products

@router.post("/")
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.put("/{product_id}")
async def update_product(product_id: int, product: schemas.Product, db: Session = Depends(get_db)):
    db.query(models.Product).filter(models.Product.id == product_id).update(product.model_dump())
    db.commit()
    updated_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}