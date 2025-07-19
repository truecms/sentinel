"""Permission checking service and decorators for RBAC system."""

from functools import wraps
from typing import Callable, Optional, Union

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_or_site, get_db
from app.models.site import Site
from app.models.user import User


class PermissionChecker:
    """Service for checking permissions in RBAC system."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._permission_cache = {}

    async def user_has_permission(
        self, user: User, permission: str, organization_id: Optional[int] = None
    ) -> bool:
        """Check if user has a specific permission."""
        # Check cache first
        cache_key = f"user:{user.id}:{permission}:{organization_id}"
        if cache_key in self._permission_cache:
            return self._permission_cache[cache_key]

        # Check superuser privilege
        if user.is_superuser:
            self._permission_cache[cache_key] = True
            return True

        # Check user's roles for the permission
        result = user.has_permission(permission, organization_id)
        self._permission_cache[cache_key] = result
        return result

    async def user_has_resource_action(
        self,
        user: User,
        resource: str,
        action: str,
        organization_id: Optional[int] = None,
    ) -> bool:
        """Check if user has permission for a specific resource and action."""
        # Check cache first
        cache_key = f"user:{user.id}:{resource}:{action}:{organization_id}"
        if cache_key in self._permission_cache:
            return self._permission_cache[cache_key]

        # Check superuser privilege
        if user.is_superuser:
            self._permission_cache[cache_key] = True
            return True

        # Check user's roles for the resource and action
        result = user.has_resource_action(resource, action, organization_id)
        self._permission_cache[cache_key] = result
        return result

    async def site_has_permission(self, site: Site, permission: str) -> bool:
        """Check if site has a specific permission (sites have limited permissions)."""
        # Sites can only perform certain actions
        allowed_site_permissions = [
            "module:read",
            "module:write",
            "site:read",
            "site:write",
            "site:sync",
        ]

        return permission in allowed_site_permissions

    async def site_has_resource_action(
        self, site: Site, resource: str, action: str
    ) -> bool:
        """Check if site has permission for a specific resource and action."""
        # Sites can only work with modules and their own site data
        if resource == "module" and action in ["read", "write"]:
            return True
        elif resource == "site" and action in ["read", "write", "sync"]:
            return True

        return False

    async def check_permission(
        self,
        auth_subject: Union[User, Site],
        permission: str,
        organization_id: Optional[int] = None,
    ) -> bool:
        """Check permission for either user or site."""
        if isinstance(auth_subject, User):
            return await self.user_has_permission(
                auth_subject, permission, organization_id
            )
        elif isinstance(auth_subject, Site):
            return await self.site_has_permission(auth_subject, permission)
        else:
            return False

    async def check_resource_action(
        self,
        auth_subject: Union[User, Site],
        resource: str,
        action: str,
        organization_id: Optional[int] = None,
    ) -> bool:
        """Check resource action permission for either user or site."""
        if isinstance(auth_subject, User):
            return await self.user_has_resource_action(
                auth_subject, resource, action, organization_id
            )
        elif isinstance(auth_subject, Site):
            return await self.site_has_resource_action(auth_subject, resource, action)
        else:
            return False


def require_permission(permission: str):
    """Decorator to require a specific permission."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request, db, and current user/site from kwargs
            # request = kwargs.get("request")  # Unused for now
            db = kwargs.get("db")
            auth_subject = kwargs.get("current_user") or kwargs.get("current_site")

            if not db:
                raise HTTPException(
                    status_code=500, detail="Database session not available"
                )

            if not auth_subject:
                raise HTTPException(status_code=401, detail="Authentication required")

            # Extract organization_id from path params if available
            organization_id = kwargs.get("organization_id")

            # Check permission
            permission_checker = PermissionChecker(db)
            has_permission = await permission_checker.check_permission(
                auth_subject, permission, organization_id
            )

            if not has_permission:
                raise HTTPException(
                    status_code=403, detail=f"Missing permission: {permission}"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_resource_action(resource: str, action: str):
    """Decorator to require a specific resource and action permission."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request, db, and current user/site from kwargs
            # request = kwargs.get("request")  # Unused for now
            db = kwargs.get("db")
            auth_subject = kwargs.get("current_user") or kwargs.get("current_site")

            if not db:
                raise HTTPException(
                    status_code=500, detail="Database session not available"
                )

            if not auth_subject:
                raise HTTPException(status_code=401, detail="Authentication required")

            # Extract organization_id from path params if available
            organization_id = kwargs.get("organization_id")

            # Check permission
            permission_checker = PermissionChecker(db)
            has_permission = await permission_checker.check_resource_action(
                auth_subject, resource, action, organization_id
            )

            if not has_permission:
                raise HTTPException(
                    status_code=403, detail=f"Missing permission: {resource}:{action}"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_superuser():
    """Decorator to require superuser privileges."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current user from kwargs
            current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")

            if not isinstance(current_user, User):
                raise HTTPException(
                    status_code=403, detail="User authentication required"
                )

            if not current_user.is_superuser:
                raise HTTPException(
                    status_code=403, detail="Superuser privileges required"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_organization_access(organization_id_param: str = "organization_id"):
    """Decorator to require access to a specific organization."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current user and organization_id from kwargs
            current_user = kwargs.get("current_user")
            organization_id = kwargs.get(organization_id_param)

            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")

            if not isinstance(current_user, User):
                raise HTTPException(
                    status_code=403, detail="User authentication required"
                )

            if not organization_id:
                raise HTTPException(status_code=400, detail="Organization ID required")

            # Check if user is superuser
            if current_user.is_superuser:
                return await func(*args, **kwargs)

            # Check if user has access to the organization
            user_org_ids = [org.id for org in current_user.organizations]
            if organization_id not in user_org_ids:
                raise HTTPException(
                    status_code=403, detail="Access denied to organization"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Dependency factory for permission checking
def require_permission_dependency(permission: str):
    """Create a dependency that checks for a specific permission."""

    async def check_permission_dependency(
        request: Request,
        db: AsyncSession = Depends(get_db),
        auth_subject: Union[User, Site] = Depends(get_current_user_or_site),
    ) -> Union[User, Site]:
        organization_id = request.path_params.get("organization_id")

        permission_checker = PermissionChecker(db)
        has_permission = await permission_checker.check_permission(
            auth_subject, permission, organization_id
        )

        if not has_permission:
            raise HTTPException(
                status_code=403, detail=f"Missing permission: {permission}"
            )

        return auth_subject

    return check_permission_dependency


def require_resource_action_dependency(resource: str, action: str):
    """Create a dependency that checks for a specific resource and action."""

    async def check_resource_action_dependency(
        request: Request,
        db: AsyncSession = Depends(get_db),
        auth_subject: Union[User, Site] = Depends(get_current_user_or_site),
    ) -> Union[User, Site]:
        organization_id = request.path_params.get("organization_id")

        permission_checker = PermissionChecker(db)
        has_permission = await permission_checker.check_resource_action(
            auth_subject, resource, action, organization_id
        )

        if not has_permission:
            raise HTTPException(
                status_code=403, detail=f"Missing permission: {resource}:{action}"
            )

        return auth_subject

    return check_resource_action_dependency
