# Issue 1.5: Implement Security Update Detection

**Type**: Feature
**Priority**: P0 - Critical
**Epic**: Core Module Monitoring System
**Estimated Effort**: 3 days
**Labels**: `backend`, `security`, `monitoring`, `priority-critical`
**Dependencies**: Issue 1.1 (Database Models), Issue 1.3 (Data Ingestion), Issue 1.4 (Version Comparison)

## Description
Implement a comprehensive security update detection system that identifies security releases, tracks security advisories, calculates risk scores, and provides actionable security insights for Drupal modules across all monitored sites.

## Background
Security updates in Drupal are critical for maintaining site integrity. The system must:
- Detect security releases from version naming patterns
- Track security advisories and CVEs
- Calculate time-to-patch metrics
- Prioritize security updates by severity
- Generate security compliance reports
- Alert on zero-day vulnerabilities

## Technical Specification

### Security Models Enhancement

#### Security Advisory Model (`app/models/security_advisory.py`)
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base

class SeverityLevel(str, enum.Enum):
    """Security severity levels following CVSS standards."""
    CRITICAL = "critical"  # CVSS 9.0-10.0
    HIGH = "high"         # CVSS 7.0-8.9
    MEDIUM = "medium"     # CVSS 4.0-6.9
    LOW = "low"           # CVSS 0.1-3.9
    NONE = "none"         # CVSS 0.0

class SecurityAdvisory(Base):
    """Security advisories for modules."""
    __tablename__ = "security_advisories"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    advisory_id = Column(String(50), unique=True, nullable=False)  # SA-CONTRIB-2024-001
    title = Column(String(500), nullable=False)
    severity = Column(Enum(SeverityLevel), nullable=False, index=True)
    cvss_score = Column(Float, nullable=True)  # 0.0-10.0
    cve_ids = Column(JSON, default=list)  # ["CVE-2024-1234", "CVE-2024-5678"]
    
    description = Column(Text, nullable=False)
    vulnerability_details = Column(Text, nullable=True)
    solution = Column(Text, nullable=False)
    
    affected_versions = Column(JSON, nullable=False)  # ["<8.x-1.5", ">=9.x-1.0,<9.x-1.3"]
    fixed_versions = Column(JSON, nullable=False)  # ["8.x-1.5", "9.x-1.3"]
    
    published_date = Column(DateTime, nullable=False, index=True)
    last_updated = Column(DateTime, nullable=False)
    
    # Relationships
    module = relationship("Module", back_populates="security_advisories")
    version_updates = relationship("ModuleVersionSecurity", back_populates="advisory")

class ModuleVersionSecurity(Base):
    """Link between module versions and security advisories."""
    __tablename__ = "module_version_security"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("module_versions.id"), nullable=False, index=True)
    advisory_id = Column(Integer, ForeignKey("security_advisories.id"), nullable=False, index=True)
    
    is_vulnerable = Column(Boolean, default=True)
    is_fixed = Column(Boolean, default=False)
    
    # Relationships
    version = relationship("ModuleVersion", back_populates="security_info")
    advisory = relationship("SecurityAdvisory", back_populates="version_updates")
```

#### Update ModuleVersion Model
```python
# Add to ModuleVersion model
security_info = relationship("ModuleVersionSecurity", back_populates="version", cascade="all, delete-orphan")
```

#### Security Metrics Model (`app/models/security_metrics.py`)
```python
class SiteSecurityMetrics(Base):
    """Aggregated security metrics for sites."""
    __tablename__ = "site_security_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), unique=True, nullable=False)
    
    # Current state
    total_modules = Column(Integer, default=0)
    modules_with_security_updates = Column(Integer, default=0)
    critical_updates = Column(Integer, default=0)
    high_updates = Column(Integer, default=0)
    medium_updates = Column(Integer, default=0)
    low_updates = Column(Integer, default=0)
    
    # Risk scoring
    security_score = Column(Float, default=100.0)  # 0-100, higher is better
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    
    # Time metrics
    average_patch_time_hours = Column(Float, nullable=True)
    fastest_patch_time_hours = Column(Float, nullable=True)
    slowest_patch_time_hours = Column(Float, nullable=True)
    
    # Compliance
    compliance_percentage = Column(Float, default=100.0)
    last_security_update_applied = Column(DateTime, nullable=True)
    
    last_calculated = Column(DateTime, nullable=False, server_default=text('now()'))
    
    # Relationships
    site = relationship("Site", back_populates="security_metrics")
