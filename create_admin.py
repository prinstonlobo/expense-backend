# create_admin.py
from app.database import SessionLocal
from app import models
from app.auth import hash_password 

def create_admin():
    db = SessionLocal()
    email = "admin@gmail.com"
    existing = db.query(models.Admin).filter(models.Admin.email == email).first()
    if existing:
        print("Admin already exists")
        return
    pwd = "admin@123@*"  # change immediately after first run
    hashed = hash_password(pwd)
    admin = models.Admin(username="Admin", email=email, password_hash=hashed)
    db.add(admin)
    db.commit()
    print("Admin created:", email)

if __name__ == "__main__":
    create_admin()
