# Import all models here to ensure they are registered with SQLAlchemy
from app.models.api_key import ApiKey
from app.models.base import Base
from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.organization import Organization
from app.models.role import Permission, Role, UserRole, role_permissions
from app.models.site import Site
from app.models.site_module import SiteModule
from app.models.user import User
from app.models.user_organization import user_organization

# Export all models
__all__ = [
    "Base",
    "User",
    "Organization",
    "Site",
    "Module",
    "ModuleVersion",
    "SiteModule",
    "user_organization",
    "ApiKey",
    "Role",
    "Permission",
    "UserRole",
    "role_permissions",
]
