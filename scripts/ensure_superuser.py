from app.core.security import get_password_hash
from app.models.user import User
from app.db.session import SessionLocal
import asyncio
from sqlalchemy import select

async def ensure_superuser():
    async with SessionLocal() as db:
        # Check if superuser exists
        query = select(User).where(User.email == 'admin@example.com')
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            print("Creating superuser...")
            user = User(
                email='admin@example.com',
                hashed_password=get_password_hash('admin123'),
                is_superuser=True,
                is_active=True
            )
            db.add(user)
            await db.commit()
            print("Superuser created successfully")
        else:
            print("Superuser already exists")
            print(f"User details: id={user.id}, email={user.email}, is_active={user.is_active}, is_superuser={user.is_superuser}")

if __name__ == "__main__":
    asyncio.run(ensure_superuser()) 