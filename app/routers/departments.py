from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils import schemas
from app.config.database import get_db
from app.models import models

router = APIRouter(
    prefix="/departments",
    tags=["departments"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_departments(db: Session = Depends(get_db)):
    departments = db.query(models.Department).all()
    return departments

@router.get("/{department_id}")
async def get_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@router.post("/", response_model=schemas.Department)
async def create_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    new_department = models.Department(**department.model_dump())
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    return new_department

@router.put("/{department_id}", response_model=schemas.Department)
async def update_department(
    department_id: int, 
    department: schemas.Department,
    db: Session = Depends(get_db)
):
    db_department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    for key, value in department.model_dump().items():
        setattr(db_department, key, value)
    
    db.commit()
    db.refresh(db_department)
    return db_department

@router.delete("/{department_id}")
async def delete_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db.delete(department)
    db.commit()
    return {"message": "Department deleted successfully"}