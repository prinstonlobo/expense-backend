# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, auth
from app.deps import get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.hash_password(user_in.password)
    user = crud.create_user(db, user_in.username, user_in.email, hashed)
    # user is created with approved=False by default
    return user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses fields: username, password
    email = form_data.username
    password = form_data.password

    # Check admin first
    admin = crud.get_admin_by_email(db, email)
    if admin and auth.verify_password(password, admin.password_hash):
        token = auth.create_access_token({"sub": str(admin.email), "role": "admin", "email": admin.email})
        return {"access_token": token, "token_type": "bearer", "role": "admin"}

    # Then user
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not auth.verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.approved:
        raise HTTPException(status_code=403, detail="User not approved by admin")

    token = auth.create_access_token({"sub": str(user.email), "role": "user", "email": user.email})
    return {"access_token": token, "token_type": "bearer", "role": "user"}
