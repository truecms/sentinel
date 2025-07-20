"""Tests for version comparator service."""

import pytest

from app.services.version_comparator import VersionComparator


class TestVersionComparator:
    """Test cases for VersionComparator."""

    @pytest.fixture
    def comparator(self):
        """Create a VersionComparator instance."""
        return VersionComparator()

    @pytest.mark.parametrize(
        "version1,version2,expected",
        [
            # Same versions
            ("1.0.0", "1.0.0", 0),
            ("8.x-1.0", "8.x-1.0", 0),
            # Basic semantic versioning
            ("1.0.0", "2.0.0", -1),
            ("2.0.0", "1.0.0", 1),
            ("1.0.0", "1.1.0", -1),
            ("1.1.0", "1.0.0", 1),
            ("1.0.0", "1.0.1", -1),
            ("1.0.1", "1.0.0", 1),
            # Drupal contrib format
            ("8.x-1.0", "8.x-2.0", -1),
            ("8.x-2.0", "8.x-1.0", 1),
            ("8.x-1.0", "8.x-1.1", -1),
            ("8.x-1.1", "8.x-1.0", 1),
            # Different Drupal core versions
            ("7.x-1.0", "8.x-1.0", -1),
            ("8.x-1.0", "7.x-1.0", 1),
            ("9.x-1.0", "10.x-1.0", -1),
            # Pre-release versions
            ("1.0.0-alpha1", "1.0.0-beta1", -1),
            ("1.0.0-beta1", "1.0.0-alpha1", 1),
            ("1.0.0-beta1", "1.0.0-rc1", -1),
            ("1.0.0-rc1", "1.0.0", -1),
            ("1.0.0", "1.0.0-rc1", 1),
            # Dev versions
            ("1.0.0-dev", "1.0.0-alpha1", -1),
            ("8.x-1.x-dev", "8.x-1.0", -1),
            ("8.x-1.0", "8.x-1.x-dev", 1),
            # Security versions
            ("1.0.0", "1.0.0-security1", -1),
            ("1.0.0-security1", "1.0.0", 1),
            # Pre-release numbers
            ("1.0.0-beta1", "1.0.0-beta2", -1),
            ("1.0.0-beta2", "1.0.0-beta1", 1),
            ("1.0.0-alpha1", "1.0.0-alpha10", -1),
            # Mixed formats
            ("8.x-1.0", "1.0.0", 1),  # 8.x > no core version
            ("1.0.0", "8.x-1.0", -1),
        ],
    )
    def test_compare(self, comparator, version1, version2, expected):
        """Test version comparison."""
        result = comparator.compare(version1, version2)
        assert result == expected

    def test_get_latest_version(self, comparator):
        """Test finding the latest version from a list."""
        versions = [
            "1.0.0",
            "1.1.0",
            "2.0.0-beta1",
            "1.2.0",
            "1.0.0-alpha1",
            "2.0.0",
            "1.3.0-rc1",
        ]

        # Include all versions
        latest = comparator.get_latest_version(versions, stable_only=False)
        assert latest == "2.0.0"

        # Only stable versions
        latest_stable = comparator.get_latest_version(versions, stable_only=True)
        assert latest_stable == "2.0.0"

        # List with only pre-releases
        pre_releases = ["1.0.0-alpha1", "1.0.0-beta1", "1.0.0-rc1"]
        latest_pre = comparator.get_latest_version(pre_releases, stable_only=False)
        assert latest_pre == "1.0.0-rc1"

        latest_stable_pre = comparator.get_latest_version(
            pre_releases, stable_only=True
        )
        assert latest_stable_pre is None

        # Empty list
        assert comparator.get_latest_version([]) is None

        # List with invalid versions
        mixed_versions = ["1.0.0", "invalid", "2.0.0", "not-a-version"]
        latest_mixed = comparator.get_latest_version(mixed_versions)
        assert latest_mixed == "2.0.0"

    def test_get_latest_version_drupal(self, comparator):
        """Test finding latest version with Drupal format."""
        versions = [
            "8.x-1.0",
            "8.x-1.1",
            "8.x-2.0-beta1",
            "8.x-1.2",
            "8.x-2.0",
            "7.x-3.0",  # Different core
            "9.x-1.0",  # Different core
        ]

        # When we have mixed Drupal core versions, the highest core version wins
        latest = comparator.get_latest_version(versions)
        assert latest == "9.x-1.0"

    def test_is_update_available(self, comparator):
        """Test update availability detection."""
        # Update available
        available = ["1.0.0", "1.1.0", "1.2.0", "2.0.0-beta1"]
        has_update, latest = comparator.is_update_available("1.0.0", available)
        assert has_update is True
        assert latest == "1.2.0"  # Latest stable

        # No update available
        has_update, latest = comparator.is_update_available("1.2.0", available)
        assert has_update is False
        assert latest is None

        # Current version is newer
        has_update, latest = comparator.is_update_available("2.0.0", available)
        assert has_update is False
        assert latest is None

        # Empty available list
        has_update, latest = comparator.is_update_available("1.0.0", [])
        assert has_update is False
        assert latest is None

    def test_is_security_update_available(self, comparator):
        """Test security update detection."""
        # Security update available
        available = ["1.0.0", "1.1.0", "1.1.0-security1", "1.2.0", "2.0.0-security1"]

        has_security, version = comparator.is_security_update_available(
            "1.0.0", available
        )
        assert has_security is True
        assert version == "2.0.0-security1"

        # No security update
        has_security, version = comparator.is_security_update_available(
            "2.0.0-security1", available
        )
        assert has_security is False
        assert version is None

        # Drupal core compatibility
        drupal_versions = [
            "8.x-1.0",
            "8.x-1.0-security1",
            "9.x-1.0-security1",  # Different core
        ]

        has_security, version = comparator.is_security_update_available(
            "8.x-1.0", drupal_versions
        )
        assert has_security is True
        assert version == "8.x-1.0-security1"

    def test_group_versions_by_branch(self, comparator):
        """Test grouping versions by branch."""
        versions = [
            "8.x-1.0",
            "8.x-1.1",
            "8.x-2.0",
            "8.x-2.1",
            "9.x-1.0",
            "9.x-1.1",
            "1.0.0",
            "1.1.0",
            "2.0.0",
        ]

        branches = comparator.group_versions_by_branch(versions)

        assert "8.x-1.x" in branches
        assert branches["8.x-1.x"] == ["8.x-1.0", "8.x-1.1"]

        assert "8.x-2.x" in branches
        assert branches["8.x-2.x"] == ["8.x-2.0", "8.x-2.1"]

        assert "9.x-1.x" in branches
        assert branches["9.x-1.x"] == ["9.x-1.0", "9.x-1.1"]

        assert "1.x" in branches
        assert branches["1.x"] == ["1.0.0", "1.1.0"]

        assert "2.x" in branches
        assert branches["2.x"] == ["2.0.0"]

    def test_filter_compatible_versions(self, comparator):
        """Test filtering versions by compatibility."""
        versions = [
            "8.x-1.0",
            "8.x-1.1",
            "8.x-2.0",
            "9.x-1.0",
            "9.x-2.0",
            "1.0.0",
            "2.0.0",
        ]

        # Filter by Drupal core
        drupal8 = comparator.filter_compatible_versions(versions, drupal_core="8.x")
        assert set(drupal8) == {"8.x-1.0", "8.x-1.1", "8.x-2.0"}

        # Filter by major version
        major1 = comparator.filter_compatible_versions(versions, major_version=1)
        assert set(major1) == {"8.x-1.0", "8.x-1.1", "9.x-1.0", "1.0.0"}

        # Filter by both
        drupal8_major1 = comparator.filter_compatible_versions(
            versions, drupal_core="8.x", major_version=1
        )
        assert set(drupal8_major1) == {"8.x-1.0", "8.x-1.1"}

    def test_calculate_version_distance(self, comparator):
        """Test calculating distance between versions."""
        distance = comparator.calculate_version_distance("1.0.0", "2.1.3")
        assert distance["major"] == 1
        assert distance["minor"] == 1
        assert distance["patch"] == 3
        assert distance["release_type_diff"] == 0  # Both stable

        # With pre-release
        distance = comparator.calculate_version_distance("1.0.0-beta1", "1.0.0")
        assert distance["major"] == 0
        assert distance["minor"] == 0
        assert distance["patch"] == 0
        assert distance["release_type_diff"] == 2  # beta to stable

        # Drupal format
        distance = comparator.calculate_version_distance("8.x-1.0", "8.x-2.1")
        assert distance["major"] == 1
        assert distance["minor"] == 1
        assert distance["patch"] == 0
