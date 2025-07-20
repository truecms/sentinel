"""Test user_organization table with is_default field"""
import pytest
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User
from app.models.user_organization import user_organization


@pytest.mark.asyncio
async def test_user_organization_insert_with_is_default(
    db_session: AsyncSession,
    test_user: User,
    test_organization: Organization
):
    """Test that we can insert a user_organization with is_default field"""
    # This test will fail if is_default field doesn't exist or isn't handled
    await db_session.execute(
        user_organization.insert().values(
            user_id=test_user.id,
            organization_id=test_organization.id,
            is_default=True
        )
    )
    await db_session.commit()
    
    # Query to verify the insert worked
    result = await db_session.execute(
        select(user_organization).where(
            user_organization.c.user_id == test_user.id,
            user_organization.c.organization_id == test_organization.id
        )
    )
    row = result.fetchone()
    
    assert row is not None
    assert row.user_id == test_user.id
    assert row.organization_id == test_organization.id
    assert row.is_default is True