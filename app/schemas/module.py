from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field


class ModuleBase(BaseModel):
    """Base schema for Module with common fields."""
    machine_name: str = Field(..., min_length=1, max_length=255, description="Unique machine name for the module")
    display_name: str = Field(..., min_length=1, max_length=255, description="Human-readable display name")
    drupal_org_link: Optional[HttpUrl] = Field(None, description="Link to Drupal.org project page")
    module_type: str = Field(default="contrib", pattern="^(contrib|custom|core)$", description="Type of module")
    description: Optional[str] = Field(None, description="Module description")


class ModuleCreate(ModuleBase):
    """Schema for creating a new module."""
    pass


class ModuleUpdate(BaseModel):
    """Schema for updating an existing module."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    drupal_org_link: Optional[HttpUrl] = None
    description: Optional[str] = None
    module_type: Optional[str] = Field(None, pattern="^(contrib|custom|core)$")


class ModuleInDB(ModuleBase):
    """Schema for module as stored in database."""
    id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class ModuleResponse(ModuleInDB):
    """Schema for module API responses with calculated fields."""
    versions_count: int = Field(0, description="Number of versions tracked for this module")
    sites_count: int = Field(0, description="Number of sites with this module installed")
    latest_version: Optional[str] = Field(None, description="Latest version string")
    has_security_update: bool = Field(False, description="Whether any version has security updates available")


class ModuleListResponse(BaseModel):
    """Schema for paginated module list responses."""
    data: List[ModuleResponse]
    total: int
    page: int
    per_page: int
    pages: int