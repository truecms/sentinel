"""
Test Data Factory for Sentinel Monitoring System

This factory provides comprehensive test data generation for realistic
testing scenarios.
It creates Drupal sites with modules, versions, and security scenarios that mirror
real-world deployments.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.organization import Organization
from app.models.site import Site
from app.models.site_module import SiteModule
from app.models.user import User


class TestDataFactory:
    """Factory for generating realistic test data scenarios."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self._load_templates()

    def _load_templates(self):
        """Load module templates from example files."""
        base_path = (
            Path(__file__).parent.parent.parent / "examples" / "drupal-submissions"
        )

        # Load existing templates
        self.minimal_modules = self._load_json_template(base_path / "minimal-site.json")
        self.standard_modules = self._load_json_template(
            base_path / "standard-site.json"
        )
        self.large_modules = self._load_json_template(base_path / "large-site.json")

        # Define common Drupal core modules
        self.core_modules = [
            {"machine_name": "views", "display_name": "Views", "module_type": "core"},
            {"machine_name": "node", "display_name": "Node", "module_type": "core"},
            {"machine_name": "user", "display_name": "User", "module_type": "core"},
            {"machine_name": "system", "display_name": "System", "module_type": "core"},
            {"machine_name": "field", "display_name": "Field", "module_type": "core"},
            {"machine_name": "text", "display_name": "Text", "module_type": "core"},
            {
                "machine_name": "taxonomy",
                "display_name": "Taxonomy",
                "module_type": "core",
            },
            {"machine_name": "file", "display_name": "File", "module_type": "core"},
        ]

        # Popular contrib modules
        self.contrib_modules = [
            {
                "machine_name": "webform",
                "display_name": "Webform",
                "module_type": "contrib",
            },
            {
                "machine_name": "paragraphs",
                "display_name": "Paragraphs",
                "module_type": "contrib",
            },
            {
                "machine_name": "pathauto",
                "display_name": "Pathauto",
                "module_type": "contrib",
            },
            {
                "machine_name": "token",
                "display_name": "Token",
                "module_type": "contrib",
            },
            {
                "machine_name": "admin_toolbar",
                "display_name": "Admin Toolbar",
                "module_type": "contrib",
            },
            {
                "machine_name": "metatag",
                "display_name": "Metatag",
                "module_type": "contrib",
            },
            {
                "machine_name": "entity_reference_revisions",
                "display_name": "Entity Reference Revisions",
                "module_type": "contrib",
            },
            {
                "machine_name": "redirect",
                "display_name": "Redirect",
                "module_type": "contrib",
            },
            {
                "machine_name": "google_analytics",
                "display_name": "Google Analytics",
                "module_type": "contrib",
            },
            {
                "machine_name": "backup_migrate",
                "display_name": "Backup and Migrate",
                "module_type": "contrib",
            },
        ]

        # Custom module templates
        self.custom_modules = [
            {
                "machine_name": "site_theme",
                "display_name": "Site Theme",
                "module_type": "custom",
            },
            {
                "machine_name": "api_integration",
                "display_name": "API Integration",
                "module_type": "custom",
            },
            {
                "machine_name": "custom_blocks",
                "display_name": "Custom Blocks",
                "module_type": "custom",
            },
            {
                "machine_name": "site_config",
                "display_name": "Site Configuration",
                "module_type": "custom",
            },
            {
                "machine_name": "data_import",
                "display_name": "Data Import Tool",
                "module_type": "custom",
            },
        ]

    def _load_json_template(self, file_path: Path) -> List[Dict]:
        """Load module data from JSON template file."""
        try:
            if file_path.exists():
                with open(file_path, "r") as f:
                    data = json.load(f)
                    return data.get("modules", [])
        except Exception:
            pass
        return []

    async def create_standard_drupal_site(
        self,
        organization: Organization,
        user: User,
        site_name: str = "Standard Drupal Site",
        site_url: str = "https://standard.example.com",
    ) -> Dict[str, Any]:
        """
        Create a standard Drupal site with ~50 modules.

        Returns a dictionary with created objects for use in tests.
        """
        # Create site
        site = Site(
            name=site_name,
            url=site_url,
            organization_id=organization.id,
            api_token=f"token_{random.randint(100000, 999999)}",
            created_by=user.id,
            updated_by=user.id,
        )
        self.db_session.add(site)
        await self.db_session.commit()
        await self.db_session.refresh(site)

        # Combine core and contrib modules for standard site
        modules_to_create = (
            self.core_modules
            + self.contrib_modules[:15]  # First 15 contrib modules
            + self.custom_modules[:3]  # First 3 custom modules
        )

        created_objects = {
            "site": site,
            "modules": [],
            "versions": [],
            "site_modules": [],
        }

        for module_data in modules_to_create:
            # Create module if it doesn't exist
            module = await self._get_or_create_module(module_data, user)
            created_objects["modules"].append(module)

            # Create version for this module
            version = await self._create_module_version(module, user)
            created_objects["versions"].append(version)

            # Create site-module association
            site_module = await self._create_site_module(site, module, version, user)
            created_objects["site_modules"].append(site_module)

        return created_objects

    async def create_large_enterprise_site(
        self,
        organization: Organization,
        user: User,
        site_name: str = "Enterprise Drupal Site",
        site_url: str = "https://enterprise.example.com",
    ) -> Dict[str, Any]:
        """
        Create an enterprise site with 200+ modules.

        Includes all core modules, many contrib modules, and numerous custom modules.
        """
        # Create site
        site = Site(
            name=site_name,
            url=site_url,
            organization_id=organization.id,
            api_token=f"token_{random.randint(100000, 999999)}",
            created_by=user.id,
            updated_by=user.id,
        )
        self.db_session.add(site)
        await self.db_session.commit()
        await self.db_session.refresh(site)

        # Generate additional contrib modules for enterprise site
        additional_contrib = [
            {
                "machine_name": f"contrib_module_{i}",
                "display_name": f"Contrib Module {i}",
                "module_type": "contrib",
            }
            for i in range(1, 51)  # 50 additional contrib modules
        ]

        # Generate additional custom modules for enterprise site
        additional_custom = [
            {
                "machine_name": f"custom_module_{i}",
                "display_name": f"Custom Module {i}",
                "module_type": "custom",
            }
            for i in range(1, 101)  # 100 additional custom modules
        ]

        # Combine all modules for enterprise site
        modules_to_create = (
            self.core_modules
            + self.contrib_modules
            + additional_contrib
            + self.custom_modules
            + additional_custom
        )

        created_objects = {
            "site": site,
            "modules": [],
            "versions": [],
            "site_modules": [],
        }

        for module_data in modules_to_create:
            # Create module if it doesn't exist
            module = await self._get_or_create_module(module_data, user)
            created_objects["modules"].append(module)

            # Create version for this module
            version = await self._create_module_version(module, user)
            created_objects["versions"].append(version)

            # Create site-module association
            site_module = await self._create_site_module(site, module, version, user)
            created_objects["site_modules"].append(site_module)

        return created_objects

    async def create_minimal_site(
        self,
        organization: Organization,
        user: User,
        site_name: str = "Minimal Drupal Site",
        site_url: str = "https://minimal.example.com",
    ) -> Dict[str, Any]:
        """
        Create a minimal Drupal site with just core modules.
        """
        # Create site
        site = Site(
            name=site_name,
            url=site_url,
            organization_id=organization.id,
            api_token=f"token_{random.randint(100000, 999999)}",
            created_by=user.id,
            updated_by=user.id,
        )
        self.db_session.add(site)
        await self.db_session.commit()
        await self.db_session.refresh(site)

        created_objects = {
            "site": site,
            "modules": [],
            "versions": [],
            "site_modules": [],
        }

        # Only create core modules for minimal site
        for module_data in self.core_modules:
            # Create module if it doesn't exist
            module = await self._get_or_create_module(module_data, user)
            created_objects["modules"].append(module)

            # Create version for this module
            version = await self._create_module_version(module, user)
            created_objects["versions"].append(version)

            # Create site-module association
            site_module = await self._create_site_module(site, module, version, user)
            created_objects["site_modules"].append(site_module)

        return created_objects

    async def populate_security_scenarios(self, user: User) -> Dict[str, Any]:
        """
        Create modules with security vulnerabilities and updates.

        Returns security-related test data including vulnerable modules and
        security versions.
        """
        security_modules = []
        security_versions = []

        # Create modules with known security issues
        vulnerable_modules_data = [
            {
                "machine_name": "webform",
                "display_name": "Webform",
                "module_type": "contrib",
                "vulnerable_version": "6.2.5",
                "secure_version": "6.2.8",
                "advisory_id": "SA-CONTRIB-2024-015",
                "severity": "high",
            },
            {
                "machine_name": "views",
                "display_name": "Views",
                "module_type": "core",
                "vulnerable_version": "10.2.0",
                "secure_version": "10.3.8",
                "advisory_id": "SA-CORE-2024-001",
                "severity": "critical",
            },
            {
                "machine_name": "paragraphs",
                "display_name": "Paragraphs",
                "module_type": "contrib",
                "vulnerable_version": "1.15.0",
                "secure_version": "1.18.0",
                "advisory_id": "SA-CONTRIB-2024-023",
                "severity": "medium",
            },
        ]

        for module_data in vulnerable_modules_data:
            # Create module
            module = await self._get_or_create_module(module_data, user)
            security_modules.append(module)

            # Create vulnerable version
            vulnerable_version = await self._get_or_create_module_version(
                module=module,
                version_string=module_data["vulnerable_version"],
                user=user,
                release_date=datetime.utcnow() - timedelta(days=120),
                is_security_update=False,
            )

            # Create secure version
            secure_version = await self._get_or_create_module_version(
                module=module,
                version_string=module_data["secure_version"],
                user=user,
                release_date=datetime.utcnow() - timedelta(days=30),
                is_security_update=True,
            )

            security_versions.extend([vulnerable_version, secure_version])

        return {
            "security_modules": security_modules,
            "security_versions": security_versions,
            "advisory_data": vulnerable_modules_data,
        }

    async def create_bulk_test_data(
        self,
        organization: Organization,
        user: User,
        num_sites: int = 10,
        modules_per_site: int = 50,
    ) -> Dict[str, Any]:
        """
        Create bulk test data for performance testing.

        Args:
            num_sites: Number of sites to create
            modules_per_site: Average number of modules per site
        """
        created_sites = []
        all_modules = []
        all_site_modules = []

        # Prepare modules to use
        all_available_modules = self.core_modules + self.contrib_modules + self.custom_modules
        
        # Generate additional modules if needed to reach modules_per_site
        if len(all_available_modules) < modules_per_site:
            for i in range(len(all_available_modules), modules_per_site):
                all_available_modules.append({
                    "machine_name": f"bulk_module_{i}",
                    "display_name": f"Bulk Module {i}",
                    "module_type": "contrib" if i % 2 == 0 else "custom",
                })

        for i in range(num_sites):
            # Create site
            site = Site(
                name=f"Bulk Test Site {i+1}",
                url=f"https://bulk-site-{i+1}.example.com",
                organization_id=organization.id,
                api_token=f"token_{random.randint(100000, 999999)}",
                created_by=user.id,
                updated_by=user.id,
            )
            self.db_session.add(site)
            await self.db_session.commit()
            await self.db_session.refresh(site)
            
            site_data = {
                "site": site,
                "modules": [],
                "versions": [],
                "site_modules": [],
            }
            
            # Use the requested number of modules per site
            modules_to_use = all_available_modules[:modules_per_site]
            
            for module_data in modules_to_use:
                # Create module if it doesn't exist
                module = await self._get_or_create_module(module_data, user)
                site_data["modules"].append(module)

                # Create version for this module
                version = await self._create_module_version(module, user)
                site_data["versions"].append(version)

                # Create site-module association
                site_module = await self._create_site_module(site, module, version, user)
                site_data["site_modules"].append(site_module)

            created_sites.append(site_data["site"])
            all_modules.extend(site_data["modules"])
            all_site_modules.extend(site_data["site_modules"])

        return {
            "sites": created_sites,
            "total_modules": len(set(m.id for m in all_modules)),  # Unique modules
            "total_site_modules": len(all_site_modules),
            "site_data": [
                {
                    "site": site,
                    "module_count": len(
                        [sm for sm in all_site_modules if sm.site_id == site.id]
                    ),
                }
                for site in created_sites
            ],
        }

    async def _get_or_create_module(self, module_data: Dict, user: User) -> Module:
        """Get existing module or create new one."""
        # Check if module already exists
        from sqlalchemy import select

        stmt = select(Module).where(Module.machine_name == module_data["machine_name"])
        result = await self.db_session.execute(stmt)
        existing_module = result.scalar_one_or_none()

        if existing_module:
            return existing_module

        # Create new module
        module = Module(
            machine_name=module_data["machine_name"],
            display_name=module_data["display_name"],
            module_type=module_data["module_type"],
            drupal_org_link=module_data.get("drupal_org_link"),
            created_by=user.id,
            updated_by=user.id,
        )
        self.db_session.add(module)
        await self.db_session.commit()
        await self.db_session.refresh(module)

        return module

    async def _get_or_create_module_version(
        self, module: Module, version_string: str, user: User, **kwargs
    ) -> ModuleVersion:
        """Get existing module version or create new one."""
        # Check if version already exists for this module
        from sqlalchemy import select

        stmt = select(ModuleVersion).where(
            ModuleVersion.module_id == module.id,
            ModuleVersion.version_string == version_string
        )
        result = await self.db_session.execute(stmt)
        existing_version = result.scalar_one_or_none()

        if existing_version:
            return existing_version

        # Create new version with provided kwargs
        version = ModuleVersion(
            module_id=module.id,
            version_string=version_string,
            created_by=user.id,
            updated_by=user.id,
            **kwargs
        )
        self.db_session.add(version)
        await self.db_session.commit()
        await self.db_session.refresh(version)

        return version

    async def _create_module_version(self, module: Module, user: User) -> ModuleVersion:
        """Create a version for a module."""
        # Generate realistic version based on module type
        if module.module_type == "core":
            version_string = "10.3.8"
        elif module.module_type == "contrib":
            version_string = (
                f"{random.randint(1, 8)}.x-{random.randint(1, 5)}."
                f"{random.randint(0, 20)}"
            )
        else:  # custom
            version_string = (
                f"{random.randint(1, 3)}.{random.randint(0, 10)}.{random.randint(0, 5)}"
            )

        # Check if version already exists for this module
        from sqlalchemy import select

        stmt = select(ModuleVersion).where(
            ModuleVersion.module_id == module.id,
            ModuleVersion.version_string == version_string
        )
        result = await self.db_session.execute(stmt)
        existing_version = result.scalar_one_or_none()

        if existing_version:
            return existing_version

        version = ModuleVersion(
            module_id=module.id,
            version_string=version_string,
            release_date=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
            is_security_update=False,
            created_by=user.id,
            updated_by=user.id,
        )
        self.db_session.add(version)
        await self.db_session.commit()
        await self.db_session.refresh(version)

        return version

    async def _create_site_module(
        self, site: Site, module: Module, version: ModuleVersion, user: User
    ) -> SiteModule:
        """Create a site-module association."""
        site_module = SiteModule(
            site_id=site.id,
            module_id=module.id,
            current_version_id=version.id,
            enabled=True,
            update_available=random.choice([True, False]),
            security_update_available=random.choice([True, False, False, False]),  # 25% chance
            created_by=user.id,
            updated_by=user.id,
        )
        self.db_session.add(site_module)
        await self.db_session.commit()
        await self.db_session.refresh(site_module)

        return site_module


