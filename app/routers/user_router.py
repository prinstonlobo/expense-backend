# app/routers/user_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app import schemas, auth, crud
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

router = APIRouter( tags=["user"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = auth.decode_token(token)
        role = payload.get("role")
        if role != "user":
            raise HTTPException(status_code=403, detail="Not authorized")
        email = payload.get("email")
        user = crud.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@router.get("/me", response_model=schemas.UserOut)
def me(current_user = Depends(get_user_from_token)):
    return current_user
