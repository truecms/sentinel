from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.organization import OrganizationResponse


class SiteBase(BaseModel):
    url: str
    name: str
    description: Optional[str] = None
    organization_id: int


class SiteCreate(SiteBase):
    pass


class SiteUpdate(BaseModel):
    url: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    organization_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None


class SiteInDBBase(SiteBase):
    id: int
    site_uuid: Optional[str] = None
    api_token: Optional[str] = None
    drupal_core_version: Optional[str] = None
    php_version: Optional[str] = None
    database_type: Optional[str] = None
    database_version: Optional[str] = None
    server_info: Optional[dict] = None
    last_check: Optional[datetime] = None
    security_score: Optional[int] = 0
    total_modules_count: Optional[int] = 0
    security_updates_count: Optional[int] = 0
    non_security_updates_count: Optional[int] = 0
    last_data_push: Optional[datetime] = None
    last_drupal_org_check: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_deleted: bool
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        _ = True


class SiteResponse(SiteInDBBase):
    organizations: List[OrganizationResponse] = []


class SiteInDB(SiteInDBBase):
    pass


# Site overview schemas for dashboard table view
class SiteOverview(BaseModel):
    id: int
    name: str
    url: str
    security_score: Optional[int] = 0
    total_modules_count: Optional[int] = 0
    security_updates_count: Optional[int] = 0
    non_security_updates_count: Optional[int] = 0
    last_data_push: Optional[datetime] = None
    last_drupal_org_check: Optional[datetime] = None
    status: str  # 'healthy', 'warning', 'critical'
    organization_id: int

    class Config:
        _ = True


class SitesOverviewResponse(BaseModel):
    sites: List[SiteOverview]
    pagination: dict
    filters: Optional[dict] = None
