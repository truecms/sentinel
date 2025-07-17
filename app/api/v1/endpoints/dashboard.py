"""Dashboard API endpoints for real-time data."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Any, Optional, List, Dict
from datetime import datetime, timedelta
import json

from app.api import deps
from app.models.user import User
from app.models.site import Site
from app.models.site_module import SiteModule
from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.organization import Organization
from app.schemas.dashboard import (
    DashboardOverview,
    SecurityDashboard,
    SiteDashboard,
    DashboardMetrics,
    VulnerabilityCount,
    TimeSeriesData,
    ActivityItem,
    ModuleRiskItem
)
from app.core.redis import get_redis
from app.services.dashboard_aggregator import DashboardAggregator

router = APIRouter()


@router.get("/dashboard/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    redis = Depends(get_redis)
) -> Any:
    """Get executive dashboard overview data."""
    # Check permissions
    if org_id and not current_user.is_superuser:
        # Verify user has access to this organization
        # TODO: Implement proper organization membership check
        pass
    
    # Try cache first
    cache_key = f"dashboard:overview:{org_id or 'all'}:{current_user.id}"
    if redis:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    
    # Aggregate metrics
    aggregator = DashboardAggregator(db)
    metrics = await aggregator.get_overview_metrics(current_user, org_id)
    
    # Cache for 1 minute
    if redis:
        await redis.setex(cache_key, 60, metrics.model_dump_json())
    
    return metrics


@router.get("/dashboard/security", response_model=SecurityDashboard)
async def get_security_dashboard(
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    redis = Depends(get_redis)
) -> Any:
    """Get security operations dashboard data."""
    # Try cache first
    cache_key = f"dashboard:security:{org_id or 'all'}:{current_user.id}"
    if redis:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    
    # Aggregate security metrics
    aggregator = DashboardAggregator(db)
    security_data = await aggregator.get_security_metrics(current_user, org_id)
    
    # Cache for 30 seconds (more frequent updates for security data)
    if redis:
        await redis.setex(cache_key, 30, json.dumps(security_data.dict()))
    
    return security_data


@router.get("/dashboard/site/{site_id}", response_model=SiteDashboard)
async def get_site_dashboard(
    site_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    redis = Depends(get_redis)
) -> Any:
    """Get site-specific dashboard data."""
    # Verify access to site
    site = await db.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Check permissions
    if not current_user.is_superuser:
        # TODO: Implement proper site access check
        pass
    
    # Try cache first
    cache_key = f"dashboard:site:{site_id}:{current_user.id}"
    if redis:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    
    # Aggregate site metrics
    aggregator = DashboardAggregator(db)
    site_data = await aggregator.get_site_metrics(site_id)
    
    # Cache for 1 minute
    if redis:
        await redis.setex(cache_key, 60, json.dumps(site_data.dict()))
    
    return site_data


@router.get("/dashboard/activity")
async def get_recent_activity(
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> List[ActivityItem]:
    """Get recent activity feed."""
    aggregator = DashboardAggregator(db)
    activities = await aggregator.get_recent_activities(current_user, org_id, limit)
    return activities


@router.get("/dashboard/trends/{metric}")
async def get_metric_trends(
    metric: str,
    period: str = Query("day", regex="^(hour|day|week|month)$"),
    points: int = Query(30, ge=1, le=365),
    org_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> List[TimeSeriesData]:
    """Get trend data for a specific metric."""
    valid_metrics = ["security_score", "vulnerabilities", "compliance", "sites"]
    if metric not in valid_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Must be one of: {', '.join(valid_metrics)}"
        )
    
    aggregator = DashboardAggregator(db)
    trends = await aggregator.get_metric_trends(
        metric, period, points, current_user, org_id
    )
    return trends


@router.get("/risk-matrix", response_model=Dict[str, Any])
async def get_risk_matrix(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of sites to return")
) -> Any:
    """Get risk matrix data for sites.
    
    Returns risk scores for each site across different categories:
    - Security: Based on security updates and vulnerabilities
    - Performance: Based on site performance metrics
    - Updates: Based on pending updates
    """
    
    aggregator = DashboardAggregator(db)
    risk_data = await aggregator.get_risk_matrix(
        current_user, org_id, limit
    )
    return risk_data