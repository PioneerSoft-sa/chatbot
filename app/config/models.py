from sqlalchemy import Column, Integer, String, DateTime, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

# Enum for batch status
class BatchStatus(enum.Enum):
    MANUFACTURED = "Manufactured"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"

# Asset Status Enum
class AssetStatus(enum.Enum):
    IN_USE = "In Use"
    UNDER_MAINTENANCE = "Under Maintenance"
    RETIRED = "Retired"

# Maintenance Status Enum
class MaintenanceStatus(enum.Enum):
    REPORTED = "Reported"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"

# Department Model
class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    head_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Relationships
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")
    department_head = relationship("Employee", foreign_keys=[head_id])

# Employee Model
class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    designation = Column(String)
    date_joined = Column(Date, default=func.current_date())
    
    # Relationships
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    created_batches = relationship("Batch", back_populates="creator")
    handled_trackings = relationship("BatchTracking", back_populates="handler")

# Product Model
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    unit_price = Column(Float(10, 2))
    
    # Relationships
    batches = relationship("Batch", back_populates="product")

# Batch Model
class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    batch_code = Column(String, unique=True, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    manufactured_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    created_by = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="batches")
    creator = relationship("Employee", back_populates="created_batches")
    tracking_records = relationship("BatchTracking", back_populates="batch")

# Batch Tracking Model
class BatchTracking(Base):
    __tablename__ = "batch_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    location = Column(String, nullable=False)
    status = Column(Enum(BatchStatus), nullable=False)
    timestamp = Column(DateTime, default=func.now())
    handled_by = Column(Integer, ForeignKey("employees.id"))
    
    # Relationships
    batch = relationship("Batch", back_populates="tracking_records")
    handler = relationship("Employee", back_populates="handled_trackings")
    
class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_tag = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String)
    location = Column(String)
    purchase_date = Column(Date)
    warranty_until = Column(Date)
    assigned_to = Column(Integer, ForeignKey("employees.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    status = Column(Enum(AssetStatus), default=AssetStatus.IN_USE)

    # Relationships
    assigned_employee = relationship("Employee", foreign_keys=[assigned_to])
    department = relationship("Department", foreign_keys=[department_id])
    maintenance_logs = relationship("MaintenanceLog", back_populates="asset")
    vendors = relationship("AssetVendorLink", back_populates="asset")

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    reported_by = Column(Integer, ForeignKey("employees.id"))
    description = Column(String)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.REPORTED)
    assigned_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    assigned_vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    resolved_date = Column(Date)

    # Relationships
    asset = relationship("Asset", back_populates="maintenance_logs")
    reporter = relationship("Employee", foreign_keys=[reported_by])
    assigned_employee = relationship("Employee", foreign_keys=[assigned_employee_id])
    assigned_vendor = relationship("Vendor", foreign_keys=[assigned_vendor_id])

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_person = Column(String)
    email = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String)

    # Relationships
    assets_link = relationship("AssetVendorLink", back_populates="vendor")

class AssetVendorLink(Base):
    __tablename__ = "asset_vendor_link"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    service_type = Column(String)
    last_service_date = Column(Date)

    # Relationships
    asset = relationship("Asset", back_populates="vendors")
    vendor = relationship("Vendor", back_populates="assets_link")
