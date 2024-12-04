import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_superuser():
    # Database session
    db: Session = SessionLocal()

    # Superuser details from environment variables
    superuser_email = os.getenv("SUPERUSER_EMAIL", "admin@example.com")
    superuser_password = os.getenv("SUPERUSER_PASSWORD", "admin123")

    # Check if superuser already exists
    superuser = db.query(User).filter(User.email == superuser_email).first()
    if superuser:
        print(f"Superuser with email {superuser_email} already exists. Skipping creation.")
    else:
        # Create superuser
        hashed_password = get_password_hash(superuser_password)
        superuser = User(
            email=superuser_email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True,
        )
        db.add(superuser)
        db.commit()
        print(f"Superuser with email {superuser_email} created successfully.")

    # Close the database session
    db.close()

if __name__ == "__main__":
    create_superuser() 