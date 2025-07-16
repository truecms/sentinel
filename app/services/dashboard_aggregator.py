"""Dashboard data aggregation service."""

from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case, desc
from datetime import datetime, timedelta
import asyncio
import logging

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
    RiskItem,
    ModuleRiskItem,
    SecurityMetrics,
    SiteHealth,
    SiteModuleStats,
    Recommendation,
    HealthStatus,
    SeverityLevel
)

logger = logging.getLogger(__name__)


class DashboardAggregator:
    """Efficient dashboard data aggregation."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_overview_metrics(
        self,
        user: User,
        org_id: Optional[int] = None
    ) -> DashboardOverview:
        """Get executive dashboard overview metrics."""
        # Run queries in parallel
        tasks = [
            self._get_site_count(user, org_id),
            self._get_security_score(user, org_id),
            self._get_vulnerability_counts(user, org_id),
            self._get_compliance_rate(user, org_id),
            self._get_top_risks(user, org_id),
            self._get_recent_activity(user, org_id, limit=10),
            self._get_metric_trends(user, org_id)
        ]
        
        results = await asyncio.gather(*tasks)
        
        metrics = DashboardMetrics(
            total_sites=results[0],
            security_score=results[1]["score"],
            critical_updates=results[1]["critical_updates"],
            compliance_rate=results[3],
            vulnerabilities=results[2]
        )
        
        return DashboardOverview(
            metrics=metrics,
            trends=results[6],
            top_risks=results[4],
            recent_activity=results[5]
        )
    
    async def get_security_metrics(
        self,
        user: User,
        org_id: Optional[int] = None
    ) -> SecurityDashboard:
        """Get security operations dashboard metrics."""
        tasks = [
            self._get_security_stats(user, org_id),
            self._get_critical_modules(user, org_id),
            self._get_vulnerability_timeline(user, org_id),
            self._get_recent_patches(user, org_id),
            self._get_security_alerts(user, org_id)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return SecurityDashboard(
            metrics=results[0],
            critical_modules=results[1],
            vulnerability_timeline=results[2],
            recent_patches=results[3],
            alert_queue=results[4]
        )
    
    async def get_site_metrics(self, site_id: int) -> SiteDashboard:
        """Get site-specific dashboard metrics."""
        # Get site info
        site = await self.db.get(Site, site_id)
        if not site:
            raise ValueError(f"Site {site_id} not found")
        
        tasks = [
            self._get_site_health(site_id),
            self._get_site_module_stats(site_id),
            self._get_site_timeline(site_id),
            self._get_site_recommendations(site_id)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return SiteDashboard(
            site_id=site_id,
            site_name=site.name,
            health=results[0],
            modules=results[1],
            timeline=results[2],
            recommendations=results[3]
        )
    
    async def _get_site_count(self, user: User, org_id: Optional[int]) -> int:
        """Get total number of sites."""
        query = select(func.count(Site.id))
        if org_id:
            query = query.where(Site.organization_id == org_id)
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _get_security_score(
        self,
        user: User,
        org_id: Optional[int]
    ) -> Dict[str, Any]:
        """Calculate security score and critical updates."""
        # Get sites with outdated modules
        query = select(
            Site.id,
            func.count(SiteModule.id).label("outdated_modules"),
            func.sum(
                case(
                    (ModuleVersion.is_security_update == True, 1),
                    else_=0
                )
            ).label("security_updates")
        ).select_from(Site).join(
            SiteModule, Site.id == SiteModule.site_id
        ).join(
            Module, SiteModule.module_id == Module.id
        ).join(
            ModuleVersion,
            and_(
                Module.id == ModuleVersion.module_id,
                SiteModule.latest_version_id == ModuleVersion.id,
                SiteModule.latest_version_id != SiteModule.current_version_id
            )
        )
        
        if org_id:
            query = query.where(Site.organization_id == org_id)
        
        query = query.group_by(Site.id)
        
        result = await self.db.execute(query)
        site_stats = result.all()
        
        # Calculate score (simplified)
        total_sites = len(site_stats)
        if total_sites == 0:
            return {"score": 100.0, "critical_updates": 0}
        
        sites_with_security_updates = sum(
            1 for stat in site_stats if stat.security_updates > 0
        )
        critical_updates = sum(stat.security_updates or 0 for stat in site_stats)
        
        # Score calculation: 100 - (percentage of sites with security updates * 50)
        score = 100.0 - (sites_with_security_updates / total_sites * 50)
        
        return {
            "score": round(score, 1),
            "critical_updates": critical_updates
        }
    
    async def _get_vulnerability_counts(
        self,
        user: User,
        org_id: Optional[int]
    ) -> VulnerabilityCount:
        """Get vulnerability counts by severity."""
        # For now, return mock data
        # TODO: Implement actual vulnerability tracking
        return VulnerabilityCount(
            critical=0,
            high=0,
            medium=0,
            low=0
        )
    
    async def _get_compliance_rate(
        self,
        user: User,
        org_id: Optional[int]
    ) -> float:
        """Calculate compliance rate."""
        # Get sites with all modules up to date
        subquery = select(
            SiteModule.site_id,
            func.count(SiteModule.id).label("outdated_count")
        ).select_from(SiteModule).join(
            Module, SiteModule.module_id == Module.id
        ).where(
            and_(
                SiteModule.latest_version_id.is_not(None),
                SiteModule.latest_version_id != SiteModule.current_version_id
            )
        ).group_by(SiteModule.site_id).subquery()
        
        query = select(
            func.count(Site.id).label("total"),
            func.count(subquery.c.site_id).label("non_compliant")
        ).select_from(Site).outerjoin(
            subquery, Site.id == subquery.c.site_id
        )
        
        if org_id:
            query = query.where(Site.organization_id == org_id)
        
        result = await self.db.execute(query)
        stats = result.first()
        
        if not stats or stats.total == 0:
            return 100.0
        
        compliant = stats.total - (stats.non_compliant or 0)
        return round(compliant / stats.total * 100, 1)
    
    async def _get_top_risks(
        self,
        user: User,
        org_id: Optional[int],
        limit: int = 5
    ) -> List[RiskItem]:
        """Get top security risks."""
        # Get modules with the most outdated installations
        query = select(
            Module.display_name,
            Module.id,
            func.count(SiteModule.id).label("affected_sites"),
            func.bool_or(ModuleVersion.is_security_update).label("has_security")
        ).select_from(Module).join(
            SiteModule, Module.id == SiteModule.module_id
        ).join(
            ModuleVersion,
            and_(
                SiteModule.latest_version_id == ModuleVersion.id,
                SiteModule.latest_version_id != SiteModule.current_version_id
            )
        ).join(
            Site, SiteModule.site_id == Site.id
        )
        
        if org_id:
            query = query.where(Site.organization_id == org_id)
        
        query = query.group_by(Module.id, Module.display_name)
        query = query.having(func.bool_or(ModuleVersion.is_security_update) == True)
        query = query.order_by(desc("affected_sites"))
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        risks = []
        
        for row in result:
            risks.append(RiskItem(
                id=f"module-{row.id}",
                title=f"{row.name} needs security update",
                risk_score=min(row.affected_sites * 10, 100),
                affected_sites=row.affected_sites,
                severity=SeverityLevel.CRITICAL if row.has_security else SeverityLevel.HIGH,
                action_required=f"Update {row.name} on {row.affected_sites} sites"
            ))
        
        return risks
    
    async def _get_recent_activity(
        self,
        user: User,
        org_id: Optional[int],
        limit: int = 20
    ) -> List[ActivityItem]:
        """Get recent activity items."""
        # For now, return empty list
        # TODO: Implement activity tracking
        return []
    
    async def _get_metric_trends(
        self,
        user: User,
        org_id: Optional[int]
    ) -> Dict[str, List[TimeSeriesData]]:
        """Get trend data for various metrics."""
        # For now, return mock trends
        # TODO: Implement historical data tracking
        now = datetime.utcnow()
        
        trends = {
            "security_score": [],
            "vulnerabilities": [],
            "compliance": []
        }
        
        # Generate mock data points for the last 30 days
        for i in range(30):
            timestamp = now - timedelta(days=29-i)
            
            trends["security_score"].append(TimeSeriesData(
                timestamp=timestamp,
                value=85 + (i % 10) - 5  # Fluctuate between 80-90
            ))
            
            trends["compliance"].append(TimeSeriesData(
                timestamp=timestamp,
                value=90 + (i % 5) - 2  # Fluctuate between 88-93
            ))
        
        return trends
    
    async def _get_security_stats(
        self,
        user: User,
        org_id: Optional[int]
    ) -> SecurityMetrics:
        """Get security-specific statistics."""
        # TODO: Implement actual metrics
        return SecurityMetrics(
            active_threats=0,
            unpatched_vulnerabilities=0,
            average_time_to_patch=24.5,
            patches_applied_today=0,
            pending_security_updates=0,
            sla_compliance=95.5
        )
    
    async def _get_critical_modules(
        self,
        user: User,
        org_id: Optional[int],
        limit: int = 10
    ) -> List[ModuleRiskItem]:
        """Get critical modules needing updates."""
        # TODO: Implement actual critical module detection
        return []
    
    async def _get_vulnerability_timeline(
        self,
        user: User,
        org_id: Optional[int]
    ) -> List[TimeSeriesData]:
        """Get vulnerability trend over time."""
        # TODO: Implement actual vulnerability tracking
        return []
    
    async def _get_recent_patches(
        self,
        user: User,
        org_id: Optional[int],
        limit: int = 10
    ) -> List[ActivityItem]:
        """Get recently applied patches."""
        # TODO: Implement patch tracking
        return []
    
    async def _get_security_alerts(
        self,
        user: User,
        org_id: Optional[int],
        limit: int = 10
    ) -> List[ActivityItem]:
        """Get current security alerts."""
        # TODO: Implement security alert system
        return []
    
    async def _get_site_health(self, site_id: int) -> SiteHealth:
        """Calculate site health score."""
        # Count outdated modules
        query = select(
            func.count(SiteModule.id).label("total"),
            func.sum(
                case(
                    (SiteModule.latest_version_id != SiteModule.current_version_id, 1),
                    else_=0
                )
            ).label("outdated")
        ).select_from(SiteModule).where(
            SiteModule.site_id == site_id
        )
        
        result = await self.db.execute(query)
        stats = result.first()
        
        if not stats or stats.total == 0:
            score = 100.0
            status = HealthStatus.HEALTHY
        else:
            outdated_ratio = (stats.outdated or 0) / stats.total
            score = 100.0 * (1 - outdated_ratio)
            
            if score >= 90:
                status = HealthStatus.HEALTHY
            elif score >= 70:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.CRITICAL
        
        # Get last sync time
        site = await self.db.get(Site, site_id)
        
        return SiteHealth(
            score=round(score, 1),
            status=status,
            last_sync=site.updated_at or datetime.utcnow()
        )
    
    async def _get_site_module_stats(self, site_id: int) -> SiteModuleStats:
        """Get module statistics for a site."""
        # Get module counts
        query = select(
            func.count(SiteModule.id).label("total"),
            func.sum(
                case(
                    (SiteModule.latest_version_id != SiteModule.current_version_id, 1),
                    else_=0
                )
            ).label("needs_update"),
            func.sum(
                case(
                    (
                        and_(
                            SiteModule.latest_version_id != SiteModule.current_version_id,
                            SiteModule.security_update_available == True
                        ),
                        1
                    ),
                    else_=0
                )
            ).label("security_updates")
        ).select_from(SiteModule).where(
            SiteModule.site_id == site_id
        )
        
        result = await self.db.execute(query)
        stats = result.first()
        
        if not stats:
            return SiteModuleStats(
                total=0,
                up_to_date=0,
                needs_update=0,
                security_updates=0
            )
        
        return SiteModuleStats(
            total=stats.total or 0,
            up_to_date=(stats.total or 0) - (stats.needs_update or 0),
            needs_update=stats.needs_update or 0,
            security_updates=stats.security_updates or 0
        )
    
    async def _get_site_timeline(
        self,
        site_id: int,
        limit: int = 20
    ) -> List[ActivityItem]:
        """Get site activity timeline."""
        # TODO: Implement site activity tracking
        return []
    
    async def _get_site_recommendations(
        self,
        site_id: int
    ) -> List[Recommendation]:
        """Get recommendations for a site."""
        recommendations = []
        
        # Check for security updates
        query = select(
            Module.display_name,
            func.count(SiteModule.id).label("update_count")
        ).select_from(SiteModule).join(
            Module, SiteModule.module_id == Module.id
        ).where(
            and_(
                SiteModule.site_id == site_id,
                SiteModule.latest_version_id != SiteModule.current_version_id,
                SiteModule.security_update_available == True
            )
        ).group_by(Module.display_name)
        
        result = await self.db.execute(query)
        
        for row in result:
            recommendations.append(Recommendation(
                id=f"security-update-{row.name}",
                priority=SeverityLevel.CRITICAL,
                title=f"Security update available for {row.name}",
                description=f"{row.name} has {row.update_count} security updates available",
                action=f"Update {row.name} to the latest version"
            ))
        
        return recommendations
    
    async def get_recent_activities(
        self,
        user: User,
        org_id: Optional[int],
        limit: int
    ) -> List[ActivityItem]:
        """Get recent activities for the activity endpoint."""
        return await self._get_recent_activity(user, org_id, limit)
    
    async def get_metric_trends(
        self,
        metric: str,
        period: str,
        points: int,
        user: User,
        org_id: Optional[int]
    ) -> List[TimeSeriesData]:
        """Get trend data for a specific metric."""
        # TODO: Implement actual trend calculation based on period
        trends = await self._get_metric_trends(user, org_id)
        
        metric_map = {
            "security_score": "security_score",
            "vulnerabilities": "vulnerabilities",
            "compliance": "compliance",
            "sites": "sites"
        }
        
        if metric in metric_map and metric_map[metric] in trends:
            return trends[metric_map[metric]]
        
        return []