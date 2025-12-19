# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from urllib.parse import quote_plus
from app.config import settings

# Build DB URL for PyMySQL driver
username = settings.DB_USER
password = quote_plus(settings.DB_PASS)  # escape special chars
host = settings.DB_HOST
port = settings.DB_PORT
db = settings.DB_NAME

DATABASE_URL = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()