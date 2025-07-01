from app.core.security import get_password_hash
from app.models.user import User
from app.db.session import async_session_maker
import asyncio
from sqlalchemy import select
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def ensure_superuser():
    async with async_session_maker() as db:
        # Check if superuser exists
        query = select(User).where(User.email == 'admin@example.com')
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.info("Creating superuser...")
            # Generate password hash
            hashed_password = get_password_hash('admin123')
            logger.debug(f"Generated password hash: {hashed_password}")
            
            # Create user
            user = User(
                email='admin@example.com',
                hashed_password=hashed_password,
                is_superuser=True,
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info("Superuser created successfully")
            logger.debug(f"Created user details: {user.__dict__}")
        else:
            logger.info("Superuser already exists")
            logger.debug(f"User details: id={user.id}, email={user.email}, is_active={user.is_active}, is_superuser={user.is_superuser}")
            
            # Update password if needed
            hashed_password = get_password_hash('admin123')
            if user.hashed_password != hashed_password:
                logger.info("Updating superuser password...")
                user.hashed_password = hashed_password
                await db.commit()
                logger.info("Password updated successfully")

if __name__ == "__main__":
    asyncio.run(ensure_superuser()) 