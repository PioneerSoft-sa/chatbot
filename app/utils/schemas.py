from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

# ======== Schema for Employee ========= #
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

# ========= Schema for Department ========= #
class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    head_id: Optional[int] = None

class Department(DepartmentBase):
    id: int
    head_id: Optional[int]
    
    class Config:
        from_attributes = True

# ========= Schema for Product ========= #
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

# ========= Schema for Batch ========= #
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

# ========= Schema for Batch Tracking ========= #
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
        
# ========= Schema for Asset ========= #
class AssetBase(BaseModel):
    asset_tag: str
    name: str
    category: Optional[str] = None
    location: Optional[str] = None
    purchase_date: Optional[date] = None
    warranty_until: Optional[date] = None
    assigned_to: Optional[int] = None
    department_id: Optional[int] = None
    status: Optional[str] = "IN_USE"

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int

    class Config:
        from_attributes = True
        
# ========= Schema for Maintenance Log ========= #
class MaintenanceLogBase(BaseModel):
    asset_id: int
    reported_by: int
    description: str
    status: Optional[str] = "REPORTED"
    assigned_employee_id: Optional[int] = None
    assigned_vendor_id: Optional[int] = None
    resolved_date: Optional[date] = None

class MaintenanceLogCreate(MaintenanceLogBase):
    pass

class MaintenanceLog(MaintenanceLogBase):
    id: int

    class Config:
        from_attributes = True

# ========= Schema for Vendor ========= #
class VendorBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int

    class Config:
        from_attributes = True
        
# ========= Schema for AssetVendorLink ========= #
class AssetVendorLinkBase(BaseModel):
    asset_id: int
    vendor_id: int
    service_type: Optional[str] = None
    last_service_date: Optional[date] = None

class AssetVendorLinkCreate(AssetVendorLinkBase):
    pass

class AssetVendorLink(AssetVendorLinkBase):
    id: int

    class Config:
        from_attributes = True

# ========= Schema for Chat ========= #
class ChatQuery(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    batch_info: Optional[dict] = None