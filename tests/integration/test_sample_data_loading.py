"""Integration test to demonstrate sample data loading for CI/CD."""

import os

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site import Site
from app.schemas.dashboard import SecurityMetrics


@pytest.mark.skipif(
    os.getenv("LOAD_SAMPLE_DATA") != "true",
    reason="Sample data loading is not enabled (set LOAD_SAMPLE_DATA=true)"
)
class TestSampleDataLoading:
    """Test suite that uses sample data for integration testing."""

    @pytest.mark.asyncio
    async def test_sample_sites_loaded(self, db_session: AsyncSession, load_sample_data):
        """Test that sample sites are loaded correctly."""
        # Query for sites
        result = await db_session.execute(
            select(Site).where(Site.organization_id == 1)
        )
        sites = result.scalars().all()
        
        # Verify we have 3 test sites
        assert len(sites) == 3
        
        # Verify site names
        site_names = {site.name for site in sites}
        expected_names = {
            "Test Production Site",
            "Test Staging Site", 
            "Test Development Site"
        }
        assert site_names == expected_names
        
        # Verify security scores
        for site in sites:
            if "Production" in site.name:
                assert site.security_score == 92
                assert site.security_updates_count == 0
            elif "Staging" in site.name:
                assert site.security_score == 78
                assert site.security_updates_count == 2
            elif "Development" in site.name:
                assert site.security_score == 65
                assert site.security_updates_count == 3
    
    @pytest.mark.asyncio
    async def test_security_dashboard_with_sample_data(self, db_session: AsyncSession, load_sample_data, client, superuser_token_headers):
        """Test security dashboard API with realistic sample data."""
        # Make request to security dashboard endpoint
        response = await client.get(
            "/api/v1/dashboard/security",
            headers=superuser_token_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the security dashboard contains expected data structure
        assert "metrics" in data
        assert "critical_modules" in data
        assert "vulnerability_timeline" in data
        assert "recent_patches" in data
        
        # Verify metrics structure - based on SecurityMetrics schema
        metrics = data["metrics"]
        assert "active_threats" in metrics
        assert "unpatched_vulnerabilities" in metrics
        assert "average_time_to_patch" in metrics
        assert "patches_applied_today" in metrics
        assert "pending_security_updates" in metrics
        assert "sla_compliance" in metrics
        
        # With current implementation, these will be placeholder values
        # but structure should be correct
        assert isinstance(metrics["active_threats"], int)
        assert isinstance(metrics["average_time_to_patch"], (int, float))
        assert isinstance(metrics["sla_compliance"], (int, float))
    
    def test_security_metrics_schema(self):
        """Test that SecurityMetrics schema accepts the correct fields."""
        # This test verifies the expected field names for SecurityMetrics
        metrics = SecurityMetrics(
            active_threats=5,
            unpatched_vulnerabilities=10,
            average_time_to_patch=24.5,
            patches_applied_today=3,
            pending_security_updates=7,
            sla_compliance=95.5
        )
        
        assert metrics.active_threats == 5
        assert metrics.unpatched_vulnerabilities == 10
        assert metrics.average_time_to_patch == 24.5
        assert metrics.patches_applied_today == 3
        assert metrics.pending_security_updates == 7
        assert metrics.sla_compliance == 95.5


def test_security_metrics_schema_standalone():
    """Test that SecurityMetrics schema accepts the correct fields."""
    # This test verifies the expected field names for SecurityMetrics
    metrics = SecurityMetrics(
        active_threats=5,
        unpatched_vulnerabilities=10,
        average_time_to_patch=24.5,
        patches_applied_today=3,
        pending_security_updates=7,
        sla_compliance=95.5
    )
    
    assert metrics.active_threats == 5
    assert metrics.unpatched_vulnerabilities == 10
    assert metrics.average_time_to_patch == 24.5
    assert metrics.patches_applied_today == 3
    assert metrics.pending_security_updates == 7
    assert metrics.sla_compliance == 95.5


@pytest.mark.skipif(
    os.getenv("LOAD_SAMPLE_DATA") != "true",
    reason="Sample data loading is not enabled (set LOAD_SAMPLE_DATA=true)"
)
class TestDashboardWithSampleData:
    """Test dashboard endpoints with sample data."""
    
    @pytest.mark.asyncio
    async def test_dashboard_overview_with_sample_data(self, db_session: AsyncSession, load_sample_data, client, superuser_token_headers):
        """Test dashboard overview API with realistic sample data."""
        # Make request to dashboard overview endpoint
        response = await client.get(
            "/api/v1/dashboard/overview",
            headers=superuser_token_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the dashboard overview contains expected data structure
        assert "metrics" in data
        assert "trends" in data
        assert "top_risks" in data
        assert "recent_activity" in data
        
        # Verify metrics structure
        metrics = data["metrics"]
        assert "total_sites" in metrics
        assert "security_score" in metrics
        assert "critical_updates" in metrics
        assert "compliance_rate" in metrics
        assert "vulnerabilities" in metrics
        
        # With sample data loaded, we should have some sites
        assert metrics["total_sites"] >= 3  # We loaded 3 test sites
        
        # Verify vulnerabilities structure
        vulnerabilities = metrics["vulnerabilities"]
        assert "critical" in vulnerabilities
        assert "high" in vulnerabilities
        assert "medium" in vulnerabilities
        assert "low" in vulnerabilities
    
    @pytest.mark.asyncio
    async def test_sites_api_with_sample_data(self, db_session: AsyncSession, load_sample_data, client, superuser_token_headers):
        """Test sites API endpoint with sample data."""
        # Get all sites
        response = await client.get(
            "/api/v1/sites",
            headers=superuser_token_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # We should have 3 sites from sample data
        sites = data["items"]
        assert len(sites) >= 3
        
        # Verify site properties
        site_names = [site["name"] for site in sites]
        assert "Test Production Site" in site_names
        assert "Test Staging Site" in site_names
        assert "Test Development Site" in site_names
        
        # Verify security scores match sample data
        for site in sites:
            if site["name"] == "Test Production Site":
                assert site["security_score"] == 92
                assert site["security_updates_count"] == 0
            elif site["name"] == "Test Staging Site":
                assert site["security_score"] == 78
                assert site["security_updates_count"] == 2
            elif site["name"] == "Test Development Site":
                assert site["security_score"] == 65
                assert site["security_updates_count"] == 3
    
    @pytest.mark.asyncio
    async def test_modules_api_with_sample_data(self, db_session: AsyncSession, load_sample_data, client, superuser_token_headers):
        """Test modules API endpoint with sample data."""
        from app.models.module import Module
        
        # First verify modules exist in database
        result = await db_session.execute(select(Module))
        db_modules = result.scalars().all()
        print(f"DEBUG: Found {len(db_modules)} modules in database")
        for mod in db_modules:
            print(f"  - {mod.display_name} ({mod.machine_name})")
        
        # Get all modules
        response = await client.get(
            "/api/v1/modules",
            headers=superuser_token_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        print(f"DEBUG: API Response: {data}")
        
        # We should have at least 9 modules from sample data
        modules = data["data"]
        
        assert len(modules) >= 9
        
        # Verify specific modules exist
        module_names = [module["display_name"] for module in modules]
        expected_modules = [
            "Views",
            "Node",
            "User",
            "System",
            "Webform",
            "Pathauto",
            "Token",
            "Metatag",
            "Custom Authentication"
        ]
        
        for expected in expected_modules:
            assert expected in module_names, f"Module {expected} not found"
        
        # Verify modules have necessary fields
        for module in modules:
            assert "id" in module
            assert "machine_name" in module
            assert "display_name" in module
            assert "module_type" in module
            assert module["module_type"] in ["core", "contrib", "custom"]
    
    @pytest.mark.asyncio
    async def test_module_versions_with_sample_data(self, db_session: AsyncSession, load_sample_data, client, superuser_token_headers):
        """Test module versions data from sample data."""
        from app.models.module_version import ModuleVersion
        from app.models.module import Module
        
        # First verify module versions exist in database
        result = await db_session.execute(
            select(ModuleVersion)
            .join(Module)
            .where(Module.machine_name == "webform")
        )
        webform_versions = result.scalars().all()
        print(f"DEBUG: Found {len(webform_versions)} versions for webform module")
        
        # Verify we have at least the expected versions
        assert len(webform_versions) >= 2  # At least current and latest
        
        version_strings = [v.version_string for v in webform_versions]
        print(f"DEBUG: Webform versions: {version_strings}")
        
        # Check for the actual versions based on what sample data contains
        # The sample data includes ['6.0.3', '6.0.4', '6.0.5']
        assert "6.0.3" in version_strings  # Older version
        assert "6.0.4" in version_strings  # Another version
        assert "6.0.5" in version_strings  # Latest version
        
        # Verify security update flag exists on at least one version
        has_security_update = any(v.is_security_update for v in webform_versions)
        assert has_security_update, "At least one version should have security update flag"