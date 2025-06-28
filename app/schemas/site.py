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
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_deleted: bool
    created_by: int
    updated_by: int

    class Config:
        from_attributes = True

class SiteResponse(SiteInDBBase):
    organizations: List[OrganizationResponse] = []

class SiteInDB(SiteInDBBase):
    pass
