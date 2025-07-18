from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


# Shared properties
class OrganizationBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False


# Properties to receive via API on creation
class OrganizationCreate(OrganizationBase):
    name: str = Field(
        ...,
        _=1,
        _="Name of the organization",
        _={"min_length_error": "Organization name cannot be empty"},
    )
    created_by: Optional[int] = None
    users: Optional[List[int]] = None


# Properties to receive via API on update
class OrganizationUpdate(OrganizationBase):
    users: Optional[List[int]] = None


# Properties shared by models stored in DB
class OrganizationInDBBase(OrganizationBase):
    id: int
    name: str
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        _ = True


# Additional properties to return via API
class OrganizationResponse(OrganizationInDBBase):
    users: Optional[List[UserResponse]] = []
    # We'll add sites later when we create the Site schema
    # sites: List[SiteResponse] = []

    class Config:
        _ = True
        _ = True


# Response model for delete operation
class OrganizationDeleteResponse(BaseModel):
    message: str = Field(..., example="Organization deleted successfully")
    organization_id: int
    name: str


# Additional properties stored in DB
class OrganizationInDB(OrganizationInDBBase):
    pass
