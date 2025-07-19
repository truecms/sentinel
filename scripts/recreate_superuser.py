import asyncio

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User


async def recreate_superuser():
    async with SessionLocal() as db:
        # Check if superuser exists
        query = select(User).where(User.email == "admin@example.com")
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user:
            print("Updating existing superuser...")
            # Update the existing user instead of deleting
            user.hashed_password = get_password_hash("admin123")
            user.is_superuser = True
            user.is_active = True
            await db.commit()
            print("Superuser updated successfully")
        else:
            print("Creating new superuser...")
            user = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                is_superuser=True,
                is_active=True,
            )
            db.add(user)
            await db.commit()
            print("Superuser created successfully")

        # Verify the user
        query = select(User).where(User.email == "admin@example.com")
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user:
            print(
                f"User details: id={user.id}, email={user.email}, is_active={user.is_active}, is_superuser={user.is_superuser}"
            )
            print(f"Hashed password: {user.hashed_password}")


if __name__ == "__main__":
    asyncio.run(recreate_superuser())