```

### Security Detection Service

#### Security Detector (`app/services/security_detector.py`)
```python
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
import logging

from app.models import (
    Module, ModuleVersion, SiteModule, Site,
    SecurityAdvisory, ModuleVersionSecurity, SiteSecurityMetrics
)
from app.services.version_comparator import VersionComparator
from app.schemas.security import SecuritySeverity

logger = logging.getLogger(__name__)

class SecurityDetector:
    """Service for detecting and analyzing security updates."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.version_comparator = VersionComparator()
        
    async def detect_security_version(
        self,
        module: Module,
        version_string: str,
        release_notes: Optional[str] = None
    ) -> Tuple[bool, Optional[SecuritySeverity]]:
        """
        Detect if a version is a security release.
        
        Returns:
            Tuple of (is_security_release, severity)
        """
        # Pattern matching for security releases
        security_patterns = [
            (r'security', SecuritySeverity.HIGH),
            (r'SECURITY', SecuritySeverity.HIGH),
            (r'SA-CONTRIB', SecuritySeverity.HIGH),
            (r'CVE-\d{4}-\d+', SecuritySeverity.CRITICAL),
            (r'critical.*security', SecuritySeverity.CRITICAL),
            (r'highly critical', SecuritySeverity.CRITICAL),
            (r'moderately critical', SecuritySeverity.MEDIUM),
            (r'less critical', SecuritySeverity.LOW),
        ]
        
        # Check version string
        version_lower = version_string.lower()
        if 'security' in version_lower:
            return True, SecuritySeverity.HIGH
        
        # Check release notes if available
        if release_notes:
            notes_lower = release_notes.lower()
            for pattern, severity in security_patterns:
                if re.search(pattern, release_notes, re.IGNORECASE):
                    return True, severity
        
        # Check for security advisories
        advisory = await self._check_advisory_database(module.id, version_string)
        if advisory:
            return True, advisory.severity
        
        return False, None
    
    async def analyze_site_security(self, site_id: int) -> Dict[str, Any]:
        """
        Comprehensive security analysis for a site.
        
        Returns detailed security status and recommendations.
        """
        # Get all site modules with security updates available
        query = select(SiteModule).where(
            and_(
                SiteModule.site_id == site_id,
                SiteModule.enabled == True,
                SiteModule.security_update_available == True
            )
        ).options(
            selectinload(SiteModule.module),
            selectinload(SiteModule.current_version),
            selectinload(SiteModule.latest_version)
        )
        
        result = await self.db.execute(query)
        vulnerable_modules = result.scalars().all()
        
        # Categorize by severity
        security_summary = {
            "total_vulnerabilities": len(vulnerable_modules),
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "unknown": [],
            "risk_score": 0.0,
            "recommendations": []
        }
        
        for site_module in vulnerable_modules:
            severity = await self._get_module_security_severity(
                site_module.module,
                site_module.current_version,
                site_module.latest_version
            )
            
            module_info = {
                "module_name": site_module.module.machine_name,
                "current_version": site_module.current_version.version_string,
                "secure_version": site_module.latest_version.version_string,
                "days_vulnerable": await self._calculate_vulnerability_days(site_module),
                "severity": severity,
                "advisory": await self._get_latest_advisory(site_module.module.id)
            }
            
            # Categorize by severity
            if severity == SecuritySeverity.CRITICAL:
                security_summary["critical"].append(module_info)
            elif severity == SecuritySeverity.HIGH:
                security_summary["high"].append(module_info)
            elif severity == SecuritySeverity.MEDIUM:
                security_summary["medium"].append(module_info)
            elif severity == SecuritySeverity.LOW:
                security_summary["low"].append(module_info)
            else:
                security_summary["unknown"].append(module_info)
        
        # Calculate risk score
        security_summary["risk_score"] = self._calculate_risk_score(security_summary)
        
        # Generate recommendations
        security_summary["recommendations"] = self._generate_recommendations(security_summary)
        
        # Update metrics
        await self._update_security_metrics(site_id, security_summary)
        
        return security_summary
    
    async def check_zero_day_vulnerabilities(self) -> List[Dict[str, Any]]:
        """
        Check for zero-day vulnerabilities (advisories without fixes).
        
        Returns list of modules with zero-day vulnerabilities.
        """
        query = select(SecurityAdvisory).where(
            SecurityAdvisory.fixed_versions == []
        ).options(
            selectinload(SecurityAdvisory.module)
        )
        
        result = await self.db.execute(query)
        zero_days = result.scalars().all()
        
        vulnerabilities = []
        for advisory in zero_days:
            # Find affected sites
            affected_sites = await self._get_sites_using_module(advisory.module_id)
            
            vulnerabilities.append({
                "module": advisory.module.machine_name,
                "advisory_id": advisory.advisory_id,
                "severity": advisory.severity,
                "published": advisory.published_date,
                "description": advisory.description,
                "affected_sites": len(affected_sites),
                "sites": affected_sites
            })
        
        return vulnerabilities
    
    async def calculate_security_compliance(
        self,
        site_id: int,
        sla_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Calculate security compliance based on SLA.
        
        Args:
            site_id: Site to analyze
            sla_hours: Hours allowed to apply security updates
            
        Returns:
            Compliance metrics and detailed breakdown
        """
        # Get patch history
        patch_times = await self._get_security_patch_times(site_id)
        
        total_patches = len(patch_times)
        compliant_patches = sum(
            1 for time in patch_times 
            if time <= timedelta(hours=sla_hours)
        )
        
        compliance_rate = (
            (compliant_patches / total_patches * 100) 
            if total_patches > 0 
            else 100.0
        )
        
        return {
            "compliance_percentage": compliance_rate,
            "total_security_updates": total_patches,
            "compliant_updates": compliant_patches,
            "sla_breaches": total_patches - compliant_patches,
            "average_patch_time": (
                sum(patch_times, timedelta()) / total_patches 
                if total_patches > 0 
                else timedelta()
            ),
            "sla_hours": sla_hours,
            "details": await self._get_compliance_details(site_id, sla_hours)
        }
    
    def _calculate_risk_score(self, security_summary: Dict[str, Any]) -> float:
        """
        Calculate overall risk score (0-100, lower is riskier).
        
        Factors:
        - Number of vulnerabilities by severity
        - Time since vulnerability published
        - Module criticality
        """
        base_score = 100.0
        
        # Deduct points based on vulnerabilities
        deductions = {
            "critical": 25.0,
            "high": 15.0,
            "medium": 8.0,
            "low": 3.0
        }
        
        for severity, modules in security_summary.items():
            if severity in deductions and isinstance(modules, list):
                for module in modules:
                    # Base deduction
                    score_deduction = deductions[severity]
                    
                    # Additional deduction for age
                    days_vulnerable = module.get("days_vulnerable", 0)
                    if days_vulnerable > 30:
                        score_deduction *= 1.5
                    elif days_vulnerable > 7:
                        score_deduction *= 1.2
                    
                    base_score -= score_deduction
        
        # Ensure score stays in valid range
        return max(0.0, min(100.0, base_score))
    
    def _generate_recommendations(self, security_summary: Dict[str, Any]) -> List[str]:
        """Generate actionable security recommendations."""
        recommendations = []
        
        # Critical updates
        if security_summary["critical"]:
            recommendations.append({
                "priority": "URGENT",
                "action": "Apply critical security updates immediately",
                "modules": [m["module_name"] for m in security_summary["critical"]],
                "reason": "Critical vulnerabilities pose immediate risk"
            })
        
        # High priority updates
        if security_summary["high"]:
            recommendations.append({
                "priority": "HIGH",
                "action": "Schedule high-priority updates within 24 hours",
                "modules": [m["module_name"] for m in security_summary["high"]],
                "reason": "High severity vulnerabilities require prompt attention"
            })
        
        # Old vulnerabilities
        old_vulns = []
        for severity in ["critical", "high", "medium", "low"]:
            if severity in security_summary:
                old_vulns.extend([
                    m for m in security_summary[severity]
                    if m.get("days_vulnerable", 0) > 30
                ])
        
        if old_vulns:
            recommendations.append({
                "priority": "HIGH",
                "action": "Address long-standing vulnerabilities",
                "modules": [m["module_name"] for m in old_vulns],
                "reason": "Vulnerabilities over 30 days old increase exposure risk"
            })
        
        # Risk score based recommendations
        risk_score = security_summary["risk_score"]
        if risk_score < 50:
            recommendations.append({
                "priority": "CRITICAL",
                "action": "Implement emergency security response plan",
                "reason": f"Risk score {risk_score:.1f} indicates critical security posture"
            })
        elif risk_score < 70:
            recommendations.append({
                "priority": "HIGH",
                "action": "Prioritize security updates in next maintenance window",
                "reason": f"Risk score {risk_score:.1f} requires immediate improvement"
            })
        
        return recommendations
    
    async def _update_security_metrics(
        self,
        site_id: int,
        security_summary: Dict[str, Any]
    ) -> None:
        """Update site security metrics in database."""
        # Get or create metrics record
        query = select(SiteSecurityMetrics).where(
            SiteSecurityMetrics.site_id == site_id
        )
        result = await self.db.execute(query)
        metrics = result.scalar_one_or_none()
        
        if not metrics:
            metrics = SiteSecurityMetrics(site_id=site_id)
        
        # Update metrics
        metrics.modules_with_security_updates = security_summary["total_vulnerabilities"]
        metrics.critical_updates = len(security_summary["critical"])
        metrics.high_updates = len(security_summary["high"])
        metrics.medium_updates = len(security_summary["medium"])
        metrics.low_updates = len(security_summary["low"])
        metrics.security_score = security_summary["risk_score"]
        
        # Determine risk level
        if metrics.security_score < 50:
            metrics.risk_level = "critical"
        elif metrics.security_score < 70:
            metrics.risk_level = "high"
        elif metrics.security_score < 85:
            metrics.risk_level = "medium"
        else:
            metrics.risk_level = "low"
        
        metrics.last_calculated = datetime.utcnow()
        
        self.db.add(metrics)
        await self.db.commit()
