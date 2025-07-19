#!/usr/bin/env python3
"""
Script to load comprehensive sample data into the monitoring database.
"""

import asyncio
import os
import sys
from pathlib import Path

import asyncpg

# Add the parent directory to the path so we can import from the app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)


async def load_sample_data():
    """Load the comprehensive sample data SQL file."""

    # Path to the sample data SQL file
    sql_file = Path(__file__).parent.parent / "sql" / "comprehensive_sample_data.sql"

    if not sql_file.exists():
        print(f"Error: Sample data file not found at {sql_file}")
        return False

    try:
        # Read the SQL file
        print(f"Reading sample data from {sql_file}")
        with open(sql_file, "r") as f:
            sql_content = f.read()

        # Connect to database
        print("Connecting to database...")
        connection = await asyncpg.connect(DATABASE_URL)

        try:
            # Execute the SQL
            print("Loading sample data...")
            await connection.execute(sql_content)
            print("✅ Sample data loaded successfully!")

            # Verify the data was loaded
            print("\n📊 Data verification:")

            # Check sites count
            sites_count = await connection.fetchval("SELECT COUNT(*) FROM sites")
            print(f"  Sites: {sites_count}")

            # Check modules count
            modules_count = await connection.fetchval("SELECT COUNT(*) FROM modules")
            print(f"  Modules: {modules_count}")

            # Check site_modules count
            site_modules_count = await connection.fetchval(
                "SELECT COUNT(*) FROM site_modules"
            )
            print(f"  Site modules: {site_modules_count}")

            # Check security updates count
            security_updates = await connection.fetchval(
                "SELECT COUNT(*) FROM site_modules WHERE security_update_available = true"
            )
            print(f"  Security updates needed: {security_updates}")

            # Check compliance
            total_sites = await connection.fetchval("SELECT COUNT(*) FROM sites")
            sites_with_updates = await connection.fetchval(
                "SELECT COUNT(DISTINCT site_id) FROM site_modules WHERE update_available = true"
            )
            compliance_rate = (
                ((total_sites - sites_with_updates) / total_sites * 100)
                if total_sites > 0
                else 100
            )
            print(f"  Compliance rate: {compliance_rate:.1f}%")

            return True

        finally:
            await connection.close()

    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return False


async def reset_database():
    """Reset the database by clearing all data."""

    try:
        print("Connecting to database...")
        connection = await asyncpg.connect(DATABASE_URL)

        try:
            print("Clearing existing data...")
            await connection.execute("DELETE FROM site_modules")
            await connection.execute("DELETE FROM module_versions")
            await connection.execute("DELETE FROM sites")
            await connection.execute("DELETE FROM modules")
            print("✅ Database cleared successfully!")

        finally:
            await connection.close()

    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

    return True


async def main():
    """Main function to handle command line arguments and run the script."""

    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        print("🔄 Resetting database...")
        success = await reset_database()
        if not success:
            sys.exit(1)

    print("📦 Loading sample data...")
    success = await load_sample_data()

    if success:
        print("\n🎉 Sample data loading completed successfully!")
        print("\n💡 You can now:")
        print("   1. Visit the dashboard to see realistic metrics")
        print("   2. Check the Module Status Overview table")
        print("   3. View security alerts and compliance data")
        print("   4. Test the real-time WebSocket updates")
    else:
        print("\n❌ Sample data loading failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
