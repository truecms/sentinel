from typing import Any, List, Optional
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import crud_module, crud_site_module
from app.models.user import User
from app.schemas.site import SiteResponse
from app.schemas.site_module import SiteModuleResponse

router = APIRouter()


@router.get("/modules/{module_id}/sites", response_model=List[SiteResponse])
async def get_module_sites(
    module_id: int,
    db: AsyncSession = Depends(deps.get_db),
    version_id: Optional[int] = Query(None, description="Filter by specific version"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get all sites using a specific module.
    
    - **version_id**: Filter by specific version
    """
    # Check if module exists
    module = await crud_module.get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    site_modules, total = await crud_site_module.get_module_sites(
        db=db,
        module_id=module_id,
        version_id=version_id,
        skip=skip,
        limit=limit
    )
    
    # Filter sites based on user permissions (non-superusers see only their org's sites)
    accessible_sites = []
    for site_module in site_modules:
        site = site_module.site
        if current_user.is_superuser or current_user.organization_id == site.organization_id:
            accessible_sites.append(site)
    
    return [SiteResponse(**site.__dict__) for site in accessible_sites]


@router.get("/modules/{module_id}/site-modules", response_model=List[SiteModuleResponse])
async def get_module_site_modules(
    module_id: int,
    db: AsyncSession = Depends(deps.get_db),
    version_id: Optional[int] = Query(None, description="Filter by specific version"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get all site-module relationships for a specific module.
    
    - **version_id**: Filter by specific version
    """
    # Check if module exists
    module = await crud_module.get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    site_modules, total = await crud_site_module.get_module_sites(
        db=db,
        module_id=module_id,
        version_id=version_id,
        skip=skip,
        limit=limit
    )
    
    # Filter based on user permissions and convert to response format
    accessible_site_modules = []
    for site_module in site_modules:
        site = site_module.site
        if current_user.is_superuser or current_user.organization_id == site.organization_id:
            module_response = SiteModuleResponse(
                **site_module.__dict__,
                module=site_module.module.__dict__,
                current_version=site_module.current_version.__dict__,
                latest_version=site_module.latest_version.__dict__ if site_module.latest_version else None,
                site_name=site.name,
                site_url=site.url
            )
            accessible_site_modules.append(module_response)
    
    return accessible_site_modules