```

### Security API Endpoints

#### Security Endpoints (`app/api/v1/endpoints/security.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.security import (
    SecuritySummaryResponse,
    SecurityAdvisoryResponse,
    ComplianceReportResponse,
    ZeroDayAlert
)
from app.services.security_detector import SecurityDetector

router = APIRouter()

@router.get("/sites/{site_id}/security", response_model=SecuritySummaryResponse)
async def get_site_security_status(
    site_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get comprehensive security status for a site.
    
    Returns:
    - Vulnerabilities by severity
    - Risk score and recommendations
    - Patch time metrics
    """
    # Check user has access to site
    if not await deps.user_has_site_access(db, current_user, site_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    detector = SecurityDetector(db)
    security_summary = await detector.analyze_site_security(site_id)
    
    return SecuritySummaryResponse(**security_summary)

@router.get("/sites/{site_id}/security/compliance", response_model=ComplianceReportResponse)
async def get_security_compliance(
    site_id: int,
    sla_hours: int = Query(24, description="SLA hours for security patches"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get security compliance report for a site.
    
    Calculates compliance based on SLA for applying security patches.
    """
    if not await deps.user_has_site_access(db, current_user, site_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    detector = SecurityDetector(db)
    compliance = await detector.calculate_security_compliance(site_id, sla_hours)
    
    return ComplianceReportResponse(**compliance)

@router.get("/security/advisories", response_model=List[SecurityAdvisoryResponse])
async def get_security_advisories(
    severity: Optional[str] = Query(None, regex="^(critical|high|medium|low)$"),
    module_id: Optional[int] = None,
    days: int = Query(30, description="Advisories from last N days"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get recent security advisories.
    
    - **severity**: Filter by severity level
    - **module_id**: Filter by specific module
    - **days**: Advisories from last N days
    """
    query = select(SecurityAdvisory).where(
        SecurityAdvisory.published_date >= datetime.utcnow() - timedelta(days=days)
    )
    
    if severity:
        query = query.where(SecurityAdvisory.severity == severity)
    
    if module_id:
        query = query.where(SecurityAdvisory.module_id == module_id)
    
    query = query.order_by(SecurityAdvisory.published_date.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    advisories = result.scalars().all()
    
    return [SecurityAdvisoryResponse.from_orm(a) for a in advisories]

@router.get("/security/zero-days", response_model=List[ZeroDayAlert])
async def get_zero_day_vulnerabilities(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Get zero-day vulnerabilities (superuser only).
    
    Returns modules with security advisories but no available fixes.
    """
    detector = SecurityDetector(db)
    zero_days = await detector.check_zero_day_vulnerabilities()
    
    return [ZeroDayAlert(**zd) for zd in zero_days]

@router.post("/security/scan")
async def trigger_security_scan(
    site_id: Optional[int] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
    background_tasks: BackgroundTasks = Depends()
) -> Any:
    """
    Trigger a security scan (superuser only).
    
    Scans for new security updates and updates all metrics.
    """
    background_tasks.add_task(
        run_security_scan,
        db,
        site_id
    )
    
    return {
        "message": "Security scan initiated",
        "site_id": site_id,
        "status": "processing"
    }
```

### Security Schemas

#### Security Response Models (`app/schemas/security.py`)
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

class SecuritySeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class VulnerableModule(BaseModel):
    module_name: str
    current_version: str
    secure_version: str
    severity: SecuritySeverity
    days_vulnerable: int
    advisory_id: Optional[str] = None
    cve_ids: List[str] = []

class SecurityRecommendation(BaseModel):
    priority: str
    action: str
    modules: Optional[List[str]] = None
    reason: str

class SecuritySummaryResponse(BaseModel):
    total_vulnerabilities: int
    critical: List[VulnerableModule]
    high: List[VulnerableModule]
    medium: List[VulnerableModule]
    low: List[VulnerableModule]
    unknown: List[VulnerableModule]
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: str
    recommendations: List[SecurityRecommendation]
    last_scan: datetime

class ComplianceReportResponse(BaseModel):
    compliance_percentage: float = Field(..., ge=0, le=100)
    total_security_updates: int
    compliant_updates: int
    sla_breaches: int
    average_patch_time_hours: float
    sla_hours: int
    details: List[Dict[str, Any]]

class SecurityAdvisoryResponse(BaseModel):
    id: int
    advisory_id: str
    module_name: str
    title: str
    severity: SecuritySeverity
    cvss_score: Optional[float] = None
    cve_ids: List[str] = []
    description: str
    solution: str
    affected_versions: List[str]
    fixed_versions: List[str]
    published_date: datetime
    
    class Config:
        from_attributes = True

class ZeroDayAlert(BaseModel):
    module: str
    advisory_id: str
    severity: SecuritySeverity
    published: datetime
    description: str
    affected_sites: int
    sites: List[Dict[str, Any]]
```

## Acceptance Criteria

### Security Detection
- [ ] Accurately identify security releases from version strings
- [ ] Parse security advisories and link to versions
- [ ] Calculate CVSS scores and severity levels
- [ ] Detect zero-day vulnerabilities
- [ ] Track CVE identifiers

### Risk Assessment
- [ ] Calculate risk scores based on multiple factors
- [ ] Categorize vulnerabilities by severity
- [ ] Track vulnerability age and exposure time
- [ ] Generate actionable recommendations
- [ ] Prioritize updates by risk

### Compliance Tracking
- [ ] Calculate SLA compliance for security patches
- [ ] Track patch application times
- [ ] Generate compliance reports
- [ ] Historical compliance trends
- [ ] Identify repeat SLA violations

### Performance
- [ ] Security analysis < 500ms per site
- [ ] Bulk security scan < 30s for 100 sites
- [ ] Efficient advisory matching
- [ ] Cached security metrics

### Integration
- [ ] Update site modules with security flags
- [ ] Store security metrics
- [ ] API endpoints for security data
- [ ] Background security scanning
- [ ] Real-time security alerts

## Test Requirements

### Unit Tests (`tests/test_services/test_security_detector.py`)

```python
import pytest
from datetime import datetime, timedelta
from app.services.security_detector import SecurityDetector, SecuritySeverity

class TestSecurityDetector:
    async def test_detect_security_version(self, db_session):
        """Test detection of security versions."""
        detector = SecurityDetector(db_session)
        
        # Test cases
        test_cases = [
            ("8.x-1.5-security1", True, SecuritySeverity.HIGH),
            ("2.0.0-SECURITY", True, SecuritySeverity.HIGH),
            ("1.2.3", False, None),
            ("3.0.0-beta1", False, None),
        ]
        
        for version, expected_security, expected_severity in test_cases:
            is_security, severity = await detector.detect_security_version(
                mock_module,
                version
            )
            assert is_security == expected_security
            assert severity == expected_severity
    
    async def test_analyze_site_security(self, db_session, test_site_with_vulnerabilities):
        """Test comprehensive security analysis."""
        detector = SecurityDetector(db_session)
        
        analysis = await detector.analyze_site_security(test_site_with_vulnerabilities.id)
        
        assert analysis["total_vulnerabilities"] > 0
        assert "critical" in analysis
        assert "recommendations" in analysis
        assert 0 <= analysis["risk_score"] <= 100
    
    async def test_risk_score_calculation(self):
        """Test risk score calculation logic."""
        detector = SecurityDetector(None)
        
        # High risk scenario
        high_risk_summary = {
            "critical": [{"module_name": "m1", "days_vulnerable": 60}],
            "high": [{"module_name": "m2", "days_vulnerable": 30}],
            "medium": [],
            "low": []
        }
        
        score = detector._calculate_risk_score(high_risk_summary)
        assert score < 50  # High risk = low score
        
        # Low risk scenario
        low_risk_summary = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [{"module_name": "m3", "days_vulnerable": 1}]
        }
        
        score = detector._calculate_risk_score(low_risk_summary)
        assert score > 90  # Low risk = high score
    
    async def test_zero_day_detection(self, db_session, zero_day_advisory):
        """Test detection of zero-day vulnerabilities."""
        detector = SecurityDetector(db_session)
        
        zero_days = await detector.check_zero_day_vulnerabilities()
        
        assert len(zero_days) > 0
        assert any(zd["advisory_id"] == zero_day_advisory.advisory_id for zd in zero_days)
    
    async def test_compliance_calculation(self, db_session, test_site_with_patch_history):
        """Test security compliance calculation."""
        detector = SecurityDetector(db_session)
        
        compliance = await detector.calculate_security_compliance(
            test_site_with_patch_history.id,
            sla_hours=24
        )
        
        assert "compliance_percentage" in compliance
        assert "sla_breaches" in compliance
        assert compliance["compliance_percentage"] >= 0
        assert compliance["compliance_percentage"] <= 100
```

### Integration Tests (`tests/test_api/test_security.py`)

```python
class TestSecurityAPI:
    async def test_get_site_security_status(self, client, auth_headers, test_site):
        """Test security status endpoint."""
        response = await client.get(
            f"/api/v1/security/sites/{test_site.id}/security",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "recommendations" in data
        assert all(severity in data for severity in ["critical", "high", "medium", "low"])
    
    async def test_security_compliance_report(self, client, auth_headers, test_site):
        """Test compliance report generation."""
        response = await client.get(
            f"/api/v1/security/sites/{test_site.id}/security/compliance",
            params={"sla_hours": 48},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "compliance_percentage" in data
        assert data["sla_hours"] == 48
    
    async def test_security_advisories_list(self, client, auth_headers):
        """Test listing security advisories."""
        response = await client.get(
            "/api/v1/security/advisories",
            params={"severity": "critical", "days": 7},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        advisories = response.json()
        assert isinstance(advisories, list)
        assert all(a["severity"] == "critical" for a in advisories)
    
    async def test_zero_day_alerts_superuser_only(self, client, auth_headers, superuser_headers):
        """Test zero-day endpoint requires superuser."""
        # Regular user - should fail
        response = await client.get(
            "/api/v1/security/zero-days",
            headers=auth_headers
        )
        assert response.status_code == 403
        
        # Superuser - should succeed
        response = await client.get(
            "/api/v1/security/zero-days",
            headers=superuser_headers
        )
        assert response.status_code == 200
```

### Performance Tests

```python
class TestSecurityPerformance:
    async def test_security_analysis_performance(self, db_session, large_site):
        """Test performance of security analysis."""
        detector = SecurityDetector(db_session)
        
        start = time.time()
        await detector.analyze_site_security(large_site.id)
        elapsed = time.time() - start
        
        assert elapsed < 0.5  # Should complete in under 500ms
    
    async def test_bulk_security_scan_performance(self, db_session, many_sites):
        """Test bulk security scanning performance."""
        detector = SecurityDetector(db_session)
        
        start = time.time()
        for site in many_sites[:100]:
            await detector.analyze_site_security(site.id)
        elapsed = time.time() - start
        
        assert elapsed < 30  # 100 sites in under 30 seconds
```

## Implementation Steps

1. **Create security models**
   - SecurityAdvisory model
   - ModuleVersionSecurity link table
   - SiteSecurityMetrics model
   - Database migrations

2. **Implement security detector**
   - Version security detection
   - Advisory management
   - Risk calculation
   - Compliance tracking

3. **Build security API**
   - Security status endpoint
   - Compliance reports
   - Advisory listing
   - Zero-day alerts

4. **Add background tasks**
   - Periodic security scans
   - Advisory updates
   - Metric calculations

5. **Create security alerts**
   - Email notifications
   - Dashboard warnings
   - Slack/webhook integration

6. **Write comprehensive tests**
   - Unit tests for detection
   - API integration tests
   - Performance benchmarks

7. **Documentation**
   - Security best practices
   - API documentation
   - Response procedures

## Dependencies
- Version comparison from Issue 1.4
- Module tracking from Issues 1.1-1.3
- Background task infrastructure

## Definition of Done
- [ ] Security detection accurate for all version formats
- [ ] Risk scores calculated correctly
- [ ] Compliance tracking functional
- [ ] All security endpoints working
- [ ] Background scanning implemented
- [ ] Performance requirements met
- [ ] All tests passing with 80%+ coverage
- [ ] Security documentation complete
- [ ] Deployed to staging environment

## Notes
- Consider integration with CVE databases
- Future: Machine learning for risk prediction
- Add support for custom security policies
- Consider security dashboard visualizations
- Plan for security alert fatigue management