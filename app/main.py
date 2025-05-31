from fastapi import FastAPI
import os
from dotenv import load_dotenv

from .config import models
from .config.database import engine

from .routers import departments, employees, products

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI()

# Include routers
app.include_router(departments.router)
app.include_router(employees.router)
app.include_router(products.router)

@app.get("/")
def read_root():
    return {"message": "Hello World!"}