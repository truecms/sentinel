from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ModuleVersionBase(BaseModel):
    """Base schema for ModuleVersion with common fields."""

    version_string: str = Field(
        ..., min_length=1, max_length=50, description="Version string (e.g., '2.1.3')"
    )
    release_date: Optional[datetime] = Field(
        None, description="Date when this version was released"
    )
    is_security_update: bool = Field(
        False, description="Whether this version contains security fixes"
    )
    release_notes: Optional[str] = Field(
        None, description="Release notes text"
    )
    drupal_core_compatibility: Optional[List[str]] = Field(
        None, description="Compatible Drupal core versions (e.g., ['9.x', '10.x'])"
    )


class ModuleVersionCreate(ModuleVersionBase):
    """Schema for creating a new module version."""

    module_id: int = Field(..., description="ID of the module this version belongs to")


class ModuleVersionUpdate(BaseModel):
    """Schema for updating an existing module version."""

    release_date: Optional[datetime] = None
    is_security_update: Optional[bool] = None
    release_notes: Optional[str] = None
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
        _ = True


class ModuleVersionResponse(ModuleVersionInDB):
    """Schema for module version API responses with additional context."""

    module_name: str = Field(
        ..., description="Display name of the module this version belongs to"
    )
    module_machine_name: str = Field(..., description="Machine name of the module")


class ModuleVersionListResponse(BaseModel):
    """Schema for paginated module version list responses."""

    data: List[ModuleVersionResponse]
    total: int
    page: int
    per_page: int
    pages: int


# Version checking schemas
class VersionCheckRequest(BaseModel):
    """Request for checking a single module version."""

    machine_name: str = Field(..., description="Machine name of the module")
    current_version: str = Field(..., description="Current version string")


class UpdateCheckResponse(BaseModel):
    """Response for update availability check."""

    machine_name: str = Field(..., description="Machine name of the module")
    current_version: str = Field(..., description="Current version string")
    latest_version: Optional[str] = Field(None, description="Latest available version")
    latest_security_version: Optional[str] = Field(
        None, description="Latest security version"
    )
    update_available: bool = Field(False, description="Whether an update is available")
    security_update_available: bool = Field(
        False, description="Whether a security update is available"
    )
    version_lag: Dict[str, int] = Field(_=dict, description="Version lag information")


class VersionCheckResponse(BaseModel):
    """Response for version comparison."""

    comparison: int = Field(..., description="Comparison result: -1, 0, or 1")
    version1: str = Field(..., description="First version string")
    version2: str = Field(..., description="Second version string")
    version1_parsed: Dict[str, Any] = Field(
        ..., description="Parsed components of version1"
    )
    version2_parsed: Dict[str, Any] = Field(
        ..., description="Parsed components of version2"
    )
