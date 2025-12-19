# app/crud.py
from sqlalchemy.orm import Session
from app import models
from typing import Optional, List

# -----------------------------
# User & Admin CRUD (existing)
# -----------------------------
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, username: str, email: str, password_hash: str) -> models.User:
    user = models.User(username=username, email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()

def approve_user(db: Session, user_id: int) -> bool:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return False
    user.approved = True
    db.commit()
    return True

def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True

# Admin helpers
def get_admin_by_email(db: Session, email: str) -> Optional[models.Admin]:
    return db.query(models.Admin).filter(models.Admin.email == email).first()

def create_admin(db: Session, username: str, email: str, password_hash: str) -> models.Admin:
    admin = models.Admin(username=username, email=email, password_hash=password_hash)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

# -----------------------------
# Vendor & Expense CRUD (new)
# -----------------------------
# vendor CRUD
def get_all_vendors(db: Session) -> List[models.Vendor]:
    return db.query(models.Vendor).order_by(models.Vendor.name).all()

def get_vendor_by_name(db: Session, name: str) -> Optional[models.Vendor]:
    return db.query(models.Vendor).filter(models.Vendor.name == name).first()

def create_vendor(db: Session, name: str) -> models.Vendor:
    v = models.Vendor(name=name)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v

# helper: map company string to model class
_company_model_map = {
    "Thinksonic Global Solutions Pvt Ltd": models.ExpenseThinksonic,
    "Thinkmachines Industries & Automation Pvt Ltd": models.ExpenseThinkmachines,
    "Thinkplast Integrated Molding & Engineering Pvt Ltd": models.ExpenseThinkplast,
}

def get_model_for_company(company_name: str):
    return _company_model_map.get(company_name)

# Expense CRUD across the three tables
def create_expense(db: Session, company_name: str, payload: dict):
    Model = get_model_for_company(company_name)
    if not Model:
        raise ValueError("Unknown company")

    # ensure status is set: use provided payload status if present, else default to "Pending"
    payload.setdefault("status", "Pending")

    inst = Model(**payload)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst

def list_expenses_for_company(db: Session, company_name: str, limit: int = 100, skip: int = 0):
    Model = get_model_for_company(company_name)
    if not Model:
        return []
    return db.query(Model).order_by(Model.created_at.desc()).offset(skip).limit(limit).all()

def get_expense(db: Session, company_name: str, expense_id: int):
    Model = get_model_for_company(company_name)
    if not Model:
        return None
    return db.query(Model).filter(Model.id == expense_id).first()

def update_expense(db: Session, company_name: str, expense_id: int, changes: dict):
    Model = get_model_for_company(company_name)
    if not Model:
        return None
    inst = db.query(Model).filter(Model.id == expense_id).first()
    if not inst:
        return None
    for k, v in changes.items():
        setattr(inst, k, v)
    db.commit()
    db.refresh(inst)
    return inst

def delete_expense(db: Session, company_name: str, expense_id: int) -> bool:
    Model = get_model_for_company(company_name)
    if not Model:
        return False
    inst = db.query(Model).filter(Model.id == expense_id).first()
    if not inst:
        return False
    db.delete(inst)
    db.commit()
    return True
