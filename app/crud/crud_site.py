from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.site import Site
from app.schemas.site import SiteCreate, SiteUpdate

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
        updated_by=created_by
    )
    db.add(db_site)
    await db.commit()
    await db.refresh(db_site)
    return db_site

async def update_site(db: AsyncSession, site_id: int, site: SiteUpdate, updated_by: int) -> Optional[Site]:
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

async def delete_site(db: AsyncSession, site_id: int, updated_by: int) -> Optional[Site]:
    db_site = await get_site(db, site_id)
    if db_site:
        db_site.is_deleted = True
        db_site.updated_by = updated_by
        await db.commit()
        await db.refresh(db_site)
    return db_site
