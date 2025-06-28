# Issue 1.4: Add Module Version Comparison Logic

**Type**: Feature
**Priority**: P0 - Critical
**Epic**: Core Module Monitoring System
**Estimated Effort**: 2 days
**Labels**: `backend`, `logic`, `version-management`, `priority-critical`
**Dependencies**: Issue 1.1 (Database Models), Issue 1.3 (Data Ingestion)

## Description
Implement robust version comparison logic to accurately determine when module updates are available, identify the latest versions, and handle the complex version naming schemes used in the Drupal ecosystem.

## Background
Drupal modules use various version formats:
- Core modules: `9.5.11`, `10.1.6`
- Contrib modules: `8.x-1.0`, `7.x-2.5`, `4.0.0`
- Dev versions: `8.x-1.x-dev`, `2.0.x-dev`
- Pre-releases: `8.x-1.0-beta1`, `3.0.0-alpha2`, `2.1.0-rc1`
- Custom/special: `8.x-1.0+5`, `2.0.0-security1`

The system must correctly:
- Parse and normalize these versions
- Compare versions to determine which is newer
- Identify stable vs development releases
- Respect Drupal core compatibility

## Technical Specification

### Version Parser Service

#### Version Parser (`app/services/version_parser.py`)
```python
import re
from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

class ReleaseType(Enum):
    """Types of releases."""
    STABLE = "stable"
    ALPHA = "alpha"
    BETA = "beta"
    RC = "rc"
    DEV = "dev"
    SECURITY = "security"

@dataclass
class ParsedVersion:
    """Parsed version components."""
    drupal_core: Optional[str]  # "8.x", "9.x", etc.
    major: int
    minor: int
    patch: int
    release_type: ReleaseType
    release_number: Optional[int]  # For beta1, alpha2, etc.
    extra: Optional[str]  # Additional suffixes
    original: str  # Original version string
    
    @property
    def is_stable(self) -> bool:
        """Check if this is a stable release."""
        return self.release_type == ReleaseType.STABLE
    
    @property
    def is_security(self) -> bool:
        """Check if this is a security release."""
        return self.release_type == ReleaseType.SECURITY
    
    @property
    def semantic_version(self) -> str:
        """Get semantic version string."""
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.release_type != ReleaseType.STABLE:
            base += f"-{self.release_type.value}"
            if self.release_number:
                base += str(self.release_number)
        return base
    
    def to_comparable_tuple(self) -> Tuple:
        """Convert to tuple for comparison."""
        # Release type ordering: dev < alpha < beta < rc < stable < security
        type_order = {
            ReleaseType.DEV: 0,
            ReleaseType.ALPHA: 1,
            ReleaseType.BETA: 2,
            ReleaseType.RC: 3,
            ReleaseType.STABLE: 4,
            ReleaseType.SECURITY: 5
        }
        
        return (
            self.major,
            self.minor,
            self.patch,
            type_order[self.release_type],
            self.release_number or 999  # Stable releases get high number
        )

class DrupalVersionParser:
    """Parser for Drupal version strings."""
    
    # Regex patterns for different version formats
    PATTERNS = {
        # 8.x-1.0, 7.x-2.5-beta1
        'drupal_contrib': re.compile(
            r'^(\d+)\.x-(\d+)\.(\d+)(?:-(\w+)(\d+)?)?(?:\+(.+))?$'
        ),
        # 1.0.0, 2.5.3-beta1
        'semantic': re.compile(
            r'^(\d+)\.(\d+)\.(\d+)(?:-(\w+)(\d+)?)?(?:\+(.+))?$'
        ),
        # 8.x-1.x-dev
        'dev': re.compile(
            r'^(?:(\d+)\.x-)?(\d+)\.x-dev$'
        ),
        # 9.5.11 (core style)
        'core': re.compile(
            r'^(\d+)\.(\d+)\.(\d+)$'
        )
    }
    
    def parse(self, version_string: str) -> ParsedVersion:
        """Parse a Drupal version string."""
        version_string = version_string.strip()
        
        # Try each pattern
        for pattern_name, pattern in self.PATTERNS.items():
            match = pattern.match(version_string)
            if match:
                return self._parse_match(match, pattern_name, version_string)
        
        # If no pattern matches, try to extract basic numbers
        return self._parse_fallback(version_string)
    
    def _parse_match(
        self,
        match: re.Match,
        pattern_name: str,
        original: str
    ) -> ParsedVersion:
        """Parse based on regex match."""
        groups = match.groups()
        
        if pattern_name == 'drupal_contrib':
            # 8.x-1.0-beta1 format
            drupal_core = f"{groups[0]}.x"
            major = int(groups[1])
            minor = int(groups[2]) if groups[2] else 0
            patch = 0
            release_type, release_number = self._parse_release_type(groups[3], groups[4])
            extra = groups[5]
            
        elif pattern_name == 'semantic':
            # 1.0.0-beta1 format
            drupal_core = None
            major = int(groups[0])
            minor = int(groups[1])
            patch = int(groups[2])
            release_type, release_number = self._parse_release_type(groups[3], groups[4])
            extra = groups[5]
            
        elif pattern_name == 'dev':
            # 8.x-1.x-dev format
            drupal_core = f"{groups[0]}.x" if groups[0] else None
            major = int(groups[1])
            minor = 0
            patch = 0
            release_type = ReleaseType.DEV
            release_number = None
            extra = None
            
        elif pattern_name == 'core':
            # 9.5.11 format
            drupal_core = None
            major = int(groups[0])
            minor = int(groups[1])
            patch = int(groups[2])
            release_type = ReleaseType.STABLE
            release_number = None
            extra = None
        
        return ParsedVersion(
            drupal_core=drupal_core,
            major=major,
            minor=minor,
            patch=patch,
            release_type=release_type,
            release_number=release_number,
            extra=extra,
            original=original
        )
    
    def _parse_release_type(
        self,
        type_str: Optional[str],
        number_str: Optional[str]
    ) -> Tuple[ReleaseType, Optional[int]]:
        """Parse release type and number."""
        if not type_str:
            return ReleaseType.STABLE, None
        
        type_lower = type_str.lower()
        number = int(number_str) if number_str else None
        
        if type_lower in ['alpha', 'a']:
            return ReleaseType.ALPHA, number
        elif type_lower in ['beta', 'b']:
            return ReleaseType.BETA, number
        elif type_lower in ['rc', 'release-candidate']:
            return ReleaseType.RC, number
        elif type_lower == 'dev':
            return ReleaseType.DEV, number
        elif type_lower == 'security':
            return ReleaseType.SECURITY, number
        else:
            return ReleaseType.STABLE, None
    
    def _parse_fallback(self, version_string: str) -> ParsedVersion:
        """Fallback parser for non-standard versions."""
        # Extract any numbers we can find
        numbers = re.findall(r'\d+', version_string)
        major = int(numbers[0]) if len(numbers) > 0 else 0
        minor = int(numbers[1]) if len(numbers) > 1 else 0
        patch = int(numbers[2]) if len(numbers) > 2 else 0
        
        # Check for common keywords
        release_type = ReleaseType.STABLE
        if 'dev' in version_string.lower():
            release_type = ReleaseType.DEV
        elif 'beta' in version_string.lower():
            release_type = ReleaseType.BETA
        elif 'alpha' in version_string.lower():
            release_type = ReleaseType.ALPHA
        elif 'rc' in version_string.lower():
            release_type = ReleaseType.RC
        
        return ParsedVersion(
            drupal_core=None,
            major=major,
            minor=minor,
            patch=patch,
            release_type=release_type,
            release_number=None,
            extra=None,
            original=version_string
        )
```

