"""
Update detection service for Drupal modules.

Checks for available updates and identifies security updates.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.site_module import SiteModule
from app.services.version_comparator import VersionComparator
from app.services.version_parser import DrupalVersionParser


class UpdateInfo:
    """Information about an available update."""

    def __init__(
        self,
        current_version: str,
        latest_version: Optional[str] = None,
        latest_security_version: Optional[str] = None,
        update_available: bool = False,
        security_update_available: bool = False,
        version_lag: Optional[Dict[str, int]] = None,
    ):
        self.current_version = current_version
        self.latest_version = latest_version
        self.latest_security_version = latest_security_version
        self.update_available = update_available
        self.security_update_available = security_update_available
        self.version_lag = version_lag or {}


class UpdateDetector:
    """Service for detecting module updates."""

    def __init__(self):
        self.comparator = VersionComparator()
        self.parser = DrupalVersionParser()
        self._version_cache: Dict[str, List[str]] = {}

    async def check_module_updates(
        self, db: AsyncSession, module_id: int, current_version: str
    ) -> UpdateInfo:
        """
        Check if updates are available for a module.

        Args:
            db: Database session
            module_id: Module ID
            current_version: Current installed version

        Returns:
            UpdateInfo object with update details
        """
        # Get all versions for the module
        result = await db.execute(
            select(ModuleVersion.version_string)
            .where(ModuleVersion.module_id == module_id)
            .order_by(ModuleVersion.created_at.desc())
        )
        available_versions = [row[0] for row in await result.fetchall()]

        if not available_versions:
            return UpdateInfo(current_version=current_version)

        # Parse current version to get constraints
        try:
            current_parsed = self.parser.parse(current_version)
        except ValueError:
            return UpdateInfo(current_version=current_version)

        # Filter compatible versions
        compatible_versions = self.comparator.filter_compatible_versions(
            available_versions,
            drupal_core=current_parsed.drupal_core,
            major_version=current_parsed.major,
        )

        # Check for updates
        update_available, latest_version = self.comparator.is_update_available(
            current_version, compatible_versions
        )

        # Check for security updates
        security_available, security_version = (
            self.comparator.is_security_update_available(
                current_version, compatible_versions
            )
        )

        # Calculate version lag if update available
        version_lag = None
        if latest_version:
            version_lag = self.comparator.calculate_version_distance(
                current_version, latest_version
            )

        return UpdateInfo(
            current_version=current_version,
            latest_version=latest_version,
            latest_security_version=security_version,
            update_available=update_available,
            security_update_available=security_available,
            version_lag=version_lag,
        )

    async def check_site_module_updates(
        self, db: AsyncSession, site_module_id: int
    ) -> UpdateInfo:
        """
        Check updates for a specific site module installation.

        Args:
            db: Database session
            site_module_id: SiteModule ID

        Returns:
            UpdateInfo object
        """
        # Get site module details
        result = await db.execute(
            select(SiteModule).where(SiteModule.id == site_module_id)
        )
        site_module = result.scalar_one_or_none()

        if not site_module or not site_module.current_version:
            return UpdateInfo(current_version="unknown")

        return await self.check_module_updates(
            db, site_module.module_id, site_module.current_version
        )

    async def batch_check_updates(
        self, db: AsyncSession, module_versions: List[Tuple[int, str]]
    ) -> Dict[int, UpdateInfo]:
        """
        Check updates for multiple modules efficiently.

        Args:
            db: Database session
            module_versions: List of (module_id, current_version) tuples

        Returns:
            Dictionary mapping module_id to UpdateInfo
        """
        results = {}

        # Get unique module IDs
        module_ids = list(set(mv[0] for mv in module_versions))

        # Batch fetch all versions for these modules
        stmt = (
            select(ModuleVersion.module_id, ModuleVersion.version_string)
            .where(ModuleVersion.module_id.in_(module_ids))
            .order_by(ModuleVersion.module_id, ModuleVersion.created_at.desc())
        )
        result = await db.execute(stmt)

        # Group versions by module
        module_version_map: Dict[int, List[str]] = {}
        async for module_id, version_string in result:
            if module_id not in module_version_map:
                module_version_map[module_id] = []
            module_version_map[module_id].append(version_string)

        # Check each module
        for module_id, current_version in module_versions:
            available_versions = module_version_map.get(module_id, [])

            if not available_versions:
                results[module_id] = UpdateInfo(current_version=current_version)
                continue

            # Parse current version
            try:
                current_parsed = self.parser.parse(current_version)
            except ValueError:
                results[module_id] = UpdateInfo(current_version=current_version)
                continue

            # Filter compatible versions
            compatible_versions = self.comparator.filter_compatible_versions(
                available_versions,
                drupal_core=current_parsed.drupal_core,
                major_version=current_parsed.major,
            )

            # Check for updates
            update_available, latest_version = self.comparator.is_update_available(
                current_version, compatible_versions
            )

            # Check for security updates
            security_available, security_version = (
                self.comparator.is_security_update_available(
                    current_version, compatible_versions
                )
            )

            # Calculate version lag
            version_lag = None
            if latest_version:
                version_lag = self.comparator.calculate_version_distance(
                    current_version, latest_version
                )

            results[module_id] = UpdateInfo(
                current_version=current_version,
                latest_version=latest_version,
                latest_security_version=security_version,
                update_available=update_available,
                security_update_available=security_available,
                version_lag=version_lag,
            )

        return results

    async def update_site_module_flags(
        self, db: AsyncSession, site_module: SiteModule, update_info: UpdateInfo
    ) -> None:
        """
        Update the database flags for a site module based on update availability.

        Args:
            db: Database session
            site_module: SiteModule instance to update
            update_info: Update information
        """
        site_module.update_available = update_info.update_available
        site_module.security_update_available = update_info.security_update_available
        site_module.latest_version = update_info.latest_version
        site_module.last_updated = datetime.utcnow()

        await db.commit()

    async def get_modules_needing_check(
        self, db: AsyncSession, limit: int = 100
    ) -> List[Tuple[int, str]]:
        """
        Get unique module/version combinations that need checking.

        Args:
            db: Database session
            limit: Maximum number of combinations to return

        Returns:
            List of (module_id, version) tuples
        """
        # Get distinct module/version combinations from site_modules
        stmt = (
            select(SiteModule.module_id, SiteModule.current_version)
            .distinct()
            .where(
                and_(SiteModule.current_version.isnot(None), SiteModule.enabled == True)
            )
            .limit(limit)
        )

        result = await db.execute(stmt)
        return [(row[0], row[1]) for row in await result.fetchall()]

    def get_version_branch(self, version: str) -> Optional[str]:
        """
        Get the branch identifier for a version.

        Args:
            version: Version string

        Returns:
            Branch identifier (e.g., "8.x-1.x", "2.x")
        """
        try:
            parsed = self.parser.parse(version)
            if parsed.drupal_core:
                return f"{parsed.drupal_core}-{parsed.major}.x"
            else:
                return f"{parsed.major}.x"
        except ValueError:
            return None
