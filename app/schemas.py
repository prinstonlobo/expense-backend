# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# request
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class AdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

# response
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    approved: bool
    role: str
    created_at: datetime

    class Config:
        orm_mode = True

class AdminOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True