### Version Comparison Service

#### Version Comparator (`app/services/version_comparator.py`)
```python
from typing import List, Optional, Dict, Tuple
from app.services.version_parser import DrupalVersionParser, ParsedVersion
import logging

logger = logging.getLogger(__name__)

class VersionComparator:
    """Service for comparing Drupal module versions."""
    
    def __init__(self):
        self.parser = DrupalVersionParser()
    
    def compare(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.
        
        Returns:
            -1 if version1 < version2
            0 if version1 == version2
            1 if version1 > version2
        """
        try:
            parsed1 = self.parser.parse(version1)
            parsed2 = self.parser.parse(version2)
            
            # Compare Drupal core compatibility first if both have it
            if parsed1.drupal_core and parsed2.drupal_core:
                if parsed1.drupal_core != parsed2.drupal_core:
                    # Different core versions are not comparable
                    core1 = int(parsed1.drupal_core.split('.')[0])
                    core2 = int(parsed2.drupal_core.split('.')[0])
                    return -1 if core1 < core2 else 1
            
            # Compare version tuples
            tuple1 = parsed1.to_comparable_tuple()
            tuple2 = parsed2.to_comparable_tuple()
            
            if tuple1 < tuple2:
                return -1
            elif tuple1 > tuple2:
                return 1
            else:
                return 0
                
        except Exception as e:
            logger.warning(f"Error comparing versions {version1} and {version2}: {str(e)}")
            # Fallback to string comparison
            return -1 if version1 < version2 else (1 if version1 > version2 else 0)
    
    def get_latest_version(
        self,
        versions: List[str],
        stable_only: bool = False,
        drupal_core: Optional[str] = None
    ) -> Optional[str]:
        """
        Get the latest version from a list.
        
        Args:
            versions: List of version strings
            stable_only: Only consider stable releases
            drupal_core: Filter by Drupal core compatibility
        
        Returns:
            Latest version string or None if no matching versions
        """
        if not versions:
            return None
        
        parsed_versions = []
        for version in versions:
            try:
                parsed = self.parser.parse(version)
                
                # Apply filters
                if stable_only and not parsed.is_stable:
                    continue
                
                if drupal_core and parsed.drupal_core and parsed.drupal_core != drupal_core:
                    continue
                
                parsed_versions.append(parsed)
            except Exception as e:
                logger.warning(f"Error parsing version {version}: {str(e)}")
                continue
        
        if not parsed_versions:
            return None
        
        # Sort by comparable tuple (highest first)
        parsed_versions.sort(key=lambda v: v.to_comparable_tuple(), reverse=True)
        return parsed_versions[0].original
    
    def is_update_available(
        self,
        current_version: str,
        available_versions: List[str],
        include_unstable: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if an update is available.
        
        Returns:
            Tuple of (update_available, latest_version)
        """
        try:
            current_parsed = self.parser.parse(current_version)
            
            # Filter available versions
            candidates = []
            for version in available_versions:
                parsed = self.parser.parse(version)
                
                # Skip if different Drupal core
                if (current_parsed.drupal_core and 
                    parsed.drupal_core and 
                    current_parsed.drupal_core != parsed.drupal_core):
                    continue
                
                # Skip unstable if not requested
                if not include_unstable and not parsed.is_stable:
                    continue
                
                # Only consider newer versions
                if self.compare(version, current_version) > 0:
                    candidates.append(version)
            
            if not candidates:
                return False, None
            
            latest = self.get_latest_version(candidates)
            return True, latest
            
        except Exception as e:
            logger.error(f"Error checking updates: {str(e)}")
            return False, None
    
    def is_security_update_available(
        self,
        current_version: str,
        available_versions: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a security update is available.
        
        Returns:
            Tuple of (security_update_available, security_version)
        """
        try:
            current_parsed = self.parser.parse(current_version)
            
            security_versions = []
            for version in available_versions:
                parsed = self.parser.parse(version)
                
                # Must be newer and marked as security
                if (parsed.is_security and 
                    self.compare(version, current_version) > 0):
                    security_versions.append(version)
            
            if not security_versions:
                return False, None
            
            latest_security = self.get_latest_version(security_versions)
            return True, latest_security
            
        except Exception as e:
            logger.error(f"Error checking security updates: {str(e)}")
            return False, None
    
    def group_versions_by_branch(
        self,
        versions: List[str]
    ) -> Dict[str, List[str]]:
        """
        Group versions by their branch (major.minor).
        
        Returns:
            Dict mapping branch to list of versions
        """
        branches = {}
        
        for version in versions:
            try:
                parsed = self.parser.parse(version)
                
                # Determine branch key
                if parsed.drupal_core:
                    branch = f"{parsed.drupal_core}-{parsed.major}.x"
                else:
                    branch = f"{parsed.major}.{parsed.minor}.x"
                
                if branch not in branches:
                    branches[branch] = []
                branches[branch].append(version)
                
            except Exception as e:
                logger.warning(f"Error parsing version {version}: {str(e)}")
                # Put unparseable versions in 'unknown'
                if 'unknown' not in branches:
                    branches['unknown'] = []
                branches['unknown'].append(version)
        
        return branches
```

