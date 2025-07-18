import asyncio

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User


async def create_superuser():
    async with SessionLocal() as db:
        user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True,
        )
        db.add(user)
        await db.commit()


if __name__ == "__main__":
    asyncio.run(create_superuser())
