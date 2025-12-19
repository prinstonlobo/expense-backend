# app/routers/admin_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.deps import get_db
from app import crud, schemas, auth

router = APIRouter(tags=["admin"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------------------------------------------------------
# FIXED: Admin token decoder (email-based, NOT ID based)
# ---------------------------------------------------------
def get_admin_from_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = auth.decode_token(token)

        # Validate admin role
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")

        # "sub" contains admin EMAIL (not ID)
        admin_email = payload.get("sub")
        if not admin_email:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")

        # Fetch admin by email
        admin = crud.get_admin_by_email(db, admin_email)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")

        return admin

    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


# ---------------------------------------------------------
# GET ALL USERS (Admin only)
# ---------------------------------------------------------
@router.get("/users", response_model=list[schemas.UserOut])
def list_users(
    current_admin = Depends(get_admin_from_token),
    db: Session = Depends(get_db)
):
    return crud.get_all_users(db)


# ---------------------------------------------------------
# APPROVE USER (Admin only)
# ---------------------------------------------------------
@router.post("/approve/{user_id}")
def approve_user(
    user_id: int,
    current_admin = Depends(get_admin_from_token),
    db: Session = Depends(get_db)
):
    ok = crud.approve_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User approved"}


# ---------------------------------------------------------
# DELETE USER (Admin only)
# ---------------------------------------------------------
@router.delete("/user/{user_id}")
def delete_user(
    user_id: int,
    current_admin = Depends(get_admin_from_token),
    db: Session = Depends(get_db)
):
    ok = crud.delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}
