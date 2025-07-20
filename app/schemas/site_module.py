from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.module import ModuleResponse
from app.schemas.module_version import ModuleVersionResponse


class SiteModuleBase(BaseModel):
    """Base schema for SiteModule with common fields."""

    enabled: bool = Field(True, description="Whether the module is enabled on the site")


class SiteModuleCreate(SiteModuleBase):
    """Schema for creating a new site-module association."""

    site_id: int = Field(..., description="ID of the site")
    module_id: int = Field(..., description="ID of the module")
    current_version_id: int = Field(
        ..., description="ID of the currently installed version"
    )


class SiteModuleUpdate(BaseModel):
    """Schema for updating an existing site-module association."""

    enabled: Optional[bool] = Field(None, description="Whether the module is enabled")
    current_version_id: Optional[int] = Field(
        None, description="ID of the new current version"
    )


class SiteModuleInDB(SiteModuleBase):
    """Schema for site-module association as stored in database."""

    id: int
    site_id: int
    module_id: int
    current_version_id: int
    update_available: bool = Field(..., description="Whether an update is available")
    security_update_available: bool = Field(
        ..., description="Whether a security update is available"
    )
    latest_version_id: Optional[int] = Field(
        None, description="ID of the latest available version"
    )
    first_seen: datetime = Field(
        ..., description="When this module was first detected on the site"
    )
    last_seen: datetime = Field(
        ..., description="When this module was last seen on the site"
    )
    last_updated: Optional[datetime] = Field(
        None, description="When the version was last changed"
    )
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        _ = True


class SiteModuleResponse(SiteModuleInDB):
    """Schema for site-module API responses with nested objects."""

    module: ModuleResponse = Field(..., description="Module information")
    current_version: ModuleVersionResponse = Field(
        ..., description="Currently installed version"
    )
    latest_version: Optional[ModuleVersionResponse] = Field(
        None, description="Latest available version"
    )
    site_name: str = Field(..., description="Name of the site")
    site_url: str = Field(..., description="URL of the site")


class SiteModuleSummary(BaseModel):
    """Schema for summarized site-module information."""

    id: int
    module_machine_name: str
    module_display_name: str
    current_version: str
    latest_version: Optional[str] = None
    enabled: bool
    update_available: bool
    security_update_available: bool
    last_seen: datetime


class SiteModuleListResponse(BaseModel):
    """Schema for paginated site-module list responses."""

    data: List[SiteModuleResponse]
    total: int
    page: int
    per_page: int
    pages: int


class SiteModuleStatsResponse(BaseModel):
    """Schema for site-module statistics."""

    total_modules: int = Field(..., description="Total number of modules installed")
    enabled_modules: int = Field(..., description="Number of enabled modules")
    disabled_modules: int = Field(..., description="Number of disabled modules")
    modules_with_updates: int = Field(
        ..., description="Number of modules with available updates"
    )
    modules_with_security_updates: int = Field(
        ..., description="Number of modules with security updates"
    )
    contrib_modules: int = Field(..., description="Number of contributed modules")
    custom_modules: int = Field(..., description="Number of custom modules")
    core_modules: int = Field(..., description="Number of core modules")
