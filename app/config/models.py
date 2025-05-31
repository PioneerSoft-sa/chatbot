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