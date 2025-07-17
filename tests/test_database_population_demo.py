"""
Database Population Demonstration Test

This test demonstrates the comprehensive database population functionality
implemented for Issue #30. It shows how to populate the database with
realistic test data for various scenarios.

Run with: pytest tests/test_database_population_demo.py -v
"""

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.organization import Organization
from app.models.site import Site
from app.models.site_module import SiteModule
from app.models.user import User


class TestDatabasePopulationDemo:
    """Demonstration of database population capabilities."""

    async def test_comprehensive_database_population(self, populated_database: dict):
        """
        MAIN DEMO: Show comprehensive database population in action.

        This test demonstrates:
        1. Creating realistic Drupal sites with modules
        2. Populating security vulnerability scenarios
        3. Generating bulk test data for performance testing
        4. Creating various site types (minimal, standard, enterprise)
        """
        print("\n🚀 Database Population Demo - Issue #30")
        print("=" * 50)

        # Verify populated database structure
        assert "factory" in populated_database
        assert "standard_site" in populated_database
        assert "minimal_site" in populated_database
        assert "security_data" in populated_database

        # Demo 1: Standard Drupal Site
        standard_site = populated_database["standard_site"]
        print(f"\n📊 Standard Site: {standard_site['site'].name}")
        print(f"   URL: {standard_site['site'].url}")
        print(f"   Modules: {len(standard_site['modules'])}")
        print(f"   Versions: {len(standard_site['versions'])}")
        print(f"   Site-Module associations: {len(standard_site['site_modules'])}")

        # Show module type distribution
        module_types = {}
        for module in standard_site["modules"]:
            module_types[module.module_type] = (
                module_types.get(module.module_type, 0) + 1
            )

        print("   Module types:")
        for mod_type, count in module_types.items():
            print(f"     {mod_type}: {count}")

        # Demo 2: Minimal Site
        minimal_site = populated_database["minimal_site"]
        print(f"\n🔬 Minimal Site: {minimal_site['site'].name}")
        print(f"   URL: {minimal_site['site'].url}")
        print(f"   Modules: {len(minimal_site['modules'])} (core only)")

        core_modules = [m.machine_name for m in minimal_site["modules"]]
        print(f"   Core modules: {', '.join(core_modules)}")

        # Demo 3: Security Data
        security_data = populated_database["security_data"]
        print(f"\n🔒 Security Test Data:")
        print(f"   Vulnerable modules: {len(security_data['security_modules'])}")
        print(f"   Security versions: {len(security_data['security_versions'])}")

        for advisory in security_data["advisory_data"]:
            print(
                f"   {advisory['machine_name']}: {advisory['vulnerable_version']} → {advisory['secure_version']} ({advisory['severity']})"
            )

        # Demo 4: Total Statistics
        print(f"\n📈 Total Database Stats:")
        print(f"   Total unique modules: {populated_database['total_modules']}")
        print(f"   Standard site modules: {len(standard_site['modules'])}")
        print(f"   Minimal site modules: {len(minimal_site['modules'])}")
        print(f"   Security scenarios: {len(security_data['security_modules'])}")

        print("\n✅ Database Population Demo Complete!")

    async def test_enterprise_site_population(self, enterprise_drupal_site: dict):
        """Demo: Enterprise site with 200+ modules."""
        print("\n🏢 Enterprise Site Population Demo")
        print("=" * 40)

        site = enterprise_drupal_site["site"]
        modules = enterprise_drupal_site["modules"]

        print(f"Site: {site.name}")
        print(f"URL: {site.url}")
        print(f"Total modules: {len(modules)}")

        # Show module type distribution
        module_types = {}
        for module in modules:
            module_types[module.module_type] = (
                module_types.get(module.module_type, 0) + 1
            )

        print("Module distribution:")
        for mod_type, count in module_types.items():
            print(f"  {mod_type}: {count}")

        # Verify enterprise site has significantly more modules
        assert len(modules) >= 150
        assert module_types.get("custom", 0) >= 100  # Many custom modules

        print("✅ Enterprise site populated successfully!")

    async def test_bulk_data_population_demo(self, bulk_test_data: dict):
        """Demo: Bulk data creation for performance testing."""
        print("\n📊 Bulk Data Population Demo")
        print("=" * 35)

        sites = bulk_test_data["sites"]
        total_modules = bulk_test_data["total_modules"]
        total_site_modules = bulk_test_data["total_site_modules"]

        print(f"Sites created: {len(sites)}")
        print(f"Unique modules: {total_modules}")
        print(f"Total site-module associations: {total_site_modules}")
        print(f"Average modules per site: {total_site_modules // len(sites)}")

        # Show site distribution
        print("\nSites created:")
        for i, site in enumerate(sites[:5]):  # Show first 5
            site_data = bulk_test_data["site_data"][i]
            print(f"  {site.name}: {site_data['module_count']} modules")

        if len(sites) > 5:
            print(f"  ... and {len(sites) - 5} more sites")

        print("✅ Bulk data populated successfully!")

    async def test_security_scenarios_demo(self, security_test_data: dict):
        """Demo: Security vulnerability scenarios."""
        print("\n🔐 Security Scenarios Demo")
        print("=" * 30)

        modules = security_test_data["security_modules"]
        versions = security_test_data["security_versions"]
        advisory_data = security_test_data["advisory_data"]

        print(f"Security scenarios created: {len(modules)}")
        print(f"Total versions (vulnerable + secure): {len(versions)}")

        print("\nSecurity advisories:")
        for advisory in advisory_data:
            print(f"  📋 {advisory['advisory_id']}")
            print(f"     Module: {advisory['machine_name']}")
            print(f"     Severity: {advisory['severity']}")
            print(f"     Vulnerable: {advisory['vulnerable_version']}")
            print(f"     Secure: {advisory['secure_version']}")
            print()

        # Verify security versions
        security_versions = [v for v in versions if v.is_security_update]
        vulnerable_versions = [v for v in versions if not v.is_security_update]

        assert len(security_versions) == 3
        assert len(vulnerable_versions) == 3

        print("✅ Security scenarios populated successfully!")

    async def test_database_query_performance(
        self, db_session: AsyncSession, populated_database: dict
    ):
        """Demo: Query populated database to verify data integrity."""
        print("\n⚡ Database Query Performance Demo")
        print("=" * 40)

        # Count total records in each table
        tables_to_count = [
            (Module, "Modules"),
            (ModuleVersion, "Module Versions"),
            (Site, "Sites"),
            (SiteModule, "Site-Module Associations"),
            (Organization, "Organizations"),
            (User, "Users"),
        ]

        print("Database record counts:")
        for model, name in tables_to_count:
            stmt = select(func.count(model.id))
            result = await db_session.execute(stmt)
            count = result.scalar()
            print(f"  {name}: {count}")

        # Test some specific queries
        print("\nQuery tests:")

        # Find all contrib modules
        stmt = select(Module).where(Module.module_type == "contrib")
        result = await db_session.execute(stmt)
        contrib_modules = result.scalars().all()
        print(f"  Contrib modules: {len(contrib_modules)}")

        # Find modules with security updates
        stmt = select(ModuleVersion).where(ModuleVersion.is_security_update == True)
        result = await db_session.execute(stmt)
        security_versions = result.scalars().all()
        print(f"  Security update versions: {len(security_versions)}")

        # Find sites with modules needing updates
        stmt = select(SiteModule).where(SiteModule.update_available == True)
        result = await db_session.execute(stmt)
        outdated_site_modules = result.scalars().all()
        print(f"  Site modules needing updates: {len(outdated_site_modules)}")

        print("✅ Database queries completed successfully!")

    async def test_realistic_data_structure(self, sample_drupal_modules: list[dict]):
        """Demo: Realistic module data structure."""
        print("\n📋 Sample Data Structure Demo")
        print("=" * 35)

        print(f"Sample modules generated: {len(sample_drupal_modules)}")
        print("\nModule details:")

        for module in sample_drupal_modules:
            print(f"  📦 {module['machine_name']}")
            print(f"     Name: {module['display_name']}")
            print(f"     Type: {module['module_type']}")
            print(f"     Version: {module['version']}")
            print(f"     Enabled: {module['enabled']}")
            if "description" in module:
                print(f"     Description: {module['description'][:50]}...")
            print()

        # Verify data structure
        for module in sample_drupal_modules:
            assert "machine_name" in module
            assert "display_name" in module
            assert "module_type" in module
            assert "version" in module
            assert "enabled" in module
            assert module["module_type"] in ["core", "contrib", "custom"]

        print("✅ Sample data structure validated!")


