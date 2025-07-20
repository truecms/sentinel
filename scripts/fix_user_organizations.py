#!/usr/bin/env python3
"""
Script to fix user-organization associations for existing users.
This ensures all users are properly associated with their organizations.
"""
import asyncio
import logging
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.models.user import User
from app.models.organization import Organization
from app.models.user_organization import user_organization

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_user_organizations():
    """Fix user-organization associations."""
    async with async_session_maker() as db:
        # Get all users with organization_id set
        users_query = select(User).where(User.organization_id.isnot(None))
        result = await db.execute(users_query)
        users = result.scalars().all()
        
        fixed_count = 0
        
        for user in users:
            # Check if user-organization association exists
            check_query = select(user_organization).where(
                user_organization.c.user_id == user.id,
                user_organization.c.organization_id == user.organization_id
            )
            result = await db.execute(check_query)
            existing = result.first()
            
            if not existing:
                # Create the association
                stmt = user_organization.insert().values(
                    user_id=user.id,
                    organization_id=user.organization_id,
                    is_default=True
                )
                await db.execute(stmt)
                fixed_count += 1
                logger.info(f"Fixed association for user {user.email} (ID: {user.id}) with organization {user.organization_id}")
        
        await db.commit()
        logger.info(f"Fixed {fixed_count} user-organization associations")


if __name__ == "__main__":
    asyncio.run(fix_user_organizations())