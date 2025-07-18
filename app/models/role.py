"""Role model for RBAC system."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base

# Junction table for role-permission many-to-many relationship
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
    Column("granted_by_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("granted_at", DateTime, server_default=func.now()),
)


class Role(Base):
    """Role model for RBAC system."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role")

    def __repr__(self) -> str:
        """String representation of the role."""
        return f"<Role {self.name}>"

    def has_permission(self, permission_name: str) -> bool:
        """Check if this role has a specific permission."""
        return any(perm.name == permission_name for perm in self.permissions)

    def has_resource_action(self, resource: str, action: str) -> bool:
        """Check if this role has permission for a specific resource and action."""
        # Check for exact match
        permission_name = f"{resource}:{action}"
        if self.has_permission(permission_name):
            return True

        # Check for wildcard permissions
        if self.has_permission("*:*"):  # Super admin
            return True

        if self.has_permission(f"{resource}:*"):  # All actions on resource
            return True

        if self.has_permission(f"*:{action}"):  # Specific action on all resources
            return True

        return False

    def get_permissions_list(self) -> List[str]:
        """Get a list of all permission names for this role."""
        return [perm.name for perm in self.permissions]

    @classmethod
    def create_system_role(
        cls, name: str, display_name: str, description: Optional[str] = None
    ) -> "Role":
        """Create a system role."""
        return cls(
            name=name,
            display_name=display_name,
            description=description,
            is_system=True,
        )

    @classmethod
    def create_custom_role(
        cls, name: str, display_name: str, description: Optional[str] = None
    ) -> "Role":
        """Create a custom role."""
        return cls(
            name=name,
            display_name=display_name,
            description=description,
            is_system=False,
        )


class Permission(Base):
    """Permission model for RBAC system."""

    _ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    resource = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    _ = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self) -> str:
        """String representation of the permission."""
        return f"<Permission {self.name}>"

    @classmethod
    def create_permission(
        cls, resource: str, action: str, description: Optional[str] = None
    ) -> "Permission":
        """Create a new permission."""
        name = f"{resource}:{action}"
        return cls(name=name, resource=resource, action=action, description=description)

    @property
    def is_wildcard(self) -> bool:
        """Check if this is a wildcard permission."""
        return "*" in self.resource or "*" in self.action


class UserRole(Base):
    """User-Role assignment model with organization scope."""

    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id"), nullable=True, index=True
    )
    valid_from = Column(DateTime, server_default=func.now())
    valid_until = Column(DateTime, nullable=True)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    organization = relationship("Organization")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])

    def __repr__(self) -> str:
        """String representation of the user role assignment."""
        org_part = (
            f" in org {self.organization_id}" if self.organization_id else " globally"
        )
        return f"<UserRole user={self.user_id} role={self.role_id}{org_part}>"

    def is_active(self) -> bool:
        """Check if this role assignment is currently active."""
        now = datetime.utcnow()

        # Check if role is within valid time range
        if self.valid_from and now < self.valid_from:
            return False

        if self.valid_until and now > self.valid_until:
            return False

        return True

    def is_global(self) -> bool:
        """Check if this role assignment is global (not organization-scoped)."""
        return self.organization_id is None

    def is_organization_scoped(self) -> bool:
        """Check if this role assignment is organization-scoped."""
        return self.organization_id is not None

    @classmethod
    def assign_role(
        cls,
        user_id: int,
        role_id: int,
        organization_id: Optional[int] = None,
        assigned_by_id: Optional[int] = None,
        valid_until: Optional[datetime] = None,
    ) -> "UserRole":
        """Assign a role to a user."""
        return cls(
            user_id=user_id,
            role_id=role_id,
            organization_id=organization_id,
            assigned_by_id=assigned_by_id,
            valid_until=valid_until,
        )
