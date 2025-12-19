# app/routers/expense_router.py
import os
import traceback
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

# define router early so it's present even if later imports throw
router = APIRouter(tags=["expenses"])

# --- safe imports (wrapped for clearer error messages) ---
try:
    from app.deps import get_db, get_current_user
    from app import crud
    from app import schemas_expenses
except Exception:
    # print a friendly import-time traceback and re-raise so the console shows the real error
    print("Error importing dependencies for expense_router.py:")
    traceback.print_exc()
    raise

# configure upload dirs
BASE_UPLOAD_DIR = "uploads"
INVOICE_DIR = os.path.join(BASE_UPLOAD_DIR, "invoices")
QRCODE_DIR = os.path.join(BASE_UPLOAD_DIR, "qrcodes")
SCREENSHOT_DIR = os.path.join(BASE_UPLOAD_DIR, "screenshots")

for d in (INVOICE_DIR, QRCODE_DIR, SCREENSHOT_DIR):
    os.makedirs(d, exist_ok=True)


def save_upload_file(upload_file: UploadFile, folder: str) -> Optional[str]:
    if not upload_file:
        return None
    filename = getattr(upload_file, "filename", None)
    if not filename:
        return None
    ext = os.path.splitext(filename)[1]
    safe_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{os.urandom(6).hex()}{ext}"
    dest = os.path.join(folder, safe_name)
    # make sure parent folder exists
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    # read and write safely
    content = upload_file.file.read()
    with open(dest, "wb") as f:
        f.write(content)
    return dest  # you can change to store relative paths if you prefer


# CREATE EXPENSE - accepts form-data, files optional
@router.post("/create", response_model=schemas_expenses.ExpenseOut)
async def create_expense(
    company_name: str = Form(...),
    gst_number: str = Form(None),
    expense_type: str = Form(...),  # "Purchase" or "Others"
    date: str = Form(...),  # expect YYYY-MM-DD or DD-MM-YYYY
    invoice_number: Optional[str] = Form(None),
    vendor_name: Optional[str] = Form(None),
    invoice_amount: Optional[str] = Form(None),
    purpose: Optional[str] = Form(None),
    purchased_by: Optional[str] = Form(None),

    amount_paid_by: Optional[str] = Form(None),
    payment_type: Optional[str] = Form(None),  # "Cash" or "UPI"
    amount_paid: Optional[str] = Form(None),

    # NEW: accept optional status from client (Completed/Pending)
    status: Optional[str] = Form(None),

    invoice_copy: Optional[UploadFile] = File(None),
    qrcode: Optional[UploadFile] = File(None),
    payment_screenshot: Optional[UploadFile] = File(None),

    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    
):
    # validate company model mapping
    Model = crud.get_model_for_company(company_name)
    if not Model:
        raise HTTPException(status_code=400, detail="Unknown company")

    # expense_type flag logic
    if expense_type and expense_type.lower() == "purchase":
        expense_flag = 0
        expense_type_clean = "Purchase"
    else:
        expense_flag = 1
        expense_type_clean = "Others"

    # payment_type flag logic
    if payment_type and payment_type.lower() == "cash":
        pay_flag = 0
        payment_type_clean = "Cash"
    elif payment_type and payment_type.lower() == "upi":
        pay_flag = 1
        payment_type_clean = "UPI"
    else:
        pay_flag = None
        payment_type_clean = None

    # parse date (try ISO then dd-mm-yyyy)
    try:
        dt = datetime.fromisoformat(date).date()
    except Exception:
        try:
            dt = datetime.strptime(date, "%d-%m-%Y").date()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD or DD-MM-YYYY")

    invoice_path = save_upload_file(invoice_copy, INVOICE_DIR) if invoice_copy else None
    qrcode_path = save_upload_file(qrcode, QRCODE_DIR) if qrcode else None
    screenshot_path = save_upload_file(payment_screenshot, SCREENSHOT_DIR) if payment_screenshot else None

    submitted_by = getattr(current_user, "username", None)

    payload = {
        "company_name": company_name,
        "gst_number": gst_number,
        "expense_type": expense_type_clean,
        "expense_type_flag": expense_flag,
        "date": dt,
        "invoice_number": invoice_number,
        "vendor_name": vendor_name,
        "invoice_amount": invoice_amount,
        "purpose": purpose,
        "purchased_by": purchased_by,
        "invoice_copy": invoice_path,
        "qrcode": qrcode_path,
        "amount_paid_by": amount_paid_by,
        "payment_type": payment_type_clean,
        "payment_type_flag": pay_flag,
        "amount_paid": amount_paid,
        "payment_screenshot": screenshot_path,
        "submitted_by": submitted_by,
    }

    # Only set status if client provided it (otherwise leave to CRUD default)
    if status is not None:
        payload["status"] = status

    inst = crud.create_expense(db, company_name, payload)
    return inst


