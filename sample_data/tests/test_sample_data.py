#!/usr/bin/env python3
"""
Test script to verify that sample data is loaded correctly.
"""

import os
import sys
import asyncio
import asyncpg
from pathlib import Path

# Add the parent directory to the path so we can import from the app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)


async def test_sample_data():
    """Test that sample data is loaded correctly."""

    print("🧪 Testing sample data...")

    try:
        # Connect to database
        connection = await asyncpg.connect(DATABASE_URL)

        try:
            # Test 1: Verify basic data counts
            print("\n📊 Test 1: Basic data counts")

            sites_count = await connection.fetchval("SELECT COUNT(*) FROM sites")
            modules_count = await connection.fetchval("SELECT COUNT(*) FROM modules")
            site_modules_count = await connection.fetchval(
                "SELECT COUNT(*) FROM site_modules"
            )

            print(f"  Sites: {sites_count} (expected: 8)")
            print(f"  Modules: {modules_count} (expected: 12)")
            print(f"  Site modules: {site_modules_count} (expected: >40)")

            # Verify expected counts
            assert sites_count == 8, f"Expected 8 sites, got {sites_count}"
            assert modules_count == 12, f"Expected 12 modules, got {modules_count}"
            assert (
                site_modules_count > 40
            ), f"Expected >40 site modules, got {site_modules_count}"

            print("  ✅ Basic data counts: PASS")

            # Test 2: Verify security updates
            print("\n🔒 Test 2: Security updates")

            security_updates = await connection.fetchval(
                "SELECT COUNT(*) FROM site_modules WHERE security_update_available = true"
            )
            sites_with_security = await connection.fetchval(
                "SELECT COUNT(DISTINCT site_id) FROM site_modules WHERE security_update_available = true"
            )

            print(f"  Security updates needed: {security_updates}")
            print(f"  Sites with security issues: {sites_with_security}")

            assert security_updates > 0, "Expected some security updates"
            assert sites_with_security > 0, "Expected some sites with security issues"

            print("  ✅ Security updates: PASS")

            # Test 3: Verify compliance rate is realistic
            print("\n📈 Test 3: Compliance rate")

            total_sites = await connection.fetchval("SELECT COUNT(*) FROM sites")
            sites_with_updates = await connection.fetchval(
                "SELECT COUNT(DISTINCT site_id) FROM site_modules WHERE update_available = true"
            )
            compliant_sites = total_sites - sites_with_updates
            compliance_rate = (
                (compliant_sites / total_sites * 100) if total_sites > 0 else 100
            )

            print(f"  Total sites: {total_sites}")
            print(f"  Sites needing updates: {sites_with_updates}")
            print(f"  Compliant sites: {compliant_sites}")
            print(f"  Compliance rate: {compliance_rate:.1f}%")

            # Verify realistic compliance (should be less than 100% but not too low)
            assert (
                0 < compliance_rate < 100
            ), f"Expected realistic compliance rate, got {compliance_rate:.1f}%"

            print("  ✅ Compliance rate: PASS")

            # Test 4: Verify module versions
            print("\n📦 Test 4: Module versions")

            modules_with_versions = await connection.fetchval(
                "SELECT COUNT(DISTINCT module_id) FROM module_versions"
            )
            security_versions = await connection.fetchval(
                "SELECT COUNT(*) FROM module_versions WHERE is_security_update = true"
            )

            print(f"  Modules with versions: {modules_with_versions}")
            print(f"  Security update versions: {security_versions}")

            assert modules_with_versions > 0, "Expected modules to have versions"
            assert security_versions > 0, "Expected some security update versions"

            print("  ✅ Module versions: PASS")

            # Test 5: Verify site variety
            print("\n🌐 Test 5: Site variety")

            # Get site compliance status
            sites_info = await connection.fetch(
                """
                SELECT 
                    s.name,
                    COUNT(sm.id) as total_modules,
                    COUNT(CASE WHEN sm.update_available = true THEN 1 END) as modules_needing_update,
                    COUNT(CASE WHEN sm.security_update_available = true THEN 1 END) as security_updates
                FROM sites s
                LEFT JOIN site_modules sm ON s.id = sm.site_id
                GROUP BY s.id, s.name
                ORDER BY s.name
            """
            )

            fully_compliant = 0
            partially_compliant = 0
            non_compliant = 0

            for site in sites_info:
                if site["modules_needing_update"] == 0:
                    fully_compliant += 1
                elif site["security_updates"] == 0:
                    partially_compliant += 1
                else:
                    non_compliant += 1

                print(
                    f"  {site['name']}: {site['total_modules']} modules, {site['modules_needing_update']} need updates, {site['security_updates']} security updates"
                )

            print(f"  Fully compliant sites: {fully_compliant}")
            print(f"  Partially compliant sites: {partially_compliant}")
            print(f"  Non-compliant sites: {non_compliant}")

            # Verify we have a mix of site statuses
            assert fully_compliant > 0, "Expected some fully compliant sites"
            assert non_compliant > 0, "Expected some non-compliant sites"

            print("  ✅ Site variety: PASS")

            print("\n🎉 All tests passed! Sample data is correctly loaded.")

            return True

        finally:
            await connection.close()

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def main():
    """Main function to run the tests."""

    success = await test_sample_data()

    if success:
        print("\n✅ Sample data tests completed successfully!")
    else:
        print("\n❌ Sample data tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