### Version Update Detection Service

#### Update Detector (`app/services/update_detector.py`)
```python
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models import Module, ModuleVersion, SiteModule
from app.services.version_comparator import VersionComparator
import logging

logger = logging.getLogger(__name__)

class UpdateDetector:
    """Service for detecting available module updates."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.comparator = VersionComparator()
    
    async def check_site_updates(self, site_id: int) -> Dict[str, Any]:
        """
        Check all modules for a site and identify available updates.
        
        Returns:
            Summary of available updates
        """
        # Get all site modules with their current versions
        query = select(SiteModule).where(
            and_(
                SiteModule.site_id == site_id,
                SiteModule.enabled == True
            )
        ).options(
            selectinload(SiteModule.module).selectinload(Module.versions),
            selectinload(SiteModule.current_version)
        )
        
        result = await self.db.execute(query)
        site_modules = result.scalars().all()
        
        updates_summary = {
            "total_modules": len(site_modules),
            "modules_with_updates": 0,
            "security_updates": 0,
            "update_details": []
        }
        
        for site_module in site_modules:
            update_info = await self._check_module_update(site_module)
            
            if update_info["has_update"]:
                updates_summary["modules_with_updates"] += 1
                updates_summary["update_details"].append(update_info)
                
                if update_info["has_security_update"]:
                    updates_summary["security_updates"] += 1
        
        return updates_summary
    
    async def _check_module_update(self, site_module: SiteModule) -> Dict[str, Any]:
        """Check for updates for a single module."""
        module = site_module.module
        current_version = site_module.current_version
        
        # Get all available versions for the module
        available_versions = [v.version_string for v in module.versions]
        
        # Check for any update
        has_update, latest_version = self.comparator.is_update_available(
            current_version.version_string,
            available_versions,
            include_unstable=False
        )
        
        # Check for security update
        has_security, security_version = self.comparator.is_security_update_available(
            current_version.version_string,
            available_versions
        )
        
        update_info = {
            "module_id": module.id,
            "module_name": module.machine_name,
            "current_version": current_version.version_string,
            "has_update": has_update,
            "latest_version": latest_version,
            "has_security_update": has_security,
            "security_version": security_version,
            "days_outdated": None
        }
        
        # Calculate how long outdated
        if has_update and latest_version:
            latest_version_obj = next(
                (v for v in module.versions if v.version_string == latest_version),
                None
            )
            if latest_version_obj and latest_version_obj.release_date:
                days_outdated = (datetime.utcnow() - latest_version_obj.release_date).days
                update_info["days_outdated"] = days_outdated
        
        # Update site_module flags
        if (site_module.update_available != has_update or
            site_module.security_update_available != has_security):
            
            site_module.update_available = has_update
            site_module.security_update_available = has_security
            
            if has_update and latest_version:
                latest_version_obj = next(
                    (v for v in module.versions if v.version_string == latest_version),
                    None
                )
                if latest_version_obj:
                    site_module.latest_version_id = latest_version_obj.id
            
            self.db.add(site_module)
        
        return update_info
    
    async def calculate_update_metrics(
        self,
        site_id: int,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate update metrics for a site over a time period.
        
        Returns:
            Metrics including average update lag, security response time, etc.
        """
        # This would analyze historical data to calculate:
        # - Average time to apply updates
        # - Average time to apply security updates
        # - Update compliance percentage
        # - etc.
        pass
```

