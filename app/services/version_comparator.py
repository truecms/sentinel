"""
Version comparison service for Drupal module versions.

Implements comparison logic following Drupal version conventions.
"""

from typing import Dict, List, Optional, Tuple

from app.services.version_parser import (DrupalVersionParser, ParsedVersion,
                                         ReleaseType)


class VersionComparator:
    """Service for comparing Drupal module versions."""

    def __init__(self):
        self.parser = DrupalVersionParser()

    def compare(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            -1 if version1 < version2
            0 if version1 == version2
            1 if version1 > version2

        Raises:
            ValueError: If either version string is invalid
        """
        parsed1 = self.parser.parse(version1)
        parsed2 = self.parser.parse(version2)

        # First check Drupal core compatibility
        if parsed1.drupal_core and parsed2.drupal_core:
            if parsed1.drupal_core != parsed2.drupal_core:
                # Different Drupal core versions are not comparable
                # Use numeric comparison of core version
                core1 = int(parsed1.drupal_core.replace(".x", ""))
                core2 = int(parsed2.drupal_core.replace(".x", ""))
                return -1 if core1 < core2 else 1
        elif parsed1.drupal_core and not parsed2.drupal_core:
            # Drupal contrib versions are considered newer than semantic versions
            return 1
        elif not parsed1.drupal_core and parsed2.drupal_core:
            # Semantic versions are considered older than Drupal contrib versions
            return -1

        # Compare version tuples
        tuple1 = parsed1.to_tuple()
        tuple2 = parsed2.to_tuple()

        if tuple1 < tuple2:
            return -1
        elif tuple1 > tuple2:
            return 1
        else:
            return 0

    def get_latest_version(
        self, versions: List[str], stable_only: bool = False
    ) -> Optional[str]:
        """
        Find the latest version from a list.

        Args:
            versions: List of version strings
            stable_only: If True, only consider stable and security releases

        Returns:
            Latest version string or None if list is empty
        """
        if not versions:
            return None

        valid_versions = []
        for version in versions:
            try:
                parsed = self.parser.parse(version)
                if stable_only and parsed.release_type not in [
                    ReleaseType.STABLE,
                    ReleaseType.SECURITY,
                ]:
                    continue
                valid_versions.append(version)
            except ValueError:
                # Skip invalid versions
                continue

        if not valid_versions:
            return None

        # Sort versions using custom key that includes drupal core
        def version_sort_key(version_str):
            parsed = self.parser.parse(version_str)
            # Include drupal core in the sorting key
            core_value = 0
            if parsed.drupal_core:
                core_value = int(parsed.drupal_core.replace(".x", ""))
            return (
                core_value,
                parsed.major,
                parsed.minor,
                parsed.patch,
                parsed.release_type.precedence,
                parsed.release_number or 0,
            )

        return max(valid_versions, key=version_sort_key)

    def is_update_available(
        self, current: str, available: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if an update is available.

        Args:
            current: Current version string
            available: List of available version strings

        Returns:
            Tuple of (update_available, latest_version)
        """
        latest = self.get_latest_version(available, stable_only=True)
        if not latest:
            return False, None

        comparison = self.compare(current, latest)
        return comparison < 0, latest if comparison < 0 else None

    def is_security_update_available(
        self, current: str, available: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a security update is available.

        Args:
            current: Current version string
            available: List of available version strings

        Returns:
            Tuple of (security_update_available, security_version)
        """
        try:
            current_parsed = self.parser.parse(current)
        except ValueError:
            return False, None

        security_versions = []
        for version in available:
            try:
                parsed = self.parser.parse(version)
                # Check if it's a security release and newer than current
                if (
                    parsed.release_type == ReleaseType.SECURITY
                    and self.compare(current, version) < 0
                ):
                    # If Drupal core versions exist, they must match
                    if current_parsed.drupal_core and parsed.drupal_core:
                        if current_parsed.drupal_core != parsed.drupal_core:
                            continue
                    security_versions.append(version)
            except ValueError:
                continue

        if not security_versions:
            return False, None

        latest_security = self.get_latest_version(security_versions)
        return True, latest_security

    def group_versions_by_branch(self, versions: List[str]) -> Dict[str, List[str]]:
        """
        Group versions by their branch (major version or Drupal core).

        Args:
            versions: List of version strings

        Returns:
            Dictionary mapping branch to list of versions
        """
        branches = {}

        for version in versions:
            try:
                parsed = self.parser.parse(version)

                # Determine branch key
                if parsed.drupal_core:
                    # For Drupal contrib modules
                    branch = f"{parsed.drupal_core}-{parsed.major}.x"
                else:
                    # For semantic versioning
                    branch = f"{parsed.major}.x"

                if branch not in branches:
                    branches[branch] = []
                branches[branch].append(version)

            except ValueError:
                # Skip invalid versions
                continue

        # Sort versions within each branch
        def version_sort_key(version_str):
            parsed = self.parser.parse(version_str)
            return parsed.to_tuple()

        for branch in branches:
            branches[branch].sort(key=version_sort_key)

        return branches

    def filter_compatible_versions(
        self,
        versions: List[str],
        drupal_core: Optional[str] = None,
        major_version: Optional[int] = None,
    ) -> List[str]:
        """
        Filter versions by compatibility criteria.

        Args:
            versions: List of version strings
            drupal_core: Drupal core version to filter by (e.g., "9.x")
            major_version: Major version to filter by

        Returns:
            List of compatible versions
        """
        compatible = []

        for version in versions:
            try:
                parsed = self.parser.parse(version)

                # Check Drupal core compatibility
                if drupal_core:
                    # If filtering by drupal_core, only include versions that have drupal_core
                    if not parsed.drupal_core:
                        continue
                    if parsed.drupal_core != drupal_core:
                        continue

                # Check major version
                if major_version is not None:
                    if parsed.major != major_version:
                        continue

                compatible.append(version)

            except ValueError:
                continue

        return compatible

    def calculate_version_distance(
        self, version1: str, version2: str
    ) -> Dict[str, int]:
        """
        Calculate the distance between two versions.

        Args:
            version1: First version
            version2: Second version

        Returns:
            Dictionary with major, minor, patch differences
        """
        parsed1 = self.parser.parse(version1)
        parsed2 = self.parser.parse(version2)

        return {
            "major": abs(parsed2.major - parsed1.major),
            "minor": abs(parsed2.minor - parsed1.minor),
            "patch": abs(parsed2.patch - parsed1.patch),
            "release_type_diff": parsed2.release_type.precedence
            - parsed1.release_type.precedence,
        }
