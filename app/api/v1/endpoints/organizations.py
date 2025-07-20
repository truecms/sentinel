from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import schemas
from app.api import deps
from app.models import User
from app.models.organization import Organization
from app.models.site import Site
from app.models.user_organization import user_organization
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationDeleteResponse,
    OrganizationResponse,
    OrganizationUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[OrganizationResponse])
async def read_organizations(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Any:
    """Retrieve organizations."""
    # Build base query
    query = select(Organization).options(selectinload(Organization.users))

    # Apply filters
    if name:
        query = query.where(Organization.name.ilike(f"%{name}%"))
    if is_active is not None:
        query = query.where(Organization.is_active == is_active)

    # Always exclude soft-deleted organizations unless explicitly requested
    query = query.where(~Organization.is_deleted)

    # For non-superusers, only show organizations they belong to
    if not current_user.is_superuser:
        query = query.join(
            user_organization, Organization.id == user_organization.c.organization_id
        ).where(user_organization.c.user_id == current_user.id)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    organizations = result.unique().scalars().all()

    return organizations


@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_in: OrganizationCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create new organization."""
    # Check if user has permission - superusers or org_admins can create new organizations
    from app.models.role import UserRole, Role
    
    # Check if user is superuser
    if not current_user.is_superuser:
        # Check if user has org_admin role in any organization
        user_roles_query = (
            select(UserRole)
            .join(Role)
            .where(
                UserRole.user_id == current_user.id,
                Role.name == "org_admin"
            )
        )
        result = await db.execute(user_roles_query)
        has_org_admin_role = result.first() is not None
        
        if not has_org_admin_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions. Only administrators can create organizations.",
            )

    # Check if organization exists
    query = select(Organization).where(
        Organization.name == organization_in.name, ~Organization.is_deleted
    )
    result = await db.execute(query)
    organization = result.scalar_one_or_none()

    if organization:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The organization with this name already exists.",
        )

    # Create organization
    organization = Organization(
        name=organization_in.name,
        description=organization_in.description,
        created_by=organization_in.created_by or current_user.id,
        updated_by=current_user.id,
        is_active=True,
        is_deleted=False,
    )
    db.add(organization)
    await db.commit()
    await db.refresh(organization)
    
    # Add the creator to the organization
    await db.execute(
        user_organization.insert().values(
            user_id=current_user.id,
            organization_id=organization.id,
            is_default=False  # Not default since user already has a default org
        )
    )
    
    # Assign org_admin role to the creator in this organization
    from app.models.role import Role, UserRole
    
    # Get org_admin role
    role_query = select(Role).where(Role.name == "org_admin")
    result = await db.execute(role_query)
    org_admin_role = result.scalar_one_or_none()
    
    if org_admin_role:
        # Create user role assignment
        user_role = UserRole.assign_role(
            user_id=current_user.id,
            role_id=org_admin_role.id,
            organization_id=organization.id,
            assigned_by_id=current_user.id  # Self-assigned
        )
        db.add(user_role)
        await db.commit()

    # Add users to organization if specified
    if organization_in.users:
        for user_id in organization_in.users:
            # Check if user exists
            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

            if user:
                # Add user to organization
                await db.execute(
                    user_organization.insert().values(
                        user_id=user_id, organization_id=organization.id
                    )
                )
                # Update user's organization_id
                user.organization_id = organization.id
                db.add(user)

    await db.commit()
    await db.refresh(organization)

    # Reload organization with users
    query = (
        select(Organization)
        .options(selectinload(Organization.users))
        .where(Organization.id == organization.id)
    )
    result = await db.execute(query)
    organization = result.unique().scalar_one()

    return organization


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def read_organization(
    organization_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get a specific organization by id."""
    query = (
        select(Organization)
        .options(selectinload(Organization.users))
        .where(
            Organization.id == organization_id,
            Organization.is_active,
            ~Organization.is_deleted,
        )
    )
    result = await db.execute(query)
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    # Check if user has access to this organization
    if (
        not current_user.is_superuser
        and current_user.organization_id != organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return organization


@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    organization_in: OrganizationUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update an organization."""
    # Check if user has permission using RBAC
    from app.models.role import UserRole
    
    # Get the actual User model instance with roles loaded
    user_query = (
        select(User)
        .options(selectinload(User.user_roles).selectinload(UserRole.role))
        .where(User.id == current_user.id)
    )
    result = await db.execute(user_query)
    user = result.scalar_one()
    
    # Check if user has org_admin role for this organization or is superuser
    if not user.is_superuser and not user.has_role("org_admin", organization_id=organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Get organization
    query = (
        select(Organization)
        .options(selectinload(Organization.users))
        .where(
            Organization.id == organization_id,
            Organization.is_active,
            ~Organization.is_deleted,
        )
    )
    result = await db.execute(query)
    organization = result.unique().scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Update organization fields
    for field, value in organization_in.model_dump(exclude_unset=True).items():
        if field != "users":
            setattr(organization, field, value)

    organization.updated_by = current_user.id
    organization.updated_at = datetime.utcnow()

    # Update user associations if specified
    if organization_in.users is not None:
        # Remove existing user associations
        await db.execute(
            user_organization.delete().where(
                user_organization.c.organization_id == organization_id
            )
        )

        # Clear organization_id for users
        await db.execute(
            update(User)
            .where(User.organization_id == organization_id)
            .values(organization_id=None)
        )

        # Add new user associations
        for user_id in organization_in.users:
            # Check if user exists
            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

            if user:
                # Add user to organization
                await db.execute(
                    user_organization.insert().values(
                        user_id=user_id, organization_id=organization_id
                    )
                )
                # Update user's organization_id
                user.organization_id = organization_id
                db.add(user)

    await db.commit()
    await db.refresh(organization)

    # Reload organization with users
    query = (
        select(Organization)
        .options(selectinload(Organization.users))
        .where(Organization.id == organization_id)
    )
    result = await db.execute(query)
    organization = result.unique().scalar_one()

    return organization


@router.delete("/{organization_id}", response_model=OrganizationDeleteResponse)
async def delete_organization(
    organization_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Delete an organization."""
    # Check if organization exists and user has permission
    query = (
        select(Organization)
        .options(selectinload(Organization.users))
        .where(
            Organization.id == organization_id,
            Organization.is_active,
            ~Organization.is_deleted,
        )
    )
    result = await db.execute(query)
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    
    # Check if user has permission using RBAC
    from app.models.role import UserRole
    
    # Get the actual User model instance with roles loaded
    user_query = (
        select(User)
        .options(selectinload(User.user_roles).selectinload(UserRole.role))
        .where(User.id == current_user.id)
    )
    result = await db.execute(user_query)
    user = result.scalar_one()
    
    # Check if user has org_admin role for this organization or is superuser
    if not user.is_superuser and not user.has_role("org_admin", organization_id=organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Update associated users to remove organization_id
    user_update = (
        update(User)
        .where(User.organization_id == organization_id)
        .values(organization_id=None, updated_at=datetime.utcnow())
    )
    await db.execute(user_update)
    await db.commit()

    # Mark organization as deleted
    organization.is_active = False
    organization.is_deleted = True
    organization.updated_at = datetime.utcnow()
    organization.updated_by = current_user.id
    db.add(organization)
    await db.commit()
    await db.refresh(organization)

    return {
        "message": "Organization deleted successfully",
        "organization_id": organization.id,
        "name": organization.name,
    }


@router.get("/{organization_id}/sites", response_model=List[schemas.SiteResponse])
async def read_organization_sites(
    organization_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """Get all sites for a specific organization."""
    # Check if organization exists
    query = select(Organization).where(
        Organization.id == organization_id,
        Organization.is_active,
        ~Organization.is_deleted,
    )
    result = await db.execute(query)
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    # Check if user has access to this organization
    if (
        not current_user.is_superuser
        and current_user.organization_id != organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Get sites for the organization
    query = (
        select(Site)
        .where(
            Site.organization_id == organization_id,
            Site.is_active,
            ~Site.is_deleted,
        )
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    sites = result.scalars().all()

    return sites
