from typing import Any, List, Optional
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import crud_module, crud_module_version, crud_site_module
from app.models.user import User
from app.schemas.module import (
    ModuleCreate, 
    ModuleUpdate, 
    ModuleResponse, 
    ModuleListResponse
)

router = APIRouter()


@router.get("/", response_model=ModuleListResponse)
async def get_modules(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    module_type: Optional[str] = Query(None, regex="^(contrib|custom|core)$", description="Filter by module type"),
    has_security_update: Optional[bool] = Query(None, description="Filter modules with security updates"),
    sort_by: str = Query("display_name", regex="^(display_name|machine_name|created_at|updated_at)$", description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retrieve modules with filtering and pagination.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return  
    - **search**: Search term for module name/description
    - **module_type**: Filter by module type (contrib|custom|core)
    - **has_security_update**: Filter modules with security updates
    - **sort_by**: Field to sort by
    - **sort_order**: Sort direction (asc|desc)
    """
    modules, total = await crud_module.get_modules(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        module_type=module_type,
        has_security_update=has_security_update,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Calculate additional response fields for each module
    module_responses = []
    for module in modules:
        # Get versions count
        versions_result = await crud_module_version.get_module_versions(db, module.id, limit=1000)
        versions_count = len(versions_result[0])
        
        # Get sites count
        sites_result = await crud_site_module.get_module_sites(db, module.id, limit=1000)
        sites_count = len(sites_result[0])
        
        # Get latest version
        latest_version = await crud_module_version.get_latest_version(db, module.id)
        latest_version_string = latest_version.version_string if latest_version else None
        
        # Check for security updates
        has_security = await crud_module_version.get_latest_security_version(db, module.id) is not None
        
        module_response = ModuleResponse(
            id=module.id,
            machine_name=module.machine_name,
            display_name=module.display_name,
            drupal_org_link=module.drupal_org_link,
            module_type=module.module_type,
            description=module.description,
            is_active=module.is_active,
            is_deleted=module.is_deleted,
            created_at=module.created_at,
            updated_at=module.updated_at,
            created_by=module.created_by,
            updated_by=module.updated_by,
            versions_count=versions_count,
            sites_count=sites_count,
            latest_version=latest_version_string,
            has_security_update=has_security
        )
        module_responses.append(module_response)
    
    pages = ceil(total / limit) if limit > 0 else 1
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return ModuleListResponse(
        data=module_responses,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


# Note: Module creation is handled automatically via the Drupal site sync endpoint
# POST /api/v1/sites/{site_id}/modules
# There is no use case for manually creating modules through this API


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: int,
    include_versions: bool = Query(True, description="Include version history"),
    include_sites: bool = Query(False, description="Include sites using this module"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get detailed information about a specific module.
    
    - **include_versions**: Include version history
    - **include_sites**: Include sites using this module
    """
    module = await crud_module.get_module_with_details(
        db, module_id, include_versions, include_sites
    )
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Calculate additional fields
    versions_list, versions_count = await crud_module_version.get_module_versions(db, module.id, limit=1000)
    
    sites_list, sites_count = await crud_site_module.get_module_sites(db, module.id, limit=1000)
    
    latest_version = await crud_module_version.get_latest_version(db, module.id)
    latest_version_string = latest_version.version_string if latest_version else None
    
    has_security = await crud_module_version.get_latest_security_version(db, module.id) is not None
    
    return ModuleResponse(
        id=module.id,
        machine_name=module.machine_name,
        display_name=module.display_name,
        drupal_org_link=module.drupal_org_link,
        module_type=module.module_type,
        description=module.description,
        is_active=module.is_active,
        is_deleted=module.is_deleted,
        created_at=module.created_at,
        updated_at=module.updated_at,
        created_by=module.created_by,
        updated_by=module.updated_by,
        versions_count=versions_count,
        sites_count=sites_count,
        latest_version=latest_version_string,
        has_security_update=has_security
    )


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    *,
    db: AsyncSession = Depends(deps.get_db),
    module_id: int,
    module_update: ModuleUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Update module information (superuser only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    module = await crud_module.update_module(db, module_id, module_update, current_user.id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Calculate additional fields
    versions_list, versions_count = await crud_module_version.get_module_versions(db, module.id, limit=1000)
    
    sites_list, sites_count = await crud_site_module.get_module_sites(db, module.id, limit=1000)
    
    latest_version = await crud_module_version.get_latest_version(db, module.id)
    latest_version_string = latest_version.version_string if latest_version else None
    
    has_security = await crud_module_version.get_latest_security_version(db, module.id) is not None
    
    return ModuleResponse(
        id=module.id,
        machine_name=module.machine_name,
        display_name=module.display_name,
        drupal_org_link=module.drupal_org_link,
        module_type=module.module_type,
        description=module.description,
        is_active=module.is_active,
        is_deleted=module.is_deleted,
        created_at=module.created_at,
        updated_at=module.updated_at,
        created_by=module.created_by,
        updated_by=module.updated_by,
        versions_count=versions_count,
        sites_count=sites_count,
        latest_version=latest_version_string,
        has_security_update=has_security
    )


@router.delete("/{module_id}", response_model=ModuleResponse)
async def delete_module(
    *,
    db: AsyncSession = Depends(deps.get_db),
    module_id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Soft delete a module (superuser only).
    
    This will mark the module as inactive but preserve historical data.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    module = await crud_module.delete_module(db, module_id, current_user.id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    return ModuleResponse(
        id=module.id,
        machine_name=module.machine_name,
        display_name=module.display_name,
        drupal_org_link=module.drupal_org_link,
        module_type=module.module_type,
        description=module.description,
        is_active=module.is_active,
        is_deleted=module.is_deleted,
        created_at=module.created_at,
        updated_at=module.updated_at,
        created_by=module.created_by,
        updated_by=module.updated_by,
        versions_count=0,
        sites_count=0,
        latest_version=None,
        has_security_update=False
    )


# Note: Bulk module operations are handled via the Drupal site sync endpoint
# POST /api/v1/sites/{site_id}/modules
# The bulk endpoint has been removed as per requirements