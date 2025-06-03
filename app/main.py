from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.models import models
from app.config.database import engine
from app.routers import departments, employees, products, batches, assets, maintenance, vendors, chat

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI()

# Define allowed origins
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # Add other allowed origins as needed
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(departments.router)
app.include_router(employees.router)
app.include_router(products.router)
app.include_router(batches.router)
app.include_router(assets.router)
app.include_router(maintenance.router)
app.include_router(vendors.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"message": "Hello World!"}