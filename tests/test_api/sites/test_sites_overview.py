"""Tests for sites overview endpoint."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.site import Site
from app.models.user import User


class TestSitesOverview:
    """Test cases for GET /api/v1/sites/overview endpoint."""

    @pytest.fixture
    async def setup_test_data(self, db_session: AsyncSession, test_user: User):
        """Create test data for sites overview tests."""

        # Create organization
        org = Organization(
            name="Test Org",
            description="Test organization for sites overview",
            created_by=test_user.id,
        )
        db_session.add(org)
        await db_session.commit()
        await db_session.refresh(org)

        # Update test user to belong to this organization
        test_user.organization_id = org.id
        await db_session.commit()
        await db_session.refresh(test_user)

        # Create sites with different security profiles
        sites = []

        # Site 1: Healthy (high security score)
        site1 = Site(
            name="Healthy Site",
            url="https://healthy.example.com",
            organization_id=org.id,
            security_score=95,
            total_modules_count=20,
            security_updates_count=0,
            non_security_updates_count=1,
            created_by=test_user.id,
            updated_by=test_user.id,
            is_active=True,
            is_deleted=False,
        )
        db_session.add(site1)
        sites.append(site1)

        # Site 2: Warning (medium security score)
        site2 = Site(
            name="Warning Site",
            url="https://warning.example.com",
            organization_id=org.id,
            security_score=65,
            total_modules_count=35,
            security_updates_count=0,
            non_security_updates_count=8,
            created_by=test_user.id,
            updated_by=test_user.id,
            is_active=True,
            is_deleted=False,
        )
        db_session.add(site2)
        sites.append(site2)

        # Site 3: Critical (low security score, security updates needed)
        site3 = Site(
            name="Critical Site",
            url="https://critical.example.com",
            organization_id=org.id,
            security_score=25,
            total_modules_count=50,
            security_updates_count=5,
            non_security_updates_count=10,
            created_by=test_user.id,
            updated_by=test_user.id,
            is_active=True,
            is_deleted=False,
        )
        db_session.add(site3)
        sites.append(site3)

        await db_session.commit()
        for site in sites:
            await db_session.refresh(site)

        return {"organization": org, "sites": sites}

    async def test_get_sites_overview_success(
        self,
        client: AsyncClient,
        test_user: User,
        user_token_headers: dict,
        setup_test_data: dict,
    ):
        """Test successful retrieval of sites overview."""
        response = await client.get(
            "/api/v1/sites/overview", headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "sites" in data
        assert "pagination" in data
        assert "filters" in data

        # Check pagination
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["per_page"] == 100  # default
        assert pagination["total"] == 3
        assert pagination["total_pages"] == 1

        # Check sites data
        sites = data["sites"]
        assert len(sites) == 3

        # Verify site data structure
        site = sites[0]
        required_fields = [
            "id",
            "name",
            "url",
            "security_score",
            "total_modules_count",
            "security_updates_count",
            "non_security_updates_count",
            "last_data_push",
            "last_drupal_org_check",
            "status",
            "organization_id",
        ]
        for field in required_fields:
            assert field in site

        # Check status calculation
        site_statuses = {s["name"]: s["status"] for s in sites}
        assert site_statuses["Healthy Site"] == "healthy"
        assert site_statuses["Warning Site"] == "warning"
        assert site_statuses["Critical Site"] == "critical"

    async def test_sites_overview_pagination(
        self,
        client: AsyncClient,
        test_user: User,
        user_token_headers: dict,
        setup_test_data: dict,
    ):
        """Test pagination parameters."""
        # Test with limit
        response = await client.get(
            "/api/v1/sites/overview?limit=2", headers=user_token_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert len(data["sites"]) == 2
        assert data["pagination"]["per_page"] == 2
        assert data["pagination"]["total"] == 3
        assert data["pagination"]["total_pages"] == 2

        # Test with skip
        response = await client.get(
            "/api/v1/sites/overview?skip=2&limit=2", headers=user_token_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert len(data["sites"]) == 1  # Only 1 site left after skipping 2
        assert data["pagination"]["page"] == 2

    async def test_sites_overview_search(
        self,
        client: AsyncClient,
        test_user: User,
        user_token_headers: dict,
        setup_test_data: dict,
    ):
        """Test search functionality."""
        # Search by site name
        response = await client.get(
            "/api/v1/sites/overview?search=Healthy", headers=user_token_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert len(data["sites"]) == 1
        assert data["sites"][0]["name"] == "Healthy Site"

        # Search by URL
        response = await client.get(
            "/api/v1/sites/overview?search=warning.example", headers=user_token_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert len(data["sites"]) == 1
        assert data["sites"][0]["name"] == "Warning Site"

        # Case-insensitive search
        response = await client.get(
            "/api/v1/sites/overview?search=CRITICAL", headers=user_token_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert len(data["sites"]) == 1
        assert data["sites"][0]["name"] == "Critical Site"

    async def test_sites_overview_sorting(
        self,
        client: AsyncClient,
        test_user: User,
        user_token_headers: dict,
        setup_test_data: dict,
    ):
        """Test sorting functionality."""
        # Sort by security score ascending
        response = await client.get(
            "/api/v1/sites/overview?sort_by=security_score&sort_order=asc",
            headers=user_token_headers,
        )
        assert response.status_code == 200
        data = response.json()

        sites = data["sites"]
        scores = [site["security_score"] for site in sites]
        assert scores == sorted(scores)  # Should be in ascending order

        # Sort by security score descending
        response = await client.get(
            "/api/v1/sites/overview?sort_by=security_score&sort_order=desc",
            headers=user_token_headers,
        )
        assert response.status_code == 200
        data = response.json()

        sites = data["sites"]
        scores = [site["security_score"] for site in sites]
        assert scores == sorted(scores, reverse=True)  # Should be in descending order

        # Sort by name
        response = await client.get(
            "/api/v1/sites/overview?sort_by=name&sort_order=asc",
            headers=user_token_headers,
        )
        assert response.status_code == 200
        data = response.json()

        sites = data["sites"]
        names = [site["name"] for site in sites]
        assert names == sorted(names)

    async def test_sites_overview_filters_response(
        self,
        client: AsyncClient,
        test_user: User,
        user_token_headers: dict,
        setup_test_data: dict,
    ):
        """Test that filters are returned in response."""
        response = await client.get(
            "/api/v1/sites/overview?search=test&sort_by=security_score&sort_order=desc",
            headers=user_token_headers,
        )
        assert response.status_code == 200
        data = response.json()

        filters = data["filters"]
        assert filters["search"] == "test"
        assert filters["sort_by"] == "security_score"
        assert filters["sort_order"] == "desc"

    async def test_sites_overview_organization_filtering(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        user_token_headers: dict,
        setup_test_data: dict,
    ):
        """Test that users only see sites from their organization."""

        # Create another organization with a site
        other_org = Organization(
            name="Other Org",
            description="Another organization",
            created_by=test_user.id,
        )
        db_session.add(other_org)
        await db_session.commit()
        await db_session.refresh(other_org)

        other_site = Site(
            name="Other Org Site",
            url="https://other.example.com",
            organization_id=other_org.id,
            security_score=80,
            total_modules_count=15,
            security_updates_count=0,
            non_security_updates_count=0,
            created_by=test_user.id,
            updated_by=test_user.id,
            is_active=True,
            is_deleted=False,
        )
        db_session.add(other_site)
        await db_session.commit()

        # User should only see sites from their own organization
        response = await client.get(
            "/api/v1/sites/overview", headers=user_token_headers
        )
        assert response.status_code == 200
        data = response.json()

        # Should still only see 3 sites (from test user's organization)
        assert len(data["sites"]) == 3
        site_names = {site["name"] for site in data["sites"]}
        assert "Other Org Site" not in site_names

    async def test_sites_overview_empty_result(
        self, client: AsyncClient, test_user: User, user_token_headers: dict
    ):
        """Test response when no sites match criteria."""
        response = await client.get(
            "/api/v1/sites/overview?search=nonexistent", headers=user_token_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert data["sites"] == []
        assert data["pagination"]["total"] == 0
        assert data["pagination"]["total_pages"] == 0

    async def test_sites_overview_invalid_sort_order(
        self,
        client: AsyncClient,
        test_user: User,
        user_token_headers: dict,
        setup_test_data: dict,
    ):
        """Test validation of sort_order parameter."""
        response = await client.get(
            "/api/v1/sites/overview?sort_order=invalid", headers=user_token_headers
        )
        assert response.status_code == 422  # Validation error

    async def test_sites_overview_unauthorized(self, client: AsyncClient):
        """Test that unauthenticated requests are rejected."""
        # Remove authorization header
        client.headers.pop("Authorization", None)

        response = await client.get("/api/v1/sites/overview")
        assert response.status_code == 401