# Convenience functions for common test scenarios
async def create_populated_database(
    db_session: AsyncSession, organization: Organization, user: User
) -> Dict[str, Any]:
    """
    Create a fully populated test database with realistic data.

    This is the main function to use for comprehensive test scenarios.
    """
    factory = TestDataFactory(db_session)

    # Create different types of sites
    standard_site = await factory.create_standard_drupal_site(organization, user)
    minimal_site = await factory.create_minimal_site(organization, user)

    # Create security scenarios
    security_data = await factory.populate_security_scenarios(user)

    return {
        "factory": factory,
        "standard_site": standard_site,
        "minimal_site": minimal_site,
        "security_data": security_data,
        "total_modules": len(
            set(
                m.id
                for m in (
                    standard_site["modules"]
                    + minimal_site["modules"]
                    + security_data["security_modules"]
                )
            )
        ),
    }


async def create_sample_drupal_modules(user: User) -> List[Dict[str, Any]]:
    """
    Generate sample Drupal module data for API testing.

    Returns a list of module dictionaries suitable for API payloads.
    """
    return [
        {
            "machine_name": "views",
            "display_name": "Views",
            "module_type": "core",
            "version": "10.3.8",
            "enabled": True,
            "description": "Create customized lists and queries from your database.",
        },
        {
            "machine_name": "webform",
            "display_name": "Webform",
            "module_type": "contrib",
            "version": "6.2.8",
            "enabled": True,
            "description": "Builds professional, user-friendly web forms.",
        },
        {
            "machine_name": "paragraphs",
            "display_name": "Paragraphs",
            "module_type": "contrib",
            "version": "1.18.0",
            "enabled": True,
            "description": "Enables the creation of paragraphs entities.",
        },
        {
            "machine_name": "site_theme",
            "display_name": "Site Theme",
            "module_type": "custom",
            "version": "1.0.0",
            "enabled": True,
            "description": "Custom theme modifications for this site.",
        },
    ]
