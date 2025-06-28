from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field


class ModuleVersionBase(BaseModel):
    """Base schema for ModuleVersion with common fields."""
    version_string: str = Field(..., min_length=1, max_length=50, description="Version string (e.g., '2.1.3')")
    semantic_version: Optional[str] = Field(None, max_length=50, description="Normalized semantic version for comparison")
    release_date: Optional[datetime] = Field(None, description="Date when this version was released")
    is_security_update: bool = Field(False, description="Whether this version contains security fixes")
    release_notes_link: Optional[HttpUrl] = Field(None, description="Link to release notes")
    drupal_core_compatibility: Optional[List[str]] = Field(None, description="Compatible Drupal core versions (e.g., ['9.x', '10.x'])")


class ModuleVersionCreate(ModuleVersionBase):
    """Schema for creating a new module version."""
    module_id: int = Field(..., description="ID of the module this version belongs to")


class ModuleVersionUpdate(BaseModel):
    """Schema for updating an existing module version."""
    semantic_version: Optional[str] = Field(None, max_length=50)
    release_date: Optional[datetime] = None
    is_security_update: Optional[bool] = None
    release_notes_link: Optional[HttpUrl] = None
    drupal_core_compatibility: Optional[List[str]] = None


class ModuleVersionInDB(ModuleVersionBase):
    """Schema for module version as stored in database."""
    id: int
    module_id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class ModuleVersionResponse(ModuleVersionInDB):
    """Schema for module version API responses with additional context."""
    module_name: str = Field(..., description="Display name of the module this version belongs to")
    module_machine_name: str = Field(..., description="Machine name of the module")


class ModuleVersionListResponse(BaseModel):
    """Schema for paginated module version list responses."""
    data: List[ModuleVersionResponse]
    total: int
    page: int
    per_page: int
    pages: int