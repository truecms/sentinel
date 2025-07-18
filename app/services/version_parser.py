"""
Version parsing service for Drupal module versions.

Handles various version formats used in the Drupal ecosystem:
- Drupal contrib: 8.x-1.0, 7.x-2.5-beta1
- Semantic versioning: 1.0.0, 2.1.0-alpha2
- Dev versions: 8.x-1.x-dev, 2.0.x-dev
- Security releases: 8.x-1.0-security1
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class ReleaseType(Enum):
    """Types of releases ordered by precedence."""

    _ = "dev"
    _ = "alpha"
    _ = "beta"
    _ = "rc"
    _ = "stable"
    _ = "security"

    @property
    def precedence(self) -> int:
        """Get precedence value for comparison (higher is newer)."""
        precedence_map = {
            self.DEV: 0,
            self.ALPHA: 1,
            self.BETA: 2,
            self.RC: 3,
            self.STABLE: 4,
            self.SECURITY: 5,
        }
        return precedence_map[self]

    def __lt__(self, other):
        if not isinstance(other, ReleaseType):
            return NotImplemented
        return self.precedence < other.precedence


@dataclass
class ParsedVersion:
    """Parsed version components."""

    drupal_core: Optional[str] = None  # "8.x", "9.x", etc.
    major: int = 0
    minor: int = 0
    patch: int = 0
    release_type: ReleaseType = ReleaseType.STABLE
    release_number: Optional[int] = None  # For beta1, alpha2, etc.
    extra: Optional[str] = None  # Additional suffixes
    original: str = ""  # Original version string

    def to_semantic(self) -> str:
        """Convert to semantic version string."""
        version = f"{self.major}.{self.minor}.{self.patch}"

        if self.release_type != ReleaseType.STABLE:
            version += f"-{self.release_type.value}"
            if self.release_number is not None:
                version += str(self.release_number)

        if self.extra:
            version += f"+{self.extra}"

        return version

    def to_tuple(self) -> Tuple:
        """Convert to tuple for comparison."""
        return (
            self.major,
            self.minor,
            self.patch,
            self.release_type.precedence,
            self.release_number or 0,
        )


class DrupalVersionParser:
    """Parser for Drupal module versions."""

    # Regex patterns for different version formats
    _ = {
        # Drupal contrib format: 8.x-1.0, 7.x-2.5-beta1, 8.x-1.0+5
        "drupal_contrib": re.compile(
            r"^(\d+)\.x-(\d+)\.(\d+)"
            r"(?:-?(alpha|beta|rc|dev|security)(\d+)?)?"
            r"(?:\+(.+))?$",
            re.IGNORECASE,
        ),
        # Drupal contrib dev: 8.x-1.x-dev, 7.x-2.x-dev
        "drupal_dev": re.compile(r"^(\d+)\.x-(\d+)\.x-dev$", re.IGNORECASE),
        # Semantic versioning: 1.0.0, 2.1.0-alpha2, 3.0.0-beta1+build123
        "semantic": re.compile(
            r"^(\d+)\.(\d+)\.(\d+)"
            r"(?:-?(alpha|beta|rc|dev|security)(\d+)?)?"
            r"(?:\+(.+))?$",
            re.IGNORECASE,
        ),
        # Semantic dev: 1.x-dev, 2.0.x-dev
        "semantic_dev": re.compile(r"^(\d+)(?:\.(\d+))?\.x-dev$", re.IGNORECASE),
        # Simple numeric: 1.0, 2.5
        "simple": re.compile(r"^(\d+)\.(\d+)$"),
        # Drupal core style: 9.5.11, 10.1.6
        "drupal_core": re.compile(r"^(\d+)\.(\d+)\.(\d+)$"),
    }

    @classmethod
    def parse(cls, version_string: str) -> ParsedVersion:
        """
        Parse a version string into components.

        Args:
            version_string: Version string to parse

        Returns:
            ParsedVersion object with parsed components
        """
        if not version_string:
            raise ValueError("Version string cannot be empty")

        # Clean the version string
        version_string = version_string.strip()

        # Try Drupal contrib format first
        match = cls.PATTERNS["drupal_contrib"].match(version_string)
        if match:
            drupal_core, major, minor, release_type, release_num, extra = match.groups()
            return ParsedVersion(
                drupal_core=f"{drupal_core}.x",
                major=int(major),
                minor=int(minor),
                patch=0,
                release_type=cls._parse_release_type(release_type),
                release_number=int(release_num) if release_num else None,
                extra=extra,
                original=version_string,
            )

        # Try Drupal contrib dev format
        match = cls.PATTERNS["drupal_dev"].match(version_string)
        if match:
            drupal_core, major = match.groups()
            return ParsedVersion(
                drupal_core=f"{drupal_core}.x",
                major=int(major),
                minor=0,
                patch=0,
                release_type=ReleaseType.DEV,
                original=version_string,
            )

        # Try semantic versioning
        match = cls.PATTERNS["semantic"].match(version_string)
        if match:
            major, minor, patch, release_type, release_num, extra = match.groups()
            return ParsedVersion(
                major=int(major),
                minor=int(minor),
                patch=int(patch),
                release_type=cls._parse_release_type(release_type),
                release_num=int(release_num) if release_num else None,
                extra=extra,
                original=version_string,
            )

        # Try semantic dev
        match = cls.PATTERNS["semantic_dev"].match(version_string)
        if match:
            major, minor = match.groups()
            return ParsedVersion(
                major=int(major),
                minor=int(minor) if minor else 0,
                patch=0,
                release_type=ReleaseType.DEV,
                original=version_string,
            )

        # Try simple format
        match = cls.PATTERNS["simple"].match(version_string)
        if match:
            major, minor = match.groups()
            return ParsedVersion(
                major=int(major),
                minor=int(minor),
                patch=0,
                release_type=ReleaseType.STABLE,
                original=version_string,
            )

        # Try Drupal core style (same as semantic but explicitly named)
        match = cls.PATTERNS["drupal_core"].match(version_string)
        if match:
            major, minor, patch = match.groups()
            return ParsedVersion(
                major=int(major),
                minor=int(minor),
                patch=int(patch),
                release_type=ReleaseType.STABLE,
                original=version_string,
            )

        # If no pattern matches, raise an error
        raise ValueError(f"Unable to parse version string: {version_string}")

    @staticmethod
    def _parse_release_type(release_type_str: Optional[str]) -> ReleaseType:
        """Parse release type string to enum."""
        if not release_type_str:
            return ReleaseType.STABLE

        release_type_str = release_type_str.lower()

        if release_type_str == "alpha":
            return ReleaseType.ALPHA
        elif release_type_str == "beta":
            return ReleaseType.BETA
        elif release_type_str == "rc":
            return ReleaseType.RC
        elif release_type_str == "dev":
            return ReleaseType.DEV
        elif release_type_str == "security":
            return ReleaseType.SECURITY
        else:
            return ReleaseType.STABLE

    @classmethod
    def is_valid(cls, version_string: str) -> bool:
        """Check if a version string is valid."""
        try:
            cls.parse(version_string)
            return True
        except ValueError:
            return False

    @classmethod
    def normalize(cls, version_string: str) -> str:
        """Normalize a version string to semantic version format."""
        try:
            parsed = cls.parse(version_string)
            return parsed.to_semantic()
        except ValueError:
            return version_string
