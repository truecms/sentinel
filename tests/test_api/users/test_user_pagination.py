"""
Tests for user pagination and filtering.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import get_password_hash

pytestmark = pytest.mark.asyncio

async def test_get_users_pagination(
    client: AsyncClient,
    superuser_token_headers: dict,
    db_session: AsyncSession
):
    """Test user list pagination."""
    # Create multiple test users
    for i in range(15):  # Create enough users to test pagination
        user = User(
            email=f"testuser{i}@example.com",
            hashed_password=get_password_hash("testpass123"),
            is_active=True,
            role="user"
        )
        db_session.add(user)
    await db_session.commit()

    # Test first page
    response = await client.get(
        "/api/v1/users/?skip=0&limit=10",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

    # Test second page
    response = await client.get(
        "/api/v1/users/?skip=10&limit=10",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert len(data) <= 10

async def test_get_users_filter_active(
    client: AsyncClient,
    superuser_token_headers: dict,
    db_session: AsyncSession
):
    """Test filtering users by active status."""
    # Create active and inactive users
    active_user = User(
        email="active@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="user"
    )
    inactive_user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=False,
        role="user"
    )
    db_session.add(active_user)
    db_session.add(inactive_user)
    await db_session.commit()

    # Test filtering active users
    response = await client.get(
        "/api/v1/users/?is_active=true",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(user["is_active"] for user in data)

    # Test filtering inactive users
    response = await client.get(
        "/api/v1/users/?is_active=false",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(not user["is_active"] for user in data)

async def test_get_users_filter_role(
    client: AsyncClient,
    superuser_token_headers: dict,
    db_session: AsyncSession
):
    """Test filtering users by role."""
    # Create users with different roles
    admin_user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="admin"
    )
    regular_user = User(
        email="user@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="user"
    )
    db_session.add(admin_user)
    db_session.add(regular_user)
    await db_session.commit()

    # Test filtering admin users
    response = await client.get(
        "/api/v1/users/?role=admin",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(user["role"] == "admin" for user in data)

    # Test filtering regular users
    response = await client.get(
        "/api/v1/users/?role=user",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(user["role"] == "user" for user in data)

async def test_get_users_search(
    client: AsyncClient,
    superuser_token_headers: dict,
    db_session: AsyncSession
):
    """Test searching users by email."""
    # Create users with specific emails
    search_user = User(
        email="searchable@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="user"
    )
    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="user"
    )
    db_session.add(search_user)
    db_session.add(other_user)
    await db_session.commit()

    # Test searching by email
    response = await client.get(
        "/api/v1/users/?search=searchable",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any("searchable" in user["email"] for user in data)

async def test_get_users_combined_filters(
    client: AsyncClient,
    superuser_token_headers: dict,
    db_session: AsyncSession
):
    """Test combining multiple filters."""
    # Create various users
    user1 = User(
        email="admin1@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="admin"
    )
    user2 = User(
        email="admin2@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=False,
        role="admin"
    )
    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()

    # Test combining role and active status filters
    response = await client.get(
        "/api/v1/users/?role=admin&is_active=true",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(user["role"] == "admin" and user["is_active"] for user in data) 