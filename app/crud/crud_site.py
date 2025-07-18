from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site import Site
from app.models.user import User
from app.schemas.site import SiteCreate, SiteUpdate

# Define allowed sort fields for validation
ALLOWED_SORT_FIELDS = [
    "name",
    "url",
    "security_score",
    "total_modules_count",
    "security_updates_count",
    "non_security_updates_count",
    "last_data_push",
    "last_drupal_org_check",
    "created_at",
    "updated_at",
]


async def get_site(db: AsyncSession, site_id: int) -> Optional[Site]:
    result = await db.execute(select(Site).filter(Site.id == site_id))
    return result.scalar_one_or_none()


async def get_site_by_url(db: AsyncSession, url: str) -> Optional[Site]:
    result = await db.execute(select(Site).filter(Site.url == url))
    return result.scalar_one_or_none()


async def get_sites(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Site]:
    result = await db.execute(select(Site).offset(skip).limit(limit))
    return result.scalars().all()


async def create_site(db: AsyncSession, site: SiteCreate, created_by: int) -> Site:
    db_site = Site(
        url=site.url,
        name=site.name,
        description=site.description,
        organization_id=site.organization_id,
        created_by=created_by,
        updated_by=created_by,
    )
    db.add(db_site)
    await db.commit()
    await db.refresh(db_site)
    return db_site


async def update_site(
    db: AsyncSession, site_id: int, site: SiteUpdate, updated_by: int
) -> Optional[Site]:
    db_site = await get_site(db, site_id)
    if db_site:
        if site.url:
            db_site.url = site.url
        if site.name:
            db_site.name = site.name
        if site.description:
            db_site.description = site.description
        if site.organization_id:
            db_site.organization_id = site.organization_id
        if site.is_active is not None:
            db_site.is_active = site.is_active
        if site.is_deleted is not None:
            db_site.is_deleted = site.is_deleted
        db_site.updated_by = updated_by
        await db.commit()
        await db.refresh(db_site)
    return db_site


async def delete_site(
    db: AsyncSession, site_id: int, updated_by: int
) -> Optional[Site]:
    db_site = await get_site(db, site_id)
    if db_site:
        db_site.is_deleted = True
        db_site.updated_by = updated_by
        await db.commit()
        await db.refresh(db_site)
    return db_site


async def get_sites_overview(
    db: AsyncSession,
    user: User,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
) -> Tuple[List[Site], int]:
    """
    Get sites overview with security metrics and update tracking.

    Returns sites with calculated overview data, respecting user permissions.
    Non-superusers only see sites from their organization.
    """
    # Validate sort field first to avoid unnecessary database queries
    if sort_by not in ALLOWED_SORT_FIELDS:
        raise ValueError(
            f"Invalid sort field: {sort_by}. "
            f"Allowed fields: {', '.join(ALLOWED_SORT_FIELDS)}"
        )

    # Base query
    query = select(Site).filter(
        and_(Site.is_active.is_(True), Site.is_deleted.is_(False))
    )

    # Apply organization filter for non-superusers
    if not user.is_superuser and user.organization_id:
        query = query.filter(Site.organization_id == user.organization_id)

    # Apply search filter
    if search:
        search_filter = or_(
            Site.name.ilike(f"%{search}%"), Site.url.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    # Count total results - use direct count to avoid cartesian product
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Apply sorting
    sort_column = getattr(Site, sort_by)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    sites = result.scalars().all()

    return sites, total
