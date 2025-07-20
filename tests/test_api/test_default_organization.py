"""Test default organization functionality"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.user import User
from app.models.user_organization import user_organization


@pytest.mark.asyncio
async def test_user_can_have_only_one_default_organization(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test that a user can only have one default organization"""
    # Create two organizations
    org1 = Organization(
        name="Organization 1",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False,
    )
    org2 = Organization(
        name="Organization 2",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False,
    )
    db_session.add(org1)
    db_session.add(org2)
    await db_session.commit()
    await db_session.refresh(org1)
    await db_session.refresh(org2)
    
    # Add user to first organization as default
    await db_session.execute(
        user_organization.insert().values(
            user_id=test_user.id,
            organization_id=org1.id,
            is_default=True
        )
    )
    await db_session.commit()
    
    # Try to add user to second organization as default
    # This should fail due to the unique constraint
    from sqlalchemy.exc import IntegrityError
    
    with pytest.raises(IntegrityError):
        await db_session.execute(
            user_organization.insert().values(
                user_id=test_user.id,
                organization_id=org2.id,
                is_default=True
            )
        )
        await db_session.commit()
    
    # Rollback the failed transaction
    await db_session.rollback()
    
    # Verify user still has only one default organization
    query = select(user_organization).where(
        user_organization.c.user_id == test_user.id,
        user_organization.c.is_default == True
    )
    result = await db_session.execute(query)
    defaults = result.fetchall()
    
    assert len(defaults) == 1
    assert defaults[0].organization_id == org1.id


@pytest.mark.asyncio
async def test_switch_default_organization(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test switching default organization"""
    # Create two organizations
    org1 = Organization(
        name="Organization 1",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False,
    )
    org2 = Organization(
        name="Organization 2",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False,
    )
    db_session.add(org1)
    db_session.add(org2)
    await db_session.commit()
    await db_session.refresh(org1)
    await db_session.refresh(org2)
    
    # Add user to both organizations, first as default
    await db_session.execute(
        user_organization.insert().values(
            user_id=test_user.id,
            organization_id=org1.id,
            is_default=True
        )
    )
    await db_session.execute(
        user_organization.insert().values(
            user_id=test_user.id,
            organization_id=org2.id,
            is_default=False
        )
    )
    await db_session.commit()
    
    # Switch default to org2
    # First, unset current default
    await db_session.execute(
        user_organization.update()
        .where(
            user_organization.c.user_id == test_user.id,
            user_organization.c.is_default == True
        )
        .values(is_default=False)
    )
    
    # Then set new default
    await db_session.execute(
        user_organization.update()
        .where(
            user_organization.c.user_id == test_user.id,
            user_organization.c.organization_id == org2.id
        )
        .values(is_default=True)
    )
    await db_session.commit()
    
    # Verify the switch
    query = select(user_organization).where(
        user_organization.c.user_id == test_user.id,
        user_organization.c.is_default == True
    )
    result = await db_session.execute(query)
    defaults = result.fetchall()
    
    assert len(defaults) == 1
    assert defaults[0].organization_id == org2.id


@pytest.mark.asyncio
async def test_registration_sets_default_organization(
    client: AsyncClient,
    db_session: AsyncSession
):
    """Test that registration sets the first organization as default"""
    # This is already tested in test_auth_registration.py
    # but we'll verify it from a different angle
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "Test123!",
            "full_name": "New User",
            "organization_name": "New Org"
        }
    )
    
    assert response.status_code == 200
    user_data = response.json()
    
    # Check the user_organization association
    query = select(user_organization).where(
        user_organization.c.user_id == user_data["id"]
    )
    result = await db_session.execute(query)
    user_orgs = result.fetchall()
    
    assert len(user_orgs) == 1
    assert user_orgs[0].is_default == True