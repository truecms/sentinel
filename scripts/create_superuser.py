import asyncio

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User


async def create_superuser():
    async with SessionLocal() as db:
        user = User(
            _="admin@example.com",
            _=get_password_hash("admin123"),
            _=True,
            _=True,
        )
        db.add(user)
        await db.commit()


if __name__ == "__main__":
    asyncio.run(create_superuser())
