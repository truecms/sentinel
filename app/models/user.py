from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.user_organization import user_organization

if TYPE_CHECKING:
    from app.models.role import Role

class User(Base):
    _ = "users"

    _ = Column(Integer, primary_key=True, index=True)
    _ = Column(String, unique=True, index=True, nullable=False)
    _ = Column(String, nullable=True)
    _ = Column(String, nullable=False)
    _ = Column(Boolean(), default=True)
    _ = Column(Boolean(), default=False)
    _ = Column(DateTime, nullable=False, server_default=text("now()"))
    _ = Column(DateTime, nullable=False, server_default=text("now()"))
    _ = Column(DateTime, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    role = Column(String, nullable=True)

    # Relationships
    _ = relationship(
        "Organization", foreign_keys=[organization_id], back_populates="users"
    )
    _ = relationship(
        "Organization", secondary=user_organization, back_populates="users"
    )
    _ = relationship(
        "Organization",
        back_populates="creator",
        foreign_keys="[Organization.created_by]",
    )

    # API Keys and RBAC relationships
    _ = relationship("ApiKey", back_populates="user")
    _ = relationship(
        "UserRole", back_populates="user", foreign_keys="[UserRole.user_id]"
    )
    _ = relationship(
        "UserRole",
        _="assigned_by",
        _="[UserRole.assigned_by_id]",
    )

    def get_roles(self, organization_id: Optional[int] = None) -> List["Role"]:
        """Get user's roles, optionally filtered by organization."""

        roles = []
        for user_role in self.user_roles:
            if not user_role.is_active():
                continue

            # Include global roles
            if user_role.is_global():
                roles.append(user_role.role)
            # Include organization-specific roles if organization_id matches
            elif organization_id and user_role.organization_id == organization_id:
                roles.append(user_role.role)

        return roles

    def has_role(self, role_name: str, organization_id: Optional[int] = None) -> bool:
        """Check if user has a specific role."""
        roles = self.get_roles(organization_id)
        return any(role.name == role_name for role in roles)

    def has_permission(
        self, permission_name: str, organization_id: Optional[int] = None
    ) -> bool:
        """Check if user has a specific permission."""
        roles = self.get_roles(organization_id)
        return any(role.has_permission(permission_name) for role in roles)

    def has_resource_action(
        self, resource: str, action: str, organization_id: Optional[int] = None
    ) -> bool:
        """Check if user has permission for a specific resource and action."""
        roles = self.get_roles(organization_id)
        return any(role.has_resource_action(resource, action) for role in roles)

    def get_permissions(self, organization_id: Optional[int] = None) -> List[str]:
        """Get all permissions for this user."""
        permissions = set()
        roles = self.get_roles(organization_id)

        for role in roles:
            permissions.update(role.get_permissions_list())

        return list(permissions)
