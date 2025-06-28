from typing import Optional

from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate

def get_organization(db: Session, organization_id: int) -> Optional[Organization]:
    return db.query(Organization).filter(Organization.id == organization_id).first()

def get_organization_by_name(db: Session, name: str) -> Optional[Organization]:
    return db.query(Organization).filter(Organization.name == name).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> list[Organization]:
    return db.query(Organization).offset(skip).limit(limit).all()

def create_organization(db: Session, organization: OrganizationCreate, created_by: int) -> Organization:
    db_organization = Organization(
        name=organization.name,
        tax_id=organization.tax_id,
        created_by=created_by,
        updated_by=created_by
    )
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization

def update_organization(db: Session, organization_id: int, organization: OrganizationUpdate, updated_by: int) -> Optional[Organization]:
    db_organization = get_organization(db, organization_id)
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
        db.commit()
        db.refresh(db_organization)
    return db_organization

def delete_organization(db: Session, organization_id: int, updated_by: int) -> Optional[Organization]:
    db_organization = get_organization(db, organization_id)
    if db_organization:
        db_organization.is_deleted = True
        db_organization.updated_by = updated_by
        db.commit()
        db.refresh(db_organization)
    return db_organization
