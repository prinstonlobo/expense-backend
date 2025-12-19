# app/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from typing import Generator

from app.database import SessionLocal
from app.auth import decode_token
from app import models


# OAuth2 scheme: token must be sent as Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Validates JWT token, returns the authenticated user or admin.
    """

    # 1. Decode token
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")   # username/email encoded inside token

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
        )

    # 2. Check if this user exists in database (admin or user)

    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return user

    admin = db.query(models.Admin).filter(models.Admin.email == email).first()
    if admin:
        return admin

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )
