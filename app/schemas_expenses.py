# app/schemas_expenses.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class ExpenseCreate(BaseModel):
    company_name: str
    gst_number: Optional[str] = None
    expense_type: str  # "Purchase" or "Others"
    date: date
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_amount: Optional[str] = None
    purpose: Optional[str] = None
    purchased_by: Optional[str] = None

    amount_paid_by: Optional[str] = None
    payment_type: Optional[str] = None  # "Cash" or "UPI"
    amount_paid: Optional[str] = None

class ExpenseOut(BaseModel):
    id: int
    company_name: str
    gst_number: Optional[str]
    expense_type: str
    expense_type_flag: int

    date: date
    invoice_number: Optional[str]
    vendor_name: Optional[str]
    invoice_amount: Optional[str]
    purpose: Optional[str]
    purchased_by: Optional[str]

    invoice_copy: Optional[str]
    qrcode: Optional[str]

    amount_paid_by: Optional[str]
    payment_type: Optional[str]
    payment_type_flag: Optional[int]
    amount_paid: Optional[str]
    payment_screenshot: Optional[str]
    
    submitted_by: Optional[str]
    status: Optional[str]

    created_at: datetime

    class Config:
        orm_mode = True

class VendorCreate(BaseModel):
    name: str

class VendorOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        orm_mode = True
