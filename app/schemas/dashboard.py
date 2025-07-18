"""Dashboard data schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SeverityLevel(str, Enum):
    """Vulnerability severity levels."""

    _ = "critical"
    _ = "high"
    _ = "medium"
    _ = "low"


class HealthStatus(str, Enum):
    """Site health status."""

    _ = "healthy"
    _ = "warning"
    _ = "critical"


class VulnerabilityCount(BaseModel):
    """Vulnerability count by severity."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class TimeSeriesData(BaseModel):
    """Time series data point."""

    timestamp: datetime
    value: float
    label: Optional[str] = None


class ActivityItem(BaseModel):
    """Activity feed item."""

    id: str
    type: str  # "module_update", "site_sync", "security_alert", etc.
    title: str
    description: Optional[str] = None
    timestamp: datetime
    severity: Optional[SeverityLevel] = None
    metadata: Dict[str, Any] = {}


class RiskItem(BaseModel):
    """Risk assessment item."""

    id: str
    title: str
    risk_score: float  # 0-100
    affected_sites: int
    severity: SeverityLevel
    action_required: str


class ModuleRiskItem(BaseModel):
    """Module risk assessment."""

    module_name: str
    module_version: str
    risk_score: float
    affected_sites: int
    days_since_update: int
    has_security_update: bool


class DashboardMetrics(BaseModel):
    """Core dashboard metrics."""

    total_sites: int
    security_score: float  # 0-100
    critical_updates: int
    compliance_rate: float  # percentage
    vulnerabilities: VulnerabilityCount


class DashboardOverview(BaseModel):
    """Executive dashboard overview."""

    metrics: DashboardMetrics
    trends: Dict[str, List[TimeSeriesData]]
    top_risks: List[RiskItem]
    recent_activity: List[ActivityItem]


class SecurityMetrics(BaseModel):
    """Security-specific metrics."""

    active_threats: int
    unpatched_vulnerabilities: int
    average_time_to_patch: float  # hours
    patches_applied_today: int
    pending_security_updates: int
    sla_compliance: float  # percentage


class SecurityDashboard(BaseModel):
    """Security operations dashboard."""

    metrics: SecurityMetrics
    critical_modules: List[ModuleRiskItem]
    vulnerability_timeline: List[TimeSeriesData]
    recent_patches: List[ActivityItem]
    alert_queue: List[ActivityItem]


class SiteHealth(BaseModel):
    """Site health information."""

    score: float  # 0-100
    status: HealthStatus
    last_sync: datetime


class SiteModuleStats(BaseModel):
    """Site module statistics."""

    total: int
    up_to_date: int
    needs_update: int
    security_updates: int


class Recommendation(BaseModel):
    """Site recommendation."""

    id: str
    priority: SeverityLevel
    title: str
    description: str
    action: str


class SiteDashboard(BaseModel):
    """Site-specific dashboard."""

    site_id: int
    site_name: str
    health: SiteHealth
    modules: SiteModuleStats
    timeline: List[ActivityItem]
    recommendations: List[Recommendation]


class WebSocketNotification(BaseModel):
    """Real-time notification via WebSocket."""

    id: str
    type: str
    title: str
    message: str
    severity: Optional[SeverityLevel] = None
    timestamp: datetime = datetime.utcnow()
    data: Optional[Dict[str, Any]] = None
