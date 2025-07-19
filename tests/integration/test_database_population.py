"""
Integration tests for database population and test data generation.

These tests verify that the comprehensive test data population utilities
work correctly and can generate realistic test scenarios for the monitoring system.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.site_module import SiteModule
from app.models.user import User


class TestDatabasePopulation:
    """Test database population utilities and fixtures."""

    async def test_populated_database_fixture(self, populated_database: dict):
        """Test that the populated_database fixture creates comprehensive test data."""
        assert "factory" in populated_database
        assert "standard_site" in populated_database
        assert "minimal_site" in populated_database
        assert "security_data" in populated_database
        assert "total_modules" in populated_database

        # Verify standard site has expected structure
        standard_site = populated_database["standard_site"]
        assert "site" in standard_site
        assert "modules" in standard_site
        assert "versions" in standard_site
        assert "site_modules" in standard_site

        # Verify we have a reasonable number of modules for a standard site
        assert len(standard_site["modules"]) >= 15  # Core + contrib + custom
        assert len(standard_site["modules"]) <= 30  # Not too many for standard

        # Verify minimal site has only core modules
        minimal_site = populated_database["minimal_site"]
        assert len(minimal_site["modules"]) == 8  # Should be exactly 8 core modules

        # Verify security data is present
        security_data = populated_database["security_data"]
        assert len(security_data["security_modules"]) >= 3
        assert len(security_data["security_versions"]) >= 6  # 2 versions per module

    async def test_standard_drupal_site_creation(self, standard_drupal_site: dict):
        """Test creation of a standard Drupal site with realistic modules."""
        assert "site" in standard_drupal_site
        assert "modules" in standard_drupal_site
        assert "versions" in standard_drupal_site
        assert "site_modules" in standard_drupal_site

        site = standard_drupal_site["site"]
        assert site.name == "Standard Test Site"
        assert site.url == "https://standard-test.example.com"
        assert site.api_token is not None

        modules = standard_drupal_site["modules"]
        versions = standard_drupal_site["versions"]
        site_modules = standard_drupal_site["site_modules"]

        # Verify we have modules of different types
        module_types = {module.module_type for module in modules}
        assert "core" in module_types
        assert "contrib" in module_types
        assert "custom" in module_types

        # Verify each module has a version
        assert len(modules) == len(versions)
        assert len(modules) == len(site_modules)

        # Verify all site modules are enabled
        assert all(sm.enabled for sm in site_modules)

    async def test_enterprise_drupal_site_creation(self, enterprise_drupal_site: dict):
        """Test creation of an enterprise site with 200+ modules."""
        assert "site" in enterprise_drupal_site
        assert "modules" in enterprise_drupal_site

        site = enterprise_drupal_site["site"]
        assert site.name == "Enterprise Test Site"

        modules = enterprise_drupal_site["modules"]

        # Enterprise site should have significantly more modules
        assert len(modules) >= 150  # Should be close to or over 200

        # Verify distribution of module types
        module_types = {}
        for module in modules:
            module_types[module.module_type] = (
                module_types.get(module.module_type, 0) + 1
            )

        assert module_types.get("core", 0) >= 8
        assert module_types.get("contrib", 0) >= 50
        assert module_types.get("custom", 0) >= 100

    async def test_minimal_drupal_site_creation(self, minimal_drupal_site: dict):
        """Test creation of a minimal site with only core modules."""
        assert "site" in minimal_drupal_site
        assert "modules" in minimal_drupal_site

        site = minimal_drupal_site["site"]
        assert site.name == "Minimal Test Site"

        modules = minimal_drupal_site["modules"]

        # Minimal site should have exactly 8 core modules
        assert len(modules) == 8

        # All modules should be core type
        assert all(module.module_type == "core" for module in modules)

        # Should include expected core modules
        module_names = {module.machine_name for module in modules}
        expected_core = {
            "views",
            "node",
            "user",
            "system",
            "field",
            "text",
            "taxonomy",
            "file",
        }
        assert module_names == expected_core

    async def test_security_test_data_creation(self, security_test_data: dict):
        """Test creation of security vulnerability scenarios."""
        assert "security_modules" in security_test_data
        assert "security_versions" in security_test_data
        assert "advisory_data" in security_test_data

        modules = security_test_data["security_modules"]
        versions = security_test_data["security_versions"]
        advisory_data = security_test_data["advisory_data"]

        # Should have 3 vulnerable modules
        assert len(modules) == 3
        assert len(advisory_data) == 3

        # Should have 6 versions (2 per module: vulnerable + secure)
        assert len(versions) == 6

        # Verify we have both vulnerable and secure versions
        security_versions = [v for v in versions if v.is_security_update]
        vulnerable_versions = [v for v in versions if not v.is_security_update]

        assert len(security_versions) == 3  # One secure version per module
        assert len(vulnerable_versions) == 3  # One vulnerable version per module

        # Verify advisory data structure
        for advisory in advisory_data:
            assert "machine_name" in advisory
            assert "vulnerable_version" in advisory
            assert "secure_version" in advisory
            assert "advisory_id" in advisory
            assert "severity" in advisory

    async def test_bulk_test_data_creation(self, bulk_test_data: dict):
        """Test creation of bulk test data for performance testing."""
        assert "sites" in bulk_test_data
        assert "total_modules" in bulk_test_data
        assert "total_site_modules" in bulk_test_data
        assert "site_data" in bulk_test_data

        sites = bulk_test_data["sites"]
        assert len(sites) == 10  # Should create 10 sites

        # Verify each site has unique name and URL
        site_names = {site.name for site in sites}
        site_urls = {site.url for site in sites}
        assert len(site_names) == 10  # All unique names
        assert len(site_urls) == 10  # All unique URLs

        # Verify we have a reasonable number of total modules
        total_modules = bulk_test_data["total_modules"]
        total_site_modules = bulk_test_data["total_site_modules"]

        assert total_modules >= 20  # Should have at least 20 unique modules
        assert total_site_modules >= 400  # 10 sites * ~40+ modules each

        # Verify site data structure
        site_data = bulk_test_data["site_data"]
        assert len(site_data) == 10

        for site_info in site_data:
            assert "site" in site_info
            assert "module_count" in site_info
            assert (
                site_info["module_count"] >= 15
            )  # Each site should have reasonable modules

    async def test_site_with_outdated_modules(self, site_with_outdated_modules: dict):
        """Test creation of a site with modules that have available updates."""
        assert "site" in site_with_outdated_modules
        assert "site_modules" in site_with_outdated_modules
        assert "updates_available" in site_with_outdated_modules

        site = site_with_outdated_modules["site"]
        site_modules = site_with_outdated_modules["site_modules"]
        updates_available = site_with_outdated_modules["updates_available"]

        assert site.name == "Site with Outdated Modules"
        assert updates_available == 2  # Should have 2 modules with updates
        assert len(site_modules) == 2

        # Verify all site modules are marked as having updates available
        assert all(sm.update_available for sm in site_modules)
        assert all(not sm.security_update_available for sm in site_modules)

    async def test_site_with_security_issues(self, site_with_security_issues: dict):
        """Test creation of a site with security vulnerabilities."""
        assert "site" in site_with_security_issues
        assert "site_modules" in site_with_security_issues
        assert "security_modules" in site_with_security_issues
        assert "advisory_data" in site_with_security_issues

        site = site_with_security_issues["site"]
        site_modules = site_with_security_issues["site_modules"]

        assert site.name == "Site with Security Issues"
        assert len(site_modules) >= 3  # Should have the 3 vulnerable modules

        # Verify all site modules are marked as having security updates
        assert all(sm.security_update_available for sm in site_modules)
        assert all(sm.update_available for sm in site_modules)


class TestDatabaseQueries:
    """Test that populated data can be queried correctly."""

    async def test_module_queries_with_populated_data(
        self, db_session: AsyncSession, populated_database: dict
    ):
        """Test querying modules from populated database."""
        # Count total modules
        stmt = select(func.count(Module.id))
        result = await db_session.execute(stmt)
        total_modules = result.scalar()

        assert total_modules >= 20  # Should have at least 20 modules

        # Query modules by type
        stmt = select(Module).where(Module.module_type == "core")
        result = await db_session.execute(stmt)
        core_modules = result.scalars().all()

        assert len(core_modules) >= 8  # Should have core modules

        # Query contrib modules
        stmt = select(Module).where(Module.module_type == "contrib")
        result = await db_session.execute(stmt)
        contrib_modules = result.scalars().all()

        assert len(contrib_modules) >= 10  # Should have contrib modules

    async def test_site_module_relationships(
        self, db_session: AsyncSession, standard_drupal_site: dict
    ):
        """Test that site-module relationships are correctly established."""
        site = standard_drupal_site["site"]

        # Query site modules with relationships
        stmt = (
            select(SiteModule)
            .where(SiteModule.site_id == site.id)
            .join(Module)
            .join(ModuleVersion)
        )
        result = await db_session.execute(stmt)
        site_modules = result.scalars().all()

        assert len(site_modules) >= 15  # Should have multiple modules

        # Verify each site module has proper relationships
        for site_module in site_modules:
            assert site_module.site_id == site.id
            assert site_module.module_id is not None
            assert site_module.current_version_id is not None
            assert site_module.enabled is True

    async def test_version_queries_with_security_data(
        self, db_session: AsyncSession, security_test_data: dict
    ):
        """Test querying security-related version data."""
        # Query security versions
        stmt = select(ModuleVersion).where(ModuleVersion.is_security_update)
        result = await db_session.execute(stmt)
        security_versions = result.scalars().all()

        assert len(security_versions) >= 3  # Should have security versions

        # Query vulnerable versions
        stmt = select(ModuleVersion).where(~ModuleVersion.is_security_update)
        result = await db_session.execute(stmt)
        vulnerable_versions = result.scalars().all()

        assert len(vulnerable_versions) >= 3  # Should have vulnerable versions

        # Verify version strings are realistic
        for version in security_versions + vulnerable_versions:
            assert version.version_string is not None
            assert len(version.version_string) > 0
            assert version.release_date is not None


class TestDataFactoryMethods:
    """Test individual TestDataFactory methods."""

    async def test_get_or_create_module(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test module creation and retrieval."""
        from tests.factories.data_factory import TestDataFactory

        factory = TestDataFactory(db_session)

        module_data = {
            "machine_name": "test_unique_module",
            "display_name": "Test Unique Module",
            "module_type": "contrib",
            "description": "A test module for testing",
        }

        # Create module first time
        module1 = await factory._get_or_create_module(module_data, test_user)
        assert module1.machine_name == "test_unique_module"
        assert module1.display_name == "Test Unique Module"
        assert module1.module_type == "contrib"

        # Try to create same module again - should return existing
        module2 = await factory._get_or_create_module(module_data, test_user)
        assert module1.id == module2.id  # Should be same module

    async def test_create_module_version(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test module version creation."""
        from tests.factories.data_factory import TestDataFactory

        factory = TestDataFactory(db_session)

        # Create a module first
        module_data = {
            "machine_name": "version_test_module",
            "display_name": "Version Test Module",
            "module_type": "contrib",
        }
        module = await factory._get_or_create_module(module_data, test_user)

        # Create version
        version = await factory._create_module_version(module, test_user)

        assert version.module_id == module.id
        assert version.version_string is not None
        assert version.release_date is not None
        assert version.created_by == test_user.id


class TestSampleDataConsistency:
    """Test that sample data generation is consistent and realistic."""

    async def test_sample_drupal_modules_structure(
        self, sample_drupal_modules: list[dict]
    ):
        """Test sample Drupal modules data structure."""
        assert len(sample_drupal_modules) >= 4  # Should have at least 4 sample modules

        for module_data in sample_drupal_modules:
            assert "machine_name" in module_data
            assert "display_name" in module_data
            assert "module_type" in module_data
            assert "version" in module_data
            assert "enabled" in module_data

            # Verify module types are valid
            assert module_data["module_type"] in ["core", "contrib", "custom"]

            # Verify machine names are realistic
            assert (
                "_" in module_data["machine_name"]
                or module_data["machine_name"].isalpha()
            )

            # Verify versions are realistic
            version = module_data["version"]
            assert len(version) > 0
            assert any(char.isdigit() for char in version)

    async def test_security_update_modules_structure(
        self, security_update_modules: list[dict]
    ):
        """Test security update modules data structure."""
        assert (
            len(security_update_modules) == 3
        )  # Should have exactly 3 security scenarios

        expected_severities = {"critical", "high", "medium"}
        actual_severities = {module["severity"] for module in security_update_modules}
        assert actual_severities == expected_severities

        for module_data in security_update_modules:
            assert "machine_name" in module_data
            assert "current_version" in module_data
            assert "secure_version" in module_data
            assert "severity" in module_data
            assert "advisory_id" in module_data
            assert "description" in module_data

            # Verify advisory ID format
            assert module_data["advisory_id"].startswith("SA-")
            assert len(module_data["advisory_id"]) > 10
