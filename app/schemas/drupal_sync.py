from typing import List, Optional
from pydantic import BaseModel, Field


class DrupalModuleInfo(BaseModel):
    """Module information from Drupal site."""
    machine_name: str = Field(..., description="Module machine name")
    display_name: str = Field(..., description="Human-readable module name")
    module_type: str = Field(..., pattern="^(contrib|custom|core)$", description="Type of module")
    enabled: bool = Field(..., description="Whether the module is enabled")
    version: str = Field(..., description="Module version string")
    description: Optional[str] = Field(None, description="Module description")


class DrupalInfo(BaseModel):
    """Drupal core and environment information."""
    core_version: str = Field(..., description="Drupal core version")
    php_version: str = Field(..., description="PHP version")
    ip_address: str = Field(..., description="Server IP address")


class DrupalSiteInfo(BaseModel):
    """Site information from Drupal."""
    url: str = Field(..., description="Site URL")
    name: str = Field(..., description="Site name")
    token: str = Field(..., description="Site authentication token")


class DrupalSiteSync(BaseModel):
    """Complete payload from Drupal site for module sync."""
    site: DrupalSiteInfo = Field(..., description="Site information")
    drupal_info: DrupalInfo = Field(..., description="Drupal environment information")
    modules: List[DrupalModuleInfo] = Field(..., description="List of modules")
    full_sync: bool = Field(default=False, description="When true, modules not in payload are marked as removed")


class ModuleSyncResult(BaseModel):
    """Result of module sync operation."""
    site_id: int
    modules_processed: int
    modules_created: int
    modules_updated: int
    modules_unchanged: int
    errors: List[dict] = Field(default_factory=list)
    message: str