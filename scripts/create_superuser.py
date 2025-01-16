from app.core.security import get_password_hash
from app.models.user import User
from app.db.session import SessionLocal
import asyncio

async def create_superuser():
    async with SessionLocal() as db:
        user = User(
            email='admin@example.com',
            hashed_password=get_password_hash('admin123'),
            is_superuser=True,
            is_active=True
        )
        db.add(user)
        await db.commit()

if __name__ == "__main__":
    asyncio.run(create_superuser()) 