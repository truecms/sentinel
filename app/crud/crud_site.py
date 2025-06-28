from typing import Optional

from sqlalchemy.orm import Session

from app.models.site import Site
from app.schemas.site import SiteCreate, SiteUpdate

def get_site(db: Session, site_id: int) -> Optional[Site]:
    return db.query(Site).filter(Site.id == site_id).first()

def get_site_by_url(db: Session, url: str) -> Optional[Site]:
    return db.query(Site).filter(Site.url == url).first()

def get_sites(db: Session, skip: int = 0, limit: int = 100) -> list[Site]:
    return db.query(Site).offset(skip).limit(limit).all()

def create_site(db: Session, site: SiteCreate, created_by: int) -> Site:
    db_site = Site(
        url=site.url,
        name=site.name,
        description=site.description,
        organization_id=site.organization_id,
        created_by=created_by,
        updated_by=created_by
    )
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site

def update_site(db: Session, site_id: int, site: SiteUpdate, updated_by: int) -> Optional[Site]:
    db_site = get_site(db, site_id)
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
        db.commit()
        db.refresh(db_site)
    return db_site

def delete_site(db: Session, site_id: int, updated_by: int) -> Optional[Site]:
    db_site = get_site(db, site_id)
    if db_site:
        db_site.is_deleted = True
        db_site.updated_by = updated_by
        db.commit()
        db.refresh(db_site)
    return db_site
