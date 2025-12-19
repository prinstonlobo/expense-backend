# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Date
from app.database import Base

class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    approved = Column(Boolean, default=False, nullable=False)
    role = Column(String(50), default="user", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Vendors & Company-specific Expense Tables ---
class Vendor(Base):
    __tablename__ = "vendor"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ExpenseThinksonic(Base):
    __tablename__ = "expense_thinksonic"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    gst_number = Column(String(64), nullable=True)

    expense_type = Column(String(20), nullable=False)  # "Purchase" / "Others"
    expense_type_flag = Column(Integer, nullable=False, default=0)  # 0 -> Purchase, 1 -> Others

    date = Column(Date, nullable=False)
    invoice_number = Column(String(128), nullable=True)
    vendor_name = Column(String(200), nullable=True)
    invoice_amount = Column(String(50), nullable=True)
    purpose = Column(String(255), nullable=True)
    purchased_by = Column(String(150), nullable=True)

    invoice_copy = Column(String(1024), nullable=True)
    qrcode = Column(String(1024), nullable=True)

    amount_paid_by = Column(String(150), nullable=True)
    payment_type = Column(String(20), nullable=True)    # "Cash"/"UPI"
    payment_type_flag = Column(Integer, nullable=True)  # 0 -> Cash, 1 -> UPI
    amount_paid = Column(String(50), nullable=True)
    payment_screenshot = Column(String(1024), nullable=True)
    submitted_by = Column(String(150), nullable=True)  # username who submitted / last updated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="Pending")


class ExpenseThinkmachines(Base):
    __tablename__ = "expense_thinkmachines"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    gst_number = Column(String(64), nullable=True)

    expense_type = Column(String(20), nullable=False)
    expense_type_flag = Column(Integer, nullable=False, default=0)

    date = Column(Date, nullable=False)
    invoice_number = Column(String(128), nullable=True)
    vendor_name = Column(String(200), nullable=True)
    invoice_amount = Column(String(50), nullable=True)
    purpose = Column(String(255), nullable=True)
    purchased_by = Column(String(150), nullable=True)

    invoice_copy = Column(String(1024), nullable=True)
    qrcode = Column(String(1024), nullable=True)

    amount_paid_by = Column(String(150), nullable=True)
    payment_type = Column(String(20), nullable=True)
    payment_type_flag = Column(Integer, nullable=True)
    amount_paid = Column(String(50), nullable=True)
    payment_screenshot = Column(String(1024), nullable=True)
    submitted_by = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="Pending")


class ExpenseThinkplast(Base):
    __tablename__ = "expense_thinkplast"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    gst_number = Column(String(64), nullable=True)

    expense_type = Column(String(20), nullable=False)
    expense_type_flag = Column(Integer, nullable=False, default=0)

    date = Column(Date, nullable=False)
    invoice_number = Column(String(128), nullable=True)
    vendor_name = Column(String(200), nullable=True)
    invoice_amount = Column(String(50), nullable=True)
    purpose = Column(String(255), nullable=True)
    purchased_by = Column(String(150), nullable=True)

    invoice_copy = Column(String(1024), nullable=True)
    qrcode = Column(String(1024), nullable=True)

    amount_paid_by = Column(String(150), nullable=True)
    payment_type = Column(String(20), nullable=True)
    payment_type_flag = Column(Integer, nullable=True)
    amount_paid = Column(String(50), nullable=True)
    payment_screenshot = Column(String(1024), nullable=True)
    submitted_by = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  
    status = Column(String(50), default="Pending")
 
