"""Role management endpoints for RBAC system."""

from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api import deps
from app.core.permissions import require_resource_action_dependency
from app.models.organization import Organization
from app.models.role import Permission, Role, UserRole
from app.models.site import Site
from app.models.user import User
    PermissionResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    UserRoleCreate,
    UserRoleResponse,
    UserRoleUpdate,
)

router = APIRouter()

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    request: Request,
    db: AsyncSession = Depends(deps.get_db),
    auth_subject: Union[User, Site] = Depends(
        require_resource_action_dependency("user", "read")
    ),
) -> List[Role]:
    """List all available roles."""
    query = select(Role).options(selectinload(Role.permissions))
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    request: Request,
    db: AsyncSession = Depends(deps.get_db),
    auth_subject: Union[User, Site] = Depends(
        require_resource_action_dependency("user", "read")
    ),
) -> List[Permission]:
    """List all available permissions."""
    query = select(Permission)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/users/{user_id}/roles", response_model=List[UserRoleResponse])
async def get_user_roles(
    user_id: int,
    organization_id: Optional[int] = None,
    request: Request = None,
    db: AsyncSession = Depends(deps.get_db),
    auth_subject: Union[User, Site] = Depends(
        require_resource_action_dependency("user", "read")
    ),
) -> List[UserRole]:
    """Get user's role assignments."""
    # Check if user exists
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Build query for user roles
    query = (
        select(UserRole)
        .where(UserRole.user_id == user_id)
        .options(
            selectinload(UserRole.role),
            selectinload(UserRole.organization),
            selectinload(UserRole.assigned_by),
        )
    )

    # Filter by organization if specified
    if organization_id is not None:
        query = query.where(UserRole.organization_id == organization_id)

    result = await db.execute(query)
    user_roles = result.scalars().all()

    # Filter to only active roles
    active_roles = [ur for ur in user_roles if ur.is_active()]

    return active_roles

@router.post("/users/{user_id}/roles", response_model=UserRoleResponse)
async def assign_role_to_user(
    user_id: int,
    role_data: UserRoleCreate,
    request: Request = None,
    db: AsyncSession = Depends(deps.get_db),
    auth_subject: Union[User, Site] = Depends(
        require_resource_action_dependency("user", "assign_roles")
    ),
) -> UserRole:
    """Assign a role to a user."""
    # Only users can assign roles (not sites)
    if not isinstance(auth_subject, User):
        raise HTTPException(status_code=403, detail="User authentication required")

    # Check if user exists
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if role exists
    role = await db.get(Role, role_data.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Check if organization exists (if specified)
    if role_data.organization_id:
        organization = await db.get(Organization, role_data.organization_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

    # Check if assignment already exists
    existing_query = select(UserRole).where(
        UserRole.user_id == user_id,
        UserRole.role_id == role_data.role_id,
        UserRole.organization_id == role_data.organization_id,
    )
    existing_result = await db.execute(existing_query)
    existing_assignment = existing_result.scalar_one_or_none()

    if existing_assignment:
        if existing_assignment.is_active():
            raise HTTPException(
                status_code=400, detail="Role assignment already exists"
            )
        else:
            # Reactivate existing assignment
            existing_assignment.valid_from = role_data.valid_from
            existing_assignment.valid_until = role_data.valid_until
            existing_assignment.assigned_by_id = auth_subject.id
            await db.commit()
            await db.refresh(existing_assignment)
            return existing_assignment

    # Create new assignment
    user_role = UserRole.assign_role(
        user_id=user_id,
        role_id=role_data.role_id,
        organization_id=role_data.organization_id,
        _=auth_subject.id,
        valid_until=role_data.valid_until,
    )

    db.add(user_role)
    await db.commit()
    await db.refresh(user_role)

    return user_role

@router.delete("/users/{user_id}/roles/{role_id}")
async def revoke_role_from_user(
    user_id: int,
    role_id: int,
    organization_id: Optional[int] = None,
    request: Request = None,
    db: AsyncSession = Depends(deps.get_db),
    auth_subject: Union[User, Site] = Depends(
        require_resource_action_dependency("user", "assign_roles")
    ),
) -> dict:
    """Revoke a role from a user."""
    # Only users can revoke roles (not sites)
    if not isinstance(auth_subject, User):
        raise HTTPException(status_code=403, detail="User authentication required")

    # Find the role assignment
    query = select(UserRole).where(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
        UserRole.organization_id == organization_id,
    )
    result = await db.execute(query)
    user_role = result.scalar_one_or_none()

    if not user_role:
        raise HTTPException(status_code=404, detail="Role assignment not found")

    if not user_role.is_active():
        raise HTTPException(
            status_code=400, detail="Role assignment is already inactive"
        )

    # Revoke the role by setting valid_until to now
    from datetime import datetime

    user_role.valid_until = datetime.utcnow()

    await db.commit()

    return {"message": "Role revoked successfully"}

@router.get("/users/{user_id}/permissions", response_model=List[str])
async def get_user_permissions(
    user_id: int,
    organization_id: Optional[int] = None,
    request: Request = None,
    db: AsyncSession = Depends(deps.get_db),
    auth_subject: Union[User, Site] = Depends(
        require_resource_action_dependency("user", "read")
    ),
) -> List[str]:
    """Get all permissions for a user."""
    # Check if user exists
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user's permissions
    permissions = user.get_permissions(organization_id)

    return permissions

@router.post("/users/{user_id}/permissions/check")
async def check_user_permission(
    user_id: int,
    permission_data: dict,
    organization_id: Optional[int] = None,
    request: Request = None,
    db: AsyncSession = Depends(deps.get_db),
    auth_subject: Union[User, Site] = Depends(
        require_resource_action_dependency("user", "read")
    ),
) -> dict:
    """Check if user has a specific permission."""
    # Check if user exists
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Extract permission or resource/action
    if "permission" in permission_data:
        has_permission = user.has_permission(
            permission_data["permission"], organization_id
        )
    elif "resource" in permission_data and "action" in permission_data:
        has_permission = user.has_resource_action(
            permission_data["resource"], permission_data["action"], organization_id
        )
    else:
        raise HTTPException(
            _=400,
            _="Must provide either 'permission' or 'resource' and 'action'",
        )

    return {
        "user_id": user_id,
        "organization_id": organization_id,
        "has_permission": has_permission,
        "permission_data": permission_data,
    }
