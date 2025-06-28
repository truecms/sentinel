"""
Tests for user creation endpoints.
"""

import pytest
from httpx import AsyncClient
from app.models.organization import Organization
from app.models.user import User

pytestmark = pytest.mark.asyncio

async def test_create_user(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test creating a new user."""
    # Store organization ID before async operation
    org_id = test_organization.id
    
    response = await client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json={
            "email": "newuser@example.com",
            "password": "testpass123",
            "organization_id": org_id,
            "role": "user",
            "is_active": True,
            "is_superuser": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert data["is_active"] is True
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
            "role": "user",
            "is_active": True,
            "is_superuser": False
        }
    )
    assert response.status_code == 400

async def test_create_user_with_role(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test creating a user with a specific role."""
    response = await client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json={
            "email": "roleuser@example.com",
            "password": "testpass123",
            "organization_id": test_organization.id,
            "role": "admin",
            "is_active": True,
            "is_superuser": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"

async def test_create_user_invalid_organization(
    client: AsyncClient,
    superuser_token_headers: dict
):
    """Test creating a user with an invalid organization ID."""
    response = await client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json={
            "email": "invalid@example.com",
            "password": "testpass123",
            "organization_id": 99999,  # Non-existent organization ID
            "role": "user",
            "is_active": True,
            "is_superuser": False
        }
    )
    assert response.status_code == 404

async def test_create_organization_admin(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test creating an organization admin user."""
    # Store organization ID before async operation
    org_id = test_organization.id
    
    response = await client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json={
            "email": "orgadmin@example.com",
            "password": "testpass123",
            "organization_id": org_id,
            "role": "admin",
            "is_active": True,
            "is_superuser": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"
    assert data["organization_id"] == org_id 