### CRUD Updates

#### Update Module Version CRUD (`app/crud/crud_module_version.py`)
```python
# Add these methods to the existing CRUDModuleVersion class

async def get_versions_for_module(
    self,
    db: AsyncSession,
    *,
    module_id: int,
    stable_only: bool = False
) -> List[ModuleVersion]:
    """Get all versions for a module, optionally filtered."""
    query = select(ModuleVersion).where(
        ModuleVersion.module_id == module_id
    )
    
    if stable_only:
        # Filter out dev, alpha, beta versions
        # This would need the parsed version data
        pass
    
    query = query.order_by(ModuleVersion.release_date.desc())
    result = await db.execute(query)
    return result.scalars().all()

async def get_latest_stable_version(
    self,
    db: AsyncSession,
    *,
    module_id: int,
    drupal_core: Optional[str] = None
) -> Optional[ModuleVersion]:
    """Get the latest stable version for a module."""
    versions = await self.get_versions_for_module(
        db,
        module_id=module_id,
        stable_only=True
    )
    
    if not versions:
        return None
    
    # Use version comparator to find latest
    comparator = VersionComparator()
    version_strings = [v.version_string for v in versions]
    latest_string = comparator.get_latest_version(
        version_strings,
        stable_only=True,
        drupal_core=drupal_core
    )
    
    if latest_string:
        return next(v for v in versions if v.version_string == latest_string)
    
    return None
```

## Acceptance Criteria

### Version Parsing
- [ ] Correctly parse all Drupal version formats
- [ ] Handle edge cases and malformed versions gracefully
- [ ] Extract semantic version components
- [ ] Identify release types (stable, beta, etc.)
- [ ] Parse Drupal core compatibility

