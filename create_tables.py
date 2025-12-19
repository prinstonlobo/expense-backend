from app.database import engine, Base
import app.models  # ensures models get registered

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
