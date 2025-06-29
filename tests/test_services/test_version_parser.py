"""Tests for version parser service."""

import pytest
from app.services.version_parser import DrupalVersionParser, ParsedVersion, ReleaseType


class TestVersionParser:
    """Test cases for DrupalVersionParser."""
    
    @pytest.mark.parametrize("version,expected", [
        # Drupal contrib format
        ("8.x-1.0", {
            "drupal_core": "8.x",
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.STABLE,
            "release_number": None,
            "extra": None
        }),
        ("7.x-2.5", {
            "drupal_core": "7.x",
            "major": 2,
            "minor": 5,
            "patch": 0,
            "release_type": ReleaseType.STABLE,
            "release_number": None,
            "extra": None
        }),
        ("8.x-1.0-beta1", {
            "drupal_core": "8.x",
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.BETA,
            "release_number": 1,
            "extra": None
        }),
        ("9.x-2.3-alpha2", {
            "drupal_core": "9.x",
            "major": 2,
            "minor": 3,
            "patch": 0,
            "release_type": ReleaseType.ALPHA,
            "release_number": 2,
            "extra": None
        }),
        ("8.x-1.0-rc1", {
            "drupal_core": "8.x",
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.RC,
            "release_number": 1,
            "extra": None
        }),
        ("8.x-1.0-security1", {
            "drupal_core": "8.x",
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.SECURITY,
            "release_number": 1,
            "extra": None
        }),
        ("8.x-1.0+5", {
            "drupal_core": "8.x",
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.STABLE,
            "release_number": None,
            "extra": "5"
        }),
        # Drupal dev versions
        ("8.x-1.x-dev", {
            "drupal_core": "8.x",
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.DEV,
            "release_number": None,
            "extra": None
        }),
        ("7.x-2.x-dev", {
            "drupal_core": "7.x",
            "major": 2,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.DEV,
            "release_number": None,
            "extra": None
        }),
        # Semantic versioning
        ("1.0.0", {
            "drupal_core": None,
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.STABLE,
            "release_number": None,
            "extra": None
        }),
        ("2.1.5", {
            "drupal_core": None,
            "major": 2,
            "minor": 1,
            "patch": 5,
            "release_type": ReleaseType.STABLE,
            "release_number": None,
            "extra": None
        }),
        ("3.0.0-beta1", {
            "drupal_core": None,
            "major": 3,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.BETA,
            "release_number": 1,
            "extra": None
        }),
        ("1.0.0-alpha2", {
            "drupal_core": None,
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.ALPHA,
            "release_number": 2,
            "extra": None
        }),
        ("2.0.0-rc3", {
            "drupal_core": None,
            "major": 2,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.RC,
            "release_number": 3,
            "extra": None
        }),
        ("1.0.0-security1", {
            "drupal_core": None,
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.SECURITY,
            "release_number": 1,
            "extra": None
        }),
        ("1.0.0+build123", {
            "drupal_core": None,
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.STABLE,
            "release_number": None,
            "extra": "build123"
        }),
        # Semantic dev versions
        ("1.x-dev", {
            "drupal_core": None,
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.DEV,
            "release_number": None,
            "extra": None
        }),
        ("2.0.x-dev", {
            "drupal_core": None,
            "major": 2,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.DEV,
            "release_number": None,
            "extra": None
        }),
        # Simple format
        ("1.0", {
            "drupal_core": None,
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.STABLE,
            "release_number": None,
            "extra": None
        }),
        ("2.5", {
            "drupal_core": None,
            "major": 2,
            "minor": 5,
            "patch": 0,
            "release_type": ReleaseType.STABLE,
            "release_number": None,
            "extra": None
        }),
        # Drupal core style
        ("9.5.11", {
            "drupal_core": None,
            "major": 9,
            "minor": 5,
            "patch": 11,
            "release_type": ReleaseType.STABLE,
            "release_number": None,
            "extra": None
        }),
        ("10.1.6", {
            "drupal_core": None,
            "major": 10,
            "minor": 1,
            "patch": 6,
            "release_type": ReleaseType.STABLE,
            "release_number": None,
            "extra": None
        }),
    ])
    def test_parse_versions(self, version, expected):
        """Test parsing various version formats."""
        parsed = DrupalVersionParser.parse(version)
        
        assert parsed.drupal_core == expected["drupal_core"]
        assert parsed.major == expected["major"]
        assert parsed.minor == expected["minor"]
        assert parsed.patch == expected["patch"]
        assert parsed.release_type == expected["release_type"]
        assert parsed.release_number == expected["release_number"]
        assert parsed.extra == expected["extra"]
        assert parsed.original == version
    
    def test_parse_invalid_versions(self):
        """Test parsing invalid version strings."""
        invalid_versions = [
            "invalid",
            "x.y.z",
            "8.x",
            "dev",
            "1.2.3.4",
            "8.x-",
            "-1.0.0",
            "8.x-1.0-invalid",
        ]
        
        for version in invalid_versions:
            with pytest.raises(ValueError, match=f"Unable to parse version string: {version}"):
                DrupalVersionParser.parse(version)
    
    def test_empty_version_string(self):
        """Test parsing empty version string."""
        with pytest.raises(ValueError, match="Version string cannot be empty"):
            DrupalVersionParser.parse("")
    
    def test_version_to_semantic(self):
        """Test conversion to semantic version string."""
        test_cases = [
            ("8.x-1.0", "1.0.0"),
            ("8.x-1.0-beta1", "1.0.0-beta1"),
            ("1.0.0", "1.0.0"),
            ("2.1.5", "2.1.5"),
            ("1.0.0-alpha2", "1.0.0-alpha2"),
            ("8.x-1.x-dev", "1.0.0-dev"),
            ("1.0.0+build123", "1.0.0+build123"),
            ("8.x-1.0-security1", "1.0.0-security1"),
        ]
        
        for original, expected in test_cases:
            parsed = DrupalVersionParser.parse(original)
            assert parsed.to_semantic() == expected
    
    def test_version_to_tuple(self):
        """Test conversion to comparison tuple."""
        test_cases = [
            ("1.0.0", (1, 0, 0, ReleaseType.STABLE.precedence, 0)),
            ("2.1.5", (2, 1, 5, ReleaseType.STABLE.precedence, 0)),
            ("1.0.0-alpha2", (1, 0, 0, ReleaseType.ALPHA.precedence, 2)),
            ("1.0.0-beta1", (1, 0, 0, ReleaseType.BETA.precedence, 1)),
            ("8.x-1.x-dev", (1, 0, 0, ReleaseType.DEV.precedence, 0)),
        ]
        
        for version, expected in test_cases:
            parsed = DrupalVersionParser.parse(version)
            assert parsed.to_tuple() == expected
    
    def test_is_valid(self):
        """Test version validation."""
        valid_versions = [
            "8.x-1.0",
            "1.0.0",
            "2.1.5-beta1",
            "8.x-1.x-dev",
            "10.1.6",
        ]
        
        for version in valid_versions:
            assert DrupalVersionParser.is_valid(version) is True
        
        invalid_versions = [
            "invalid",
            "x.y.z",
            "",
        ]
        
        for version in invalid_versions:
            assert DrupalVersionParser.is_valid(version) is False
    
    def test_normalize(self):
        """Test version normalization."""
        test_cases = [
            ("8.x-1.0", "1.0.0"),
            ("8.x-1.0-beta1", "1.0.0-beta1"),
            ("invalid", "invalid"),  # Returns original if can't parse
        ]
        
        for original, expected in test_cases:
            assert DrupalVersionParser.normalize(original) == expected
    
    def test_release_type_precedence(self):
        """Test release type precedence ordering."""
        assert ReleaseType.DEV < ReleaseType.ALPHA
        assert ReleaseType.ALPHA < ReleaseType.BETA
        assert ReleaseType.BETA < ReleaseType.RC
        assert ReleaseType.RC < ReleaseType.STABLE
        assert ReleaseType.STABLE < ReleaseType.SECURITY
    
    def test_case_insensitive_release_types(self):
        """Test that release types are parsed case-insensitively."""
        test_cases = [
            ("1.0.0-BETA1", ReleaseType.BETA),
            ("1.0.0-Alpha2", ReleaseType.ALPHA),
            ("1.0.0-RC1", ReleaseType.RC),
            ("8.x-1.x-DEV", ReleaseType.DEV),
            ("1.0.0-Security1", ReleaseType.SECURITY),
        ]
        
        for version, expected_type in test_cases:
            parsed = DrupalVersionParser.parse(version)
            assert parsed.release_type == expected_type