### Version Comparison
- [ ] Accurately compare versions following Drupal conventions
- [ ] 8.x-1.0 < 8.x-1.1 < 8.x-2.0
- [ ] 1.0.0-alpha1 < 1.0.0-beta1 < 1.0.0-rc1 < 1.0.0
- [ ] Handle dev versions correctly
- [ ] Respect Drupal core boundaries

### Update Detection
- [ ] Identify when updates are available
- [ ] Distinguish security updates
- [ ] Calculate update lag time
- [ ] Update database flags correctly
- [ ] Handle multiple branches

### Performance
- [ ] Version comparison < 1ms per operation
- [ ] Batch update checking < 100ms for 100 modules
- [ ] Efficient database queries
- [ ] Caching for repeated comparisons

## Test Requirements

### Unit Tests (`tests/test_services/test_version_parser.py`)

```python
import pytest
from app.services.version_parser import DrupalVersionParser, ReleaseType

class TestVersionParser:
    def setup_method(self):
        self.parser = DrupalVersionParser()
    
    @pytest.mark.parametrize("version,expected", [
        # Drupal contrib format
        ("8.x-1.0", {
            "drupal_core": "8.x",
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.STABLE
        }),
        ("7.x-2.5-beta1", {
            "drupal_core": "7.x",
            "major": 2,
            "minor": 5,
            "patch": 0,
            "release_type": ReleaseType.BETA,
            "release_number": 1
        }),
        # Semantic versioning
        ("1.0.0", {
            "major": 1,
            "minor": 0,
            "patch": 0,
            "release_type": ReleaseType.STABLE
        }),
        ("2.1.3-alpha2", {
            "major": 2,
            "minor": 1,
            "patch": 3,
            "release_type": ReleaseType.ALPHA,
            "release_number": 2
        }),
        # Dev versions
        ("8.x-1.x-dev", {
            "drupal_core": "8.x",
            "major": 1,
            "release_type": ReleaseType.DEV
        }),
        # Core format
        ("9.5.11", {
            "major": 9,
            "minor": 5,
            "patch": 11,
            "release_type": ReleaseType.STABLE
        })
    ])
    def test_parse_versions(self, version, expected):
        """Test parsing various version formats."""
        parsed = self.parser.parse(version)
        
        for key, value in expected.items():
            assert getattr(parsed, key) == value
    
    def test_parse_malformed_versions(self):
        """Test handling of malformed versions."""
        malformed = ["", "invalid", "123", "x.y.z"]
        
        for version in malformed:
            parsed = self.parser.parse(version)
            assert parsed.original == version
            # Should still produce some result
    
    def test_comparable_tuple_ordering(self):
        """Test that comparable tuples order correctly."""
        versions = [
            "1.0.0-alpha1",
            "1.0.0-beta1",
            "1.0.0-rc1",
            "1.0.0",
            "1.0.1"
        ]
        
        parsed = [self.parser.parse(v) for v in versions]
        tuples = [p.to_comparable_tuple() for p in parsed]
        
        # Verify ordering
        for i in range(len(tuples) - 1):
            assert tuples[i] < tuples[i + 1]
```

### Unit Tests (`tests/test_services/test_version_comparator.py`)

