# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine
from app import models  # now includes expense models & vendor
from app.routers import auth_router, admin_router, user_router
# <-- changed import for expense router below (import the router object directly)
from app.routers.expense_router import router as expenses_router
from app.config import settings
import os

# Create DB tables (dev only)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(admin_router.router, prefix="/admin", tags=["Admin"])
app.include_router(user_router.router, prefix="/user", tags=["User"])
# use the directly imported router
app.include_router(expenses_router, prefix="/expenses", tags=["Expenses"])

# Ensure uploads folder exists and mount
UPLOADS_DIR = "uploads"
os.makedirs(os.path.join(UPLOADS_DIR, "invoices"), exist_ok=True)
os.makedirs(os.path.join(UPLOADS_DIR, "qrcodes"), exist_ok=True)
os.makedirs(os.path.join(UPLOADS_DIR, "screenshots"), exist_ok=True)

# Expose uploads via /uploads URL (OPTIONAL - useful for previewing files)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

@app.get("/")
def root():
    return {"message": "Backend running successfully!"}
