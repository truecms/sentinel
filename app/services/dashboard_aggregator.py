"""Dashboard data aggregation service."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, case, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.site import Site
from app.models.site_module import SiteModule
from app.models.user import User
from app.schemas.dashboard import (
    ActivityItem,
    DashboardMetrics,
    DashboardOverview,
    HealthStatus,
    ModuleRiskItem,
    Recommendation,
    RiskItem,
    SecurityDashboard,
    SecurityMetrics,
    SeverityLevel,
    SiteDashboard,
    SiteHealth,
    SiteModuleStats,
    TimeSeriesData,
    VulnerabilityCount,
)

logger = logging.getLogger(__name__)


class DashboardAggregator:
    """Efficient dashboard data aggregation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview_metrics(
        self, user: User, org_id: Optional[int] = None
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
            self._get_metric_trends(user, org_id),
        ]

        results = await asyncio.gather(*tasks)

        metrics = DashboardMetrics(
            total_sites=results[0],
            security_score=results[1]["score"],
            critical_updates=results[1]["critical_updates"],
            compliance_rate=results[3],
            vulnerabilities=results[2],
        )

        return DashboardOverview(
            metrics=metrics,
            trends=results[6],
            top_risks=results[4],
            recent_activity=results[5],
        )

    async def get_security_metrics(
        self, user: User, org_id: Optional[int] = None
    ) -> SecurityDashboard:
        """Get security operations dashboard metrics."""
        tasks = [
            self._get_security_stats(user, org_id),
            self._get_critical_modules(user, org_id),
            self._get_vulnerability_timeline(user, org_id),
            self._get_recent_patches(user, org_id),
            self._get_security_alerts(user, org_id),
        ]

        results = await asyncio.gather(*tasks)

        return SecurityDashboard(
            metrics=results[0],
            critical_modules=results[1],
            vulnerability_timeline=results[2],
            recent_patches=results[3],
            alerts=results[4],
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
            self._get_site_recommendations(site_id),
        ]

        results = await asyncio.gather(*tasks)

        return SiteDashboard(
            site_id=site_id,
            name=site.name,
            health=results[0],
            modules=results[1],
            timeline=results[2],
            recommendations=results[3],
        )

    async def _get_site_count(self, user: User, org_id: Optional[int]) -> int:
        """Get total number of sites."""
        query = select(func.count(Site.id))
        if org_id:
            query = query.where(Site.organization_id == org_id)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def _get_security_score(
        self, user: User, org_id: Optional[int]
    ) -> Dict[str, Any]:
        """Calculate security score and critical updates."""
        # Get sites with outdated modules
        query = (
            select(
                Site.id,
                func.count(SiteModule.id).label("outdated_modules"),
                func.sum(case((ModuleVersion.is_security_update, 1), else_=0)).label(
                    "security_updates"
                ),
            )
            .select_from(Site)
            .join(SiteModule, Site.id == SiteModule.site_id)
            .join(Module, SiteModule.module_id == Module.id)
            .join(
                ModuleVersion,
                and_(
                    Module.id == ModuleVersion.module_id,
                    SiteModule.latest_version_id == ModuleVersion.id,
                    SiteModule.latest_version_id != SiteModule.current_version_id,
                ),
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

        return {"score": round(score, 1), "critical_updates": critical_updates}

    async def _get_vulnerability_counts(
        self, user: User, org_id: Optional[int]
    ) -> VulnerabilityCount:
        """Get vulnerability counts by severity."""
        # Count security updates needed by severity
        # Critical: Multiple security updates needed on same module/site
        # High: Single security update needed
        # Medium: Regular updates that affect security
        # Low: Minor security-related updates

        # Get sites with security updates needed
        query = (
            select(
                SiteModule.site_id,
                func.count(SiteModule.id).label("security_updates_count"),
            )
            .select_from(SiteModule)
            .join(Site, SiteModule.site_id == Site.id)
            .where(SiteModule.security_update_available)
        )

        if org_id:
            query = query.where(Site.organization_id == org_id)

        query = query.group_by(SiteModule.site_id)

        result = await self.db.execute(query)
        sites_with_security_issues = result.fetchall()

        # Calculate vulnerability counts based on security update patterns
        critical = 0
        high = 0
        medium = 0
        low = 0

        for site_data in sites_with_security_issues:
            security_count = site_data.security_updates_count

            if security_count >= 4:
                critical += 1  # Sites with many security issues
            elif security_count >= 2:
                high += 1  # Sites with multiple security issues
            elif security_count == 1:
                medium += 1  # Sites with single security issue

        # Add some baseline low-priority items
        total_sites_query = select(func.count(Site.id)).select_from(Site)
        if org_id:
            total_sites_query = total_sites_query.where(Site.organization_id == org_id)

        total_sites_result = await self.db.execute(total_sites_query)
        total_sites = total_sites_result.scalar() or 0

        # Low priority items are sites with minor update issues
        low = max(0, total_sites - critical - high - medium)

        return VulnerabilityCount(critical=critical, high=high, medium=medium, low=low)

    async def _get_compliance_rate(self, user: User, org_id: Optional[int]) -> float:
        """Calculate compliance rate."""
        # Get sites with all modules up to date
        subquery = (
            select(
                SiteModule.site_id, func.count(SiteModule.id).label("outdated_count")
            )
            .select_from(SiteModule)
            .join(Module, SiteModule.module_id == Module.id)
            .where(
                and_(
                    SiteModule.latest_version_id.is_not(None),
                    SiteModule.latest_version_id != SiteModule.current_version_id,
                )
            )
            .group_by(SiteModule.site_id)
            .subquery()
        )

        query = (
            select(
                func.count(Site.id).label("total"),
                func.count(subquery.c.site_id).label("non_compliant"),
            )
            .select_from(Site)
            .outerjoin(subquery, Site.id == subquery.c.site_id)
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
        self, user: User, org_id: Optional[int], limit: int = 5
    ) -> List[RiskItem]:
        """Get top security risks."""
        # Get modules with the most outdated installations
        query = (
            select(
                Module.display_name,
                Module.id,
                func.count(SiteModule.id).label("affected_sites"),
                func.bool_or(ModuleVersion.is_security_update).label("has_security"),
            )
            .select_from(Module)
            .join(SiteModule, Module.id == SiteModule.module_id)
            .join(
                ModuleVersion,
                and_(
                    SiteModule.latest_version_id == ModuleVersion.id,
                    SiteModule.latest_version_id != SiteModule.current_version_id,
                ),
            )
            .join(Site, SiteModule.site_id == Site.id)
        )

        if org_id:
            query = query.where(Site.organization_id == org_id)

        query = query.group_by(Module.id, Module.display_name)
        query = query.having(func.bool_or(ModuleVersion.is_security_update))
        query = query.order_by(desc("affected_sites"))
        query = query.limit(limit)

        result = await self.db.execute(query)
        risks = []

        for row in result:
            risks.append(
                RiskItem(
                    id=f"module-{row.id}",
                    title=f"{row.display_name} needs security update",
                    impact_score=min(row.affected_sites * 10, 100),
                    affected_sites=row.affected_sites,
                    severity=(
                        SeverityLevel.CRITICAL
                        if row.has_security
                        else SeverityLevel.HIGH
                    ),
                    action_required=f"Update {row.display_name} on {row.affected_sites} sites",
                )
            )

        return risks

    async def _get_recent_activity(
        self, user: User, org_id: Optional[int], limit: int = 20
    ) -> List[ActivityItem]:
        """Get recent activity items."""
        # For now, return empty list
        # TODO: Implement activity tracking
        return []

    async def _get_metric_trends(
        self, user: User, org_id: Optional[int]
    ) -> Dict[str, List[TimeSeriesData]]:
        """Get trend data for various metrics."""
        # For now, return mock trends
        # TODO: Implement historical data tracking
        now = datetime.utcnow()

        trends = {"security_score": [], "vulnerabilities": [], "compliance": []}

        # Generate mock data points for the last 30 days
        for i in range(30):
            timestamp = now - timedelta(days=29 - i)

            trends["security_score"].append(
                TimeSeriesData(
                    timestamp=timestamp,
                    value=85 + (i % 10) - 5,  # Fluctuate between 80-90
                )
            )

            trends["compliance"].append(
                TimeSeriesData(
                    timestamp=timestamp,
                    value=90 + (i % 5) - 2,  # Fluctuate between 88-93
                )
            )

        return trends

    async def _get_security_stats(
        self, user: User, org_id: Optional[int]
    ) -> SecurityMetrics:
        """Get security-specific statistics."""
        # TODO: Implement actual metrics
        return SecurityMetrics(
            active_vulnerabilities=0,
            resolved_today=0,
            mean_time_to_patch=24.5,
            critical_sites=0,
            patched_this_week=0,
            patch_compliance=95.5,
        )

    async def _get_critical_modules(
        self, user: User, org_id: Optional[int], limit: int = 10
    ) -> List[ModuleRiskItem]:
        """Get critical modules needing updates."""
        # TODO: Implement actual critical module detection
        return []

    async def _get_vulnerability_timeline(
        self, user: User, org_id: Optional[int]
    ) -> List[TimeSeriesData]:
        """Get vulnerability trend over time."""
        # TODO: Implement actual vulnerability tracking
        return []

    async def _get_recent_patches(
        self, user: User, org_id: Optional[int], limit: int = 10
    ) -> List[ActivityItem]:
        """Get recently applied patches."""
        # TODO: Implement patch tracking
        return []

    async def _get_security_alerts(
        self, user: User, org_id: Optional[int], limit: int = 10
    ) -> List[ActivityItem]:
        """Get current security alerts."""
        # TODO: Implement security alert system
        return []

    async def _get_site_health(self, site_id: int) -> SiteHealth:
        """Calculate site health score."""
        # Count outdated modules
        query = (
            select(
                func.count(SiteModule.id).label("total"),
                func.sum(
                    case(
                        (
                            SiteModule.latest_version_id
                            != SiteModule.current_version_id,
                            1,
                        ),
                        else_=0,
                    )
                ).label("outdated"),
            )
            .select_from(SiteModule)
            .where(SiteModule.site_id == site_id)
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
            last_sync=site.updated_at or datetime.utcnow(),
        )

    async def _get_site_module_stats(self, site_id: int) -> SiteModuleStats:
        """Get module statistics for a site."""
        # Get module counts
        query = (
            select(
                func.count(SiteModule.id).label("total"),
                func.sum(
                    case(
                        (
                            SiteModule.latest_version_id
                            != SiteModule.current_version_id,
                            1,
                        ),
                        else_=0,
                    )
                ).label("needs_update"),
                func.sum(
                    case(
                        (
                            and_(
                                SiteModule.latest_version_id
                                != SiteModule.current_version_id,
                                SiteModule.security_update_available,
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("security_updates"),
            )
            .select_from(SiteModule)
            .where(SiteModule.site_id == site_id)
        )

        result = await self.db.execute(query)
        stats = result.first()

        if not stats:
            return SiteModuleStats(
                total=0, up_to_date=0, needs_update=0, security_updates=0
            )

        return SiteModuleStats(
            total=stats.total or 0,
            up_to_date=(stats.total or 0) - (stats.needs_update or 0),
            needs_update=stats.needs_update or 0,
            security_updates=stats.security_updates or 0,
        )

    async def _get_site_timeline(
        self, site_id: int, limit: int = 20
    ) -> List[ActivityItem]:
        """Get site activity timeline."""
        # TODO: Implement site activity tracking
        return []

    async def _get_site_recommendations(self, site_id: int) -> List[Recommendation]:
        """Get recommendations for a site."""
        recommendations = []

        # Check for security updates
        query = (
            select(Module.display_name, func.count(SiteModule.id).label("update_count"))
            .select_from(SiteModule)
            .join(Module, SiteModule.module_id == Module.id)
            .where(
                and_(
                    SiteModule.site_id == site_id,
                    SiteModule.latest_version_id != SiteModule.current_version_id,
                    SiteModule.security_update_available,
                )
            )
            .group_by(Module.display_name)
        )

        result = await self.db.execute(query)

        for row in result:
            recommendations.append(
                Recommendation(
                    id=f"security-update-{row.display_name}",
                    severity=SeverityLevel.CRITICAL,
                    title=f"Security update available for {row.display_name}",
                    description=f"{row.display_name} has {row.update_count} security updates available",
                    action=f"Update {row.display_name} to the latest version",
                )
            )

        return recommendations

    async def get_recent_activities(
        self, user: User, org_id: Optional[int], limit: int
    ) -> List[ActivityItem]:
        """Get recent activities for the activity endpoint."""
        return await self._get_recent_activity(user, org_id, limit)

    async def get_metric_trends(
        self, metric: str, period: str, points: int, user: User, org_id: Optional[int]
    ) -> List[TimeSeriesData]:
        """Get trend data for a specific metric."""
        # TODO: Implement actual trend calculation based on period
        trends = await self._get_metric_trends(user, org_id)

        metric_map = {
            "security_score": "security_score",
            "vulnerabilities": "vulnerabilities",
            "compliance": "compliance",
            "sites": "sites",
        }

        if metric in metric_map and metric_map[metric] in trends:
            return trends[metric_map[metric]]

        return []

    async def get_risk_matrix(
        self, user: User, org_id: Optional[int] = None, limit: int = 10
    ) -> Dict[str, Any]:
        """Get risk matrix data for sites."""

        # Get sites with their metrics
        sites_query = (
            select(
                Site.id,
                Site.name,
                Site.drupal_core_version,
                func.count(SiteModule.id).label("total_modules"),
                func.count(
                    case(
                        (SiteModule.security_update_available, SiteModule.id),
                        else_=None,
                    )
                ).label("security_updates"),
                func.count(
                    case((SiteModule.update_available, SiteModule.id), else_=None)
                ).label("regular_updates"),
            )
            .select_from(Site)
            .join(SiteModule, Site.id == SiteModule.site_id)
            .group_by(Site.id, Site.name, Site.drupal_core_version)
        )

        if org_id:
            sites_query = sites_query.where(Site.organization_id == org_id)

        sites_query = sites_query.limit(limit)

        result = await self.db.execute(sites_query)
        sites_data = result.all()

        # Calculate risk scores for each site
        risk_matrix = []
        site_names = []

        for site in sites_data:
            site_names.append(site.name)

            # Security risk: Based on security updates
            security_risk = min(
                100, site.security_updates * 25
            )  # Each security update adds 25 points

            # Performance risk: Based on outdated Drupal core version
            drupal_version = site.drupal_core_version or "10.0.0"
            major_version = int(drupal_version.split(".")[0])
            performance_risk = (
                85 if major_version < 10 else (70 if major_version == 10 else 30)
            )

            # Updates risk: Based on regular updates available
            updates_risk = min(
                100, site.regular_updates * 15
            )  # Each update adds 15 points

            risk_matrix.append(
                [
                    {
                        "value": security_risk,
                        "label": str(security_risk),
                        "severity": self._get_severity(security_risk),
                    },
                    {
                        "value": performance_risk,
                        "label": str(performance_risk),
                        "severity": self._get_severity(performance_risk),
                    },
                    {
                        "value": updates_risk,
                        "label": str(updates_risk),
                        "severity": self._get_severity(updates_risk),
                    },
                ]
            )

        return {
            "xAxis": site_names,
            "yAxis": ["Security", "Performance", "Updates"],
            "data": risk_matrix,
        }

    def _get_severity(self, score: int) -> str:
        """Get severity level based on risk score."""
        if score >= 75:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 30:
            return "medium"
        elif score >= 10:
            return "low"
        else:
            return "info"

    async def update_site_tracking_data(self, site_id: int) -> None:
        """
        Update site tracking fields with calculated values.
        Called after module sync or update detection.
        """
        # Get the site
        site = await self.db.get(Site, site_id)
        if not site:
            return

        # Calculate all tracking metrics
        tasks = [
            self._calculate_site_security_score(site_id),
            self._calculate_site_module_counts(site_id),
        ]

        results = await asyncio.gather(*tasks)
        security_score, module_counts = results

        # Update the site with calculated values
        site.security_score = security_score
        site.total_modules_count = module_counts["total"]
        site.security_updates_count = module_counts["security_updates"]
        site.non_security_updates_count = module_counts["non_security_updates"]
        site.last_data_push = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(site)

    async def _calculate_site_security_score(self, site_id: int) -> int:
        """Calculate security score for a specific site."""
        # Get module statistics for this site
        query = (
            select(
                func.count(SiteModule.id).label("total_modules"),
                func.sum(case((SiteModule.update_available, 1), else_=0)).label(
                    "modules_needing_updates"
                ),
                func.sum(
                    case((SiteModule.security_update_available, 1), else_=0)
                ).label("security_updates_needed"),
            )
            .select_from(SiteModule)
            .where(
                and_(
                    SiteModule.site_id == site_id,
                    SiteModule.enabled,
                    SiteModule.is_active,
                )
            )
        )

        result = await self.db.execute(query)
        stats = result.first()

        if not stats or stats.total_modules == 0:
            return 100  # No modules means perfect score

        total_modules = stats.total_modules
        security_updates_needed = stats.security_updates_needed or 0
        modules_needing_updates = stats.modules_needing_updates or 0

        # Base score: percentage of modules up to date
        modules_up_to_date = total_modules - modules_needing_updates
        base_score = (modules_up_to_date / total_modules) * 100

        # Security penalty: Each security update reduces score significantly
        security_penalty = min(security_updates_needed * 20, 80)  # Max 80% penalty

        # Final score
        final_score = max(base_score - security_penalty, 0)

        return int(round(final_score))

    async def _calculate_site_module_counts(self, site_id: int) -> Dict[str, int]:
        """Calculate module counts for a specific site."""
        query = (
            select(
                func.count(SiteModule.id).label("total"),
                func.sum(
                    case((SiteModule.security_update_available, 1), else_=0)
                ).label("security_updates"),
                func.sum(
                    case(
                        (
                            and_(
                                SiteModule.update_available,
                                not SiteModule.security_update_available,
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("non_security_updates"),
            )
            .select_from(SiteModule)
            .where(
                and_(
                    SiteModule.site_id == site_id,
                    SiteModule.enabled,
                    SiteModule.is_active,
                )
            )
        )

        result = await self.db.execute(query)
        stats = result.first()

        return {
            "total": stats.total or 0,
            "security_updates": stats.security_updates or 0,
            "non_security_updates": stats.non_security_updates or 0,
        }

    async def update_all_sites_tracking_data(self, org_id: Optional[int] = None) -> int:
        """
        Update tracking data for all sites (or all sites in an organization).
        Returns number of sites updated.
        """
        # Get all active sites
        query = select(Site.id).filter(and_(Site.is_active, not Site.is_deleted))

        if org_id:
            query = query.filter(Site.organization_id == org_id)

        result = await self.db.execute(query)
        site_ids = [row.id for row in result.fetchall()]

        # Update each site
        for site_id in site_ids:
            await self.update_site_tracking_data(site_id)

        return len(site_ids)
