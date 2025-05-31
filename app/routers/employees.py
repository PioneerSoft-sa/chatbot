from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import models, schemas
from app.config.database import get_db

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_employees(db: Session = Depends(get_db)):
    employees = db.query(models.Employee).all()
    return employees

@router.get("/{employee_id}")
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.post("/")
async def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    new_employee = models.Employee(**employee.model_dump())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@router.put("/{employee_id}")
async def update_employee(employee_id: int, employee: schemas.Employee, db: Session = Depends(get_db)):
    db.query(models.Employee).filter(models.Employee.id == employee_id).update(employee.model_dump())
    db.commit()
    updated_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not updated_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated_employee