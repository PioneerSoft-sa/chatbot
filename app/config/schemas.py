from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

# Base schemas
class EmployeeBase(BaseModel):
    name: str
    email: str
    designation: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    department_id: Optional[int] = None

class Employee(EmployeeBase):
    id: int
    department_id: Optional[int]
    date_joined: date
    
    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    head_id: Optional[int] = None

class Department(DepartmentBase):
    id: int
    head_id: Optional[int]
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    category: Optional[str] = None
    unit_price: Optional[Decimal] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    
    class Config:
        from_attributes = True

class BatchBase(BaseModel):
    batch_code: str
    quantity: int
    manufactured_date: date
    expiry_date: Optional[date] = None

class BatchCreate(BatchBase):
    product_id: int
    created_by: int

class Batch(BatchBase):
    id: int
    product_id: int
    created_by: int
    created_at: datetime
    product: Product
    
    class Config:
        from_attributes = True

class BatchTrackingBase(BaseModel):
    location: str
    status: str

class BatchTrackingCreate(BatchTrackingBase):
    batch_id: int
    handled_by: int

class BatchTracking(BatchTrackingBase):
    id: int
    batch_id: int
    timestamp: datetime
    handled_by: int
    
    class Config:
        from_attributes = True

# Query schemas
class ChatQuery(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    batch_info: Optional[dict] = None