# LIST EXPENSES FOR COMPANY
@router.get("/company/{company_name}", response_model=List[schemas_expenses.ExpenseOut])
def list_company_expenses(
    company_name: str,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    insts = crud.list_expenses_for_company(db, company_name, limit=limit, skip=skip)
    return insts


# GET single expense
@router.get("/{company_name}/{expense_id}", response_model=schemas_expenses.ExpenseOut)
def get_expense_detail(company_name: str, expense_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    inst = crud.get_expense(db, company_name, expense_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Expense not found")
    return inst


# UPDATE expense - Admin only
@router.put("/{company_name}/{expense_id}", response_model=schemas_expenses.ExpenseOut)
async def update_expense(
    company_name: str,
    expense_id: int,
    expense_type: Optional[str] = Form(None),
    gst_number: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    invoice_number: Optional[str] = Form(None),
    vendor_name: Optional[str] = Form(None),
    invoice_amount: Optional[str] = Form(None),
    purpose: Optional[str] = Form(None),
    purchased_by: Optional[str] = Form(None),

    amount_paid_by: Optional[str] = Form(None),
    payment_type: Optional[str] = Form(None),  # "Cash" or "UPI"
    amount_paid: Optional[str] = Form(None),

    invoice_copy: Optional[UploadFile] = File(None),
    qrcode: Optional[UploadFile] = File(None),
    payment_screenshot: Optional[UploadFile] = File(None),
    allOk: Optional[bool] = Form(None),
    status: Optional[str] = Form(None),


    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Admin check - your project treats Admin as a separate model; verify accordingly
    # We'll check for presence of 'approved' attribute (users have it) — if present -> not admin
    if hasattr(current_user, "approved"):
        raise HTTPException(status_code=403, detail="Admin privileges required")

    inst = crud.get_expense(db, company_name, expense_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Expense not found")

    changes = {}

    if expense_type is not None:
        if expense_type.lower() == "purchase":
            changes["expense_type_flag"] = 0
            changes["expense_type"] = "Purchase"
        else:
            changes["expense_type_flag"] = 1
            changes["expense_type"] = "Others"

    if gst_number is not None:
        changes["gst_number"] = gst_number

    if date is not None:
        try:
            dt = datetime.fromisoformat(date).date()
        except Exception:
            try:
                dt = datetime.strptime(date, "%d-%m-%Y").date()
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid date format")
        changes["date"] = dt

    for local_field in ("invoice_number", "vendor_name", "invoice_amount", "purpose", "purchased_by", "amount_paid", "amount_paid_by"):
        val = locals().get(local_field)
        if val is not None:
            changes[local_field] = val

    if payment_type is not None:
        if payment_type.lower() == "cash":
            changes["payment_type_flag"] = 0
            changes["payment_type"] = "Cash"
        else:
            changes["payment_type_flag"] = 1
            changes["payment_type"] = "UPI"

    # handle files
    if invoice_copy is not None:
        path = save_upload_file(invoice_copy, INVOICE_DIR)
        if path:
            changes["invoice_copy"] = path
    if qrcode is not None:
        path = save_upload_file(qrcode, QRCODE_DIR)
        if path:
            changes["qrcode"] = path
    if payment_screenshot is not None:
        path = save_upload_file(payment_screenshot, SCREENSHOT_DIR)
        if path:
            changes["payment_screenshot"] = path

    if allOk is not None:
        changes["status"] = "Completed" if allOk else "Pending"
    elif status is not None:
        changes["status"] = status


    admin_username = getattr(current_user, "username", None)
    if admin_username:
        changes["submitted_by"] = admin_username

    updated = crud.update_expense(db, company_name, expense_id, changes)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update")
    return updated


# DELETE expense - Admin only
@router.delete("/{company_name}/{expense_id}")
def delete_expense(company_name: str, expense_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if hasattr(current_user, "approved"):
        raise HTTPException(status_code=403, detail="Admin privileges required")

    ok = crud.delete_expense(db, company_name, expense_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"detail": "Expense deleted"}


# VENDOR endpoints
@router.post("/vendor", response_model=schemas_expenses.VendorOut)
def add_vendor(v: schemas_expenses.VendorCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = crud.get_vendor_by_name(db, v.name)
    if existing:
        raise HTTPException(status_code=400, detail="Vendor already exists")
    created = crud.create_vendor(db, v.name)
    return created

@router.get("/vendor", response_model=List[schemas_expenses.VendorOut])
def list_vendors(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.get_all_vendors(db)


# ---------------------------------------------------------
# FETCH FILE PATHS FOR VIEW ICON (Invoice / QR / Screenshot)
# ---------------------------------------------------------
@router.get("/{company_name}/{expense_id}/files")
def get_expense_files(
    company_name: str,
    expense_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    inst = crud.get_expense(db, company_name, expense_id)

    if not inst:
        raise HTTPException(status_code=404, detail="Expense not found")

    return {
        "invoice_copy": inst.invoice_copy,
        "qrcode": inst.qrcode,
        "payment_screenshot": inst.payment_screenshot,
    }