```python
import pytest
from app.services.version_comparator import VersionComparator

class TestVersionComparator:
    def setup_method(self):
        self.comparator = VersionComparator()
    
    @pytest.mark.parametrize("v1,v2,expected", [
        # Basic comparisons
        ("1.0.0", "1.0.1", -1),
        ("1.0.1", "1.0.0", 1),
        ("1.0.0", "1.0.0", 0),
        # Drupal contrib
        ("8.x-1.0", "8.x-1.1", -1),
        ("8.x-2.0", "8.x-1.99", 1),
        # Pre-release ordering
        ("1.0.0-alpha1", "1.0.0-beta1", -1),
        ("1.0.0-rc1", "1.0.0", -1),
        ("1.0.0", "1.0.0-rc1", 1),
        # Dev versions
        ("8.x-1.x-dev", "8.x-1.0", -1),
        # Different core versions
        ("8.x-1.0", "9.x-1.0", -1),
    ])
    def test_compare_versions(self, v1, v2, expected):
        """Test version comparison."""
        result = self.comparator.compare(v1, v2)
        assert result == expected
    
    def test_get_latest_version(self):
        """Test finding latest version from list."""
        versions = [
            "8.x-1.0",
            "8.x-1.5",
            "8.x-1.2",
            "8.x-2.0-beta1",
            "8.x-1.x-dev"
        ]
        
        # Latest overall
        latest = self.comparator.get_latest_version(versions)
        assert latest == "8.x-2.0-beta1"
        
        # Latest stable only
        latest_stable = self.comparator.get_latest_version(
            versions,
            stable_only=True
        )
        assert latest_stable == "8.x-1.5"
    
    def test_is_update_available(self):
        """Test update detection."""
        current = "8.x-1.0"
        available = [
            "8.x-1.0",
            "8.x-1.1",
            "8.x-1.2-beta1",
            "8.x-2.0-dev"
        ]
        
        # Check for stable updates
        has_update, latest = self.comparator.is_update_available(
            current,
            available,
            include_unstable=False
        )
        assert has_update is True
        assert latest == "8.x-1.1"
        
        # Check including unstable
        has_update, latest = self.comparator.is_update_available(
            current,
            available,
            include_unstable=True
        )
        assert has_update is True
        assert latest == "8.x-2.0-dev"
    
    def test_group_versions_by_branch(self):
        """Test grouping versions by branch."""
        versions = [
            "8.x-1.0",
            "8.x-1.1",
            "8.x-2.0",
            "9.x-1.0",
            "1.0.0",
            "1.1.0",
            "2.0.0"
        ]
        
        groups = self.comparator.group_versions_by_branch(versions)
        
        assert "8.x-1.x" in groups
        assert len(groups["8.x-1.x"]) == 2
        assert "8.x-2.x" in groups
        assert "9.x-1.x" in groups
        assert "1.0.x" in groups
        assert "1.1.x" in groups
```

### Integration Tests (`tests/test_services/test_update_detector.py`)

```python
class TestUpdateDetector:
    async def test_check_site_updates(self, db_session, test_site, test_modules):
        """Test checking updates for all site modules."""
        detector = UpdateDetector(db_session)
        
        # Setup test data with various update scenarios
        # Module 1: Has update available
        # Module 2: Has security update
        # Module 3: Up to date
        
        summary = await detector.check_site_updates(test_site.id)
        
        assert summary["total_modules"] == 3
        assert summary["modules_with_updates"] == 2
        assert summary["security_updates"] == 1
        assert len(summary["update_details"]) == 2
    
    async def test_update_flags_persisted(self, db_session):
        """Test that update flags are saved to database."""
        # Run update detection
        # Verify flags are set on SiteModule records
        # Run again and verify no unnecessary updates
        pass
```

### Performance Tests

```python
class TestVersionPerformance:
    def test_parse_performance(self):
        """Test version parsing performance."""
        parser = DrupalVersionParser()
        versions = ["8.x-1.0"] * 1000
        
        start = time.time()
        for v in versions:
            parser.parse(v)
        elapsed = time.time() - start
        
        # Should parse 1000 versions in < 100ms
        assert elapsed < 0.1
    
    def test_comparison_performance(self):
        """Test version comparison performance."""
        comparator = VersionComparator()
        
        start = time.time()
        for _ in range(1000):
            comparator.compare("8.x-1.0", "8.x-1.1")
        elapsed = time.time() - start
        
        # Should compare 1000 times in < 10ms
        assert elapsed < 0.01
```

## Implementation Steps

1. **Implement version parser**
   - Create regex patterns
   - Build ParsedVersion class
   - Handle edge cases

2. **Create version comparator**
   - Implement comparison logic
   - Add filtering methods
   - Build branch grouping

3. **Build update detector**
   - Site update checking
   - Module update checking
   - Metric calculation

4. **Update CRUD methods**
   - Add version query methods
   - Implement filtering
   - Add caching

5. **Write comprehensive tests**
   - Unit tests for parser
   - Unit tests for comparator
   - Integration tests
   - Performance tests

6. **Documentation**
   - Version format guide
   - Comparison rules
   - API documentation

## Dependencies
- Database models from Issue 1.1
- Basic module structure in place

## Definition of Done
- [ ] All version formats parsed correctly
- [ ] Comparison logic follows Drupal conventions
- [ ] Update detection accurate
- [ ] Database flags updated properly
- [ ] Performance requirements met
- [ ] All tests passing with 80%+ coverage
- [ ] Documentation complete
- [ ] Code reviewed and approved

## Notes
- Consider caching parsed versions for performance
- May need to handle version aliases (e.g., "latest")
- Future: Integration with Drupal.org API for version data
- Consider adding version constraint parsing (e.g., "^8.x-1.0")