class TestFactoryDirectUsage:
    """Demo: Direct usage of TestDataFactory."""

    async def test_factory_direct_usage(
        self, db_session: AsyncSession, test_organization: Organization, test_user: User
    ):
        """Demo: Using TestDataFactory directly in tests."""
        print("\n🏭 TestDataFactory Direct Usage Demo")
        print("=" * 45)

        from tests.factories.data_factory import TestDataFactory

        factory = TestDataFactory(db_session)

        # Create a custom site using the factory
        custom_site = await factory.create_standard_drupal_site(
            organization=test_organization,
            user=test_user,
            site_name="Custom Demo Site",
            site_url="https://custom-demo.example.com",
        )

        print(f"Created site: {custom_site['site'].name}")
        print(f"Modules created: {len(custom_site['modules'])}")
        print(f"Versions created: {len(custom_site['versions'])}")
        print(f"Site-module associations: {len(custom_site['site_modules'])}")

        # Create security scenarios
        security_data = await factory.populate_security_scenarios(test_user)

        print(f"\nSecurity data created:")
        print(
            f"  Modules with vulnerabilities: {len(security_data['security_modules'])}"
        )
        print(f"  Security versions: {len(security_data['security_versions'])}")

        # Verify factory created data correctly
        assert len(custom_site["modules"]) >= 15
        assert len(security_data["security_modules"]) == 3

        print("✅ Factory direct usage successful!")


if __name__ == "__main__":
    print("Run with: pytest tests/test_database_population_demo.py -v -s")
    print("The -s flag shows the demo output during test execution.")
