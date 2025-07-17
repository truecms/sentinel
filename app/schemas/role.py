"""Pydantic schemas for role management."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """Base permission schema."""
    name: str
    resource: str
    action: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    """Schema for creating permissions."""
    pass


class PermissionUpdate(BaseModel):
    """Schema for updating permissions."""
    description: Optional[str] = None


class PermissionResponse(PermissionBase):
    """Schema for permission responses."""
    id: int

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """Base role schema."""
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating roles."""
    permission_ids: Optional[List[int]] = []


class RoleUpdate(BaseModel):
    """Schema for updating roles."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    """Schema for role responses."""
    id: int
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class UserRoleBase(BaseModel):
    """Base user role assignment schema."""
    user_id: int
    role_id: int
    organization_id: Optional[int] = None


class UserRoleCreate(UserRoleBase):
    """Schema for creating user role assignments."""
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class UserRoleUpdate(BaseModel):
    """Schema for updating user role assignments."""
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class UserRoleResponse(UserRoleBase):
    """Schema for user role assignment responses."""
    id: int
    valid_from: datetime
    valid_until: Optional[datetime] = None
    assigned_by_id: Optional[int] = None
    assigned_at: datetime
    
    # Nested objects (simplified to avoid circular imports)
    role: Optional[dict] = None
    organization: Optional[dict] = None
    assigned_by: Optional[dict] = None

    class Config:
        from_attributes = True


class ApiKeyBase(BaseModel):
    """Base API key schema."""
    name: Optional[str] = None
    expires_at: Optional[datetime] = None


class ApiKeyCreate(ApiKeyBase):
    """Schema for creating API keys."""
    pass


class ApiKeyUpdate(BaseModel):
    """Schema for updating API keys."""
    name: Optional[str] = None
    is_active: Optional[bool] = None


class ApiKeyResponse(ApiKeyBase):
    """Schema for API key responses."""
    id: int
    user_id: Optional[int] = None
    site_id: Optional[int] = None
    last_used: Optional[datetime] = None
    created_at: datetime
    is_active: bool
    
    # Never expose the actual key or hash
    key_preview: Optional[str] = None  # First 8 characters for identification

    class Config:
        from_attributes = True


class ApiKeyCreateResponse(ApiKeyResponse):
    """Schema for API key creation response (includes the actual key)."""
    api_key: str  # Only shown once during creation

    class Config:
        from_attributes = True