from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


async def get_organization(db: AsyncSession, organization_id: int) -> Optional[Organization]:
    result = await db.execute(select(Organization).filter(Organization.id == organization_id))
    return result.scalar_one_or_none()


async def get_organization_by_name(db: AsyncSession, name: str) -> Optional[Organization]:
    result = await db.execute(select(Organization).filter(Organization.name == name))
    return result.scalar_one_or_none()


async def get_organizations(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Organization]:
    result = await db.execute(select(Organization).offset(skip).limit(limit))
    return result.scalars().all()


async def create_organization(
    db: AsyncSession, organization: OrganizationCreate, created_by: int
) -> Organization:
    db_organization = Organization(
        name=organization.name,
        tax_id=organization.tax_id,
        created_by=created_by,
        updated_by=created_by,
    )
    db.add(db_organization)
    await db.commit()
    await db.refresh(db_organization)
    return db_organization


async def update_organization(
    db: AsyncSession, organization_id: int, organization: OrganizationUpdate, updated_by: int
) -> Optional[Organization]:
    db_organization = await get_organization(db, organization_id)
    if db_organization:
        if organization.name:
            db_organization.name = organization.name
        if organization.tax_id:
            db_organization.tax_id = organization.tax_id
        if organization.is_active is not None:
            db_organization.is_active = organization.is_active
        if organization.is_deleted is not None:
            db_organization.is_deleted = organization.is_deleted
        db_organization.updated_by = updated_by
        await db.commit()
        await db.refresh(db_organization)
    return db_organization


async def delete_organization(
    db: AsyncSession, organization_id: int, updated_by: int
) -> Optional[Organization]:
    db_organization = await get_organization(db, organization_id)
    if db_organization:
        db_organization.is_deleted = True
        db_organization.updated_by = updated_by
        await db.commit()
        await db.refresh(db_organization)
    return db_organization
