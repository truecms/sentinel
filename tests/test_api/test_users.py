import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.organization import Organization
from app.core.security import get_password_hash

pytestmark = pytest.mark.asyncio

async def test_create_user(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test creating a new user."""
    response = await client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json={
            "email": "newuser@example.com",
            "password": "testpass123",
            "organization_id": test_organization.id,
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "is_active" in data
    assert "password" not in data

async def test_create_user_duplicate_email(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User,
    test_organization: Organization
):
    """Test creating user with duplicate email."""
    response = await client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json={
            "email": test_user.email,
            "password": "testpass123",
            "organization_id": test_organization.id,
            "is_active": True
        }
    )
    assert response.status_code == 409

async def test_get_users(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User
):
    """Test getting list of users."""
    response = await client.get(
        "/api/v1/users/",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(user["email"] == test_user.email for user in data)

async def test_get_user(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User
):
    """Test getting user details."""
    response = await client.get(
        f"/api/v1/users/{test_user.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id

async def test_update_user(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User
):
    """Test updating user details."""
    response = await client.put(
        f"/api/v1/users/{test_user.id}",
        headers=superuser_token_headers,
        json={
            "email": "updated@example.com",
            "is_active": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["id"] == test_user.id

async def test_deactivate_user(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User
):
    """Test deactivating a user."""
    response = await client.put(
        f"/api/v1/users/{test_user.id}",
        headers=superuser_token_headers,
        json={
            "email": test_user.email,
            "is_active": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == False

async def test_delete_user(
    client: AsyncClient,
    superuser_token_headers: dict,
    db_session: AsyncSession
):
    """Test deleting a user."""
    # Create user to delete
    user = User(
        email="todelete@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    response = await client.delete(
        f"/api/v1/users/{user.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 204

    # Verify user is deleted
    response = await client.get(
        f"/api/v1/users/{user.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 404

async def test_user_me(
    client: AsyncClient,
    user_token_headers: dict,
    test_user: User
):
    """Test getting current user profile."""
    response = await client.get(
        "/api/v1/users/me",
        headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id

async def test_regular_user_cant_create_user(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization
):
    """Test that regular users cannot create new users."""
    response = await client.post(
        "/api/v1/users/",
        headers=user_token_headers,
        json={
            "email": "newuser@example.com",
            "password": "testpass123",
            "organization_id": test_organization.id,
            "is_active": True
        }
    )
    assert response.status_code == 403

async def test_get_organization_users(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    test_user: User,
    db_session: AsyncSession
):
    """Test getting all users in an organization."""
    # Create additional users in the organization
    for i in range(2):
        user = User(
            email=f"orguser{i}@example.com",
            hashed_password=get_password_hash("testpass123"),
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}/users",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least test_user should be there
