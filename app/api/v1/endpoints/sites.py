from typing import List, Optional
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps
from app.crud import crud_site_module, crud_module, crud_module_version
from app.models.user import User
from app.schemas.site_module import (
    SiteModuleCreate,
    SiteModuleUpdate,
    SiteModuleResponse,
    SiteModuleListResponse,
    SiteModuleStatsResponse
)
from app.schemas.module_version import ModuleVersionResponse
from app.schemas.drupal_sync import DrupalSiteSync, ModuleSyncResult

router = APIRouter()

@router.get("/", response_model=List[schemas.SiteResponse])
async def read_sites(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Retrieve sites."""
    sites = await crud.get_sites(db, skip=skip, limit=limit)
    return sites

@router.post("/", response_model=schemas.SiteResponse)
async def create_site(
    *,
    db: AsyncSession = Depends(deps.get_db),
    site_in: schemas.SiteCreate,
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Create new site."""
    site = await crud.get_site_by_url(db, url=site_in.url)
    if site:
        raise HTTPException(
            status_code=400,
            detail="The site with this URL already exists."
        )
    site = await crud.create_site(
        db=db,
        site=site_in,
        created_by=current_user.id
    )
    return site

@router.get("/{site_id}", response_model=schemas.SiteResponse)
async def read_site(
    site_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Get a specific site by id."""
    site = await crud.get_site(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.put("/{site_id}", response_model=schemas.SiteResponse)
async def update_site(
    *,
    db: AsyncSession = Depends(deps.get_db),
    site_id: int,
    site_in: schemas.SiteUpdate,
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Update a site."""
    site = await crud.get_site(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    site = await crud.update_site(
        db=db,
        site_id=site_id,
        site=site_in,
        updated_by=current_user.id
    )
    return site

@router.delete("/{site_id}", response_model=schemas.SiteResponse)
async def delete_site(
    *,
    db: AsyncSession = Depends(deps.get_db),
    site_id: int,
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Delete a site."""
    site = await crud.get_site(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    site = await crud.delete_site(
        db=db,
        site_id=site_id,
        updated_by=current_user.id
    )
    return site

# Site Module Endpoints

@router.get("/{site_id}/modules", response_model=SiteModuleListResponse)
async def get_site_modules(
    site_id: int,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    updates_only: bool = Query(False, description="Show only modules with available updates"),
    security_only: bool = Query(False, description="Show only modules with security updates"),
    enabled_only: bool = Query(True, description="Show only enabled modules"),
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    Get all modules installed on a specific site.
    
    - **updates_only**: Show only modules with available updates
    - **security_only**: Show only modules with security updates  
    - **enabled_only**: Show only enabled modules
    """
    # Check if site exists and user has access
    site = await crud.get_site(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Check organization access (non-superusers can only access their org's sites)
    if not current_user.is_superuser and current_user.organization_id != site.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    site_modules, total = await crud_site_module.get_site_modules(
        db=db,
        site_id=site_id,
        skip=skip,
        limit=limit,
        updates_only=updates_only,
        security_only=security_only,
        enabled_only=enabled_only
    )
    
    # Convert to response format with nested data
    module_responses = []
    for site_module in site_modules:
        # Create current version response
        current_version_response = ModuleVersionResponse(
            id=site_module.current_version.id,
            module_id=site_module.current_version.module_id,
            version_string=site_module.current_version.version_string,
            semantic_version=site_module.current_version.semantic_version,
            release_date=site_module.current_version.release_date,
            is_security_update=site_module.current_version.is_security_update,
            release_notes_link=site_module.current_version.release_notes_link,
            drupal_core_compatibility=site_module.current_version.drupal_core_compatibility,
            is_active=site_module.current_version.is_active,
            is_deleted=site_module.current_version.is_deleted,
            created_at=site_module.current_version.created_at,
            updated_at=site_module.current_version.updated_at,
            created_by=site_module.current_version.created_by,
            updated_by=site_module.current_version.updated_by,
            module_name=site_module.module.display_name,
            module_machine_name=site_module.module.machine_name
        )
        
        # Create latest version response if exists
        latest_version_response = None
        if site_module.latest_version:
            latest_version_response = ModuleVersionResponse(
                id=site_module.latest_version.id,
                module_id=site_module.latest_version.module_id,
                version_string=site_module.latest_version.version_string,
                semantic_version=site_module.latest_version.semantic_version,
                release_date=site_module.latest_version.release_date,
                is_security_update=site_module.latest_version.is_security_update,
                release_notes_link=site_module.latest_version.release_notes_link,
                drupal_core_compatibility=site_module.latest_version.drupal_core_compatibility,
                is_active=site_module.latest_version.is_active,
                is_deleted=site_module.latest_version.is_deleted,
                created_at=site_module.latest_version.created_at,
                updated_at=site_module.latest_version.updated_at,
                created_by=site_module.latest_version.created_by,
                updated_by=site_module.latest_version.updated_by,
                module_name=site_module.module.display_name,
                module_machine_name=site_module.module.machine_name
            )
        
        module_response = SiteModuleResponse(
            id=site_module.id,
            site_id=site_module.site_id,
            module_id=site_module.module_id,
            current_version_id=site_module.current_version_id,
            enabled=site_module.enabled,
            update_available=site_module.update_available,
            security_update_available=site_module.security_update_available,
            latest_version_id=site_module.latest_version_id,
            first_seen=site_module.first_seen,
            last_seen=site_module.last_seen,
            last_updated=site_module.last_updated,
            is_active=site_module.is_active,
            is_deleted=site_module.is_deleted,
            created_at=site_module.created_at,
            updated_at=site_module.updated_at,
            created_by=site_module.created_by,
            updated_by=site_module.updated_by,
            module=site_module.module,
            current_version=current_version_response,
            latest_version=latest_version_response,
            site_name=site_module.site.name,
            site_url=site_module.site.url
        )
        module_responses.append(module_response)
    
    pages = ceil(total / limit) if limit > 0 else 1
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return SiteModuleListResponse(
        data=module_responses,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )

@router.post("/{site_id}/modules", response_model=ModuleSyncResult)
async def sync_site_modules(
    site_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    payload: DrupalSiteSync,
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    Sync module data from a Drupal site.
    
    Accepts the complete module payload from a Drupal site and updates
    the module information accordingly. This endpoint handles:
    - Creating new modules if they don't exist
    - Creating new module versions if they don't exist
    - Updating site-module associations
    - Tracking enabled/disabled status
    """
    # Check if site exists and user has access
    site = await crud.get_site(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Check organization access
    if not current_user.is_superuser and current_user.organization_id != site.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate site URL matches
    if site.url != payload.site.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Site URL mismatch. Expected {site.url}, got {payload.site.url}"
        )
    
    # Process modules
    modules_processed = 0
    modules_created = 0
    modules_updated = 0
    modules_unchanged = 0
    errors = []
    
    for module_info in payload.modules:
        try:
            modules_processed += 1
            
            # Check if module exists
            module = await crud_module.get_module_by_machine_name(db, module_info.machine_name)
            if not module:
                # Create new module
                module_create = schemas.ModuleCreate(
                    machine_name=module_info.machine_name,
                    display_name=module_info.display_name,
                    module_type=module_info.module_type,
                    description=module_info.description
                )
                module = await crud_module.create_module(db, module_create, current_user.id)
                modules_created += 1
            
            # Check if version exists
            version = await crud_module_version.get_version_by_module_and_string(
                db, module.id, module_info.version
            )
            if not version:
                # Create new version
                version_create = schemas.ModuleVersionCreate(
                    module_id=module.id,
                    version_string=module_info.version,
                    drupal_core_compatibility=[payload.drupal_info.core_version]
                )
                version = await crud_module_version.create_module_version(
                    db, version_create, current_user.id
                )
            
            # Check if site-module association exists
            site_module = await crud_site_module.get_site_module_by_site_and_module(
                db, site_id, module.id
            )
            if site_module:
                # Update existing association
                if (site_module.current_version_id != version.id or 
                    site_module.enabled != module_info.enabled):
                    update_data = SiteModuleUpdate(
                        current_version_id=version.id,
                        enabled=module_info.enabled
                    )
                    await crud_site_module.update_site_module(
                        db, site_id, module.id, update_data, current_user.id
                    )
                    modules_updated += 1
                else:
                    modules_unchanged += 1
            else:
                # Create new association
                site_module_create = SiteModuleCreate(
                    site_id=site_id,
                    module_id=module.id,
                    current_version_id=version.id,
                    enabled=module_info.enabled
                )
                await crud_site_module.create_site_module(
                    db, site_module_create, current_user.id
                )
                modules_created += 1
                
        except Exception as e:
            errors.append({
                "module": module_info.machine_name,
                "error": str(e)
            })
    
    # Update site's last sync time
    site_update = schemas.SiteUpdate(
        name=payload.site.name  # Update site name if changed
    )
    await crud.update_site(db, site_id, site_update, current_user.id)
    
    return ModuleSyncResult(
        site_id=site_id,
        modules_processed=modules_processed,
        modules_created=modules_created,
        modules_updated=modules_updated,
        modules_unchanged=modules_unchanged,
        errors=errors,
        message=f"Successfully synced {modules_processed} modules"
    )

@router.put("/{site_id}/modules/{module_id}", response_model=SiteModuleResponse)
async def update_site_module(
    site_id: int,
    module_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    update: SiteModuleUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    Update a site-module relationship (e.g., version, enabled status).
    """
    # Check if site exists and user has access
    site = await crud.get_site(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Check organization access
    if not current_user.is_superuser and current_user.organization_id != site.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # If updating version, validate it exists and belongs to the module
    if update.current_version_id:
        version = await crud_module_version.get_module_version(db, update.current_version_id)
        if not version or version.module_id != module_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid version for this module"
            )
    
    db_site_module = await crud_site_module.update_site_module(
        db, site_id, module_id, update, current_user.id
    )
    if not db_site_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site-module association not found"
        )
    
    # Create current version response
    current_version_response = ModuleVersionResponse(
        id=db_site_module.current_version.id,
        module_id=db_site_module.current_version.module_id,
        version_string=db_site_module.current_version.version_string,
        semantic_version=db_site_module.current_version.semantic_version,
        release_date=db_site_module.current_version.release_date,
        is_security_update=db_site_module.current_version.is_security_update,
        release_notes_link=db_site_module.current_version.release_notes_link,
        drupal_core_compatibility=db_site_module.current_version.drupal_core_compatibility,
        is_active=db_site_module.current_version.is_active,
        is_deleted=db_site_module.current_version.is_deleted,
        created_at=db_site_module.current_version.created_at,
        updated_at=db_site_module.current_version.updated_at,
        created_by=db_site_module.current_version.created_by,
        updated_by=db_site_module.current_version.updated_by,
        module_name=db_site_module.module.display_name,
        module_machine_name=db_site_module.module.machine_name
    )
    
    # Create latest version response if exists
    latest_version_response = None
    if db_site_module.latest_version:
        latest_version_response = ModuleVersionResponse(
            id=db_site_module.latest_version.id,
            module_id=db_site_module.latest_version.module_id,
            version_string=db_site_module.latest_version.version_string,
            semantic_version=db_site_module.latest_version.semantic_version,
            release_date=db_site_module.latest_version.release_date,
            is_security_update=db_site_module.latest_version.is_security_update,
            release_notes_link=db_site_module.latest_version.release_notes_link,
            drupal_core_compatibility=db_site_module.latest_version.drupal_core_compatibility,
            is_active=db_site_module.latest_version.is_active,
            is_deleted=db_site_module.latest_version.is_deleted,
            created_at=db_site_module.latest_version.created_at,
            updated_at=db_site_module.latest_version.updated_at,
            created_by=db_site_module.latest_version.created_by,
            updated_by=db_site_module.latest_version.updated_by,
            module_name=db_site_module.module.display_name,
            module_machine_name=db_site_module.module.machine_name
        )
    
    return SiteModuleResponse(
        id=db_site_module.id,
        site_id=db_site_module.site_id,
        module_id=db_site_module.module_id,
        current_version_id=db_site_module.current_version_id,
        enabled=db_site_module.enabled,
        update_available=db_site_module.update_available,
        security_update_available=db_site_module.security_update_available,
        latest_version_id=db_site_module.latest_version_id,
        first_seen=db_site_module.first_seen,
        last_seen=db_site_module.last_seen,
        last_updated=db_site_module.last_updated,
        is_active=db_site_module.is_active,
        is_deleted=db_site_module.is_deleted,
        created_at=db_site_module.created_at,
        updated_at=db_site_module.updated_at,
        created_by=db_site_module.created_by,
        updated_by=db_site_module.updated_by,
        module=db_site_module.module,
        current_version=current_version_response,
        latest_version=latest_version_response,
        site_name=db_site_module.site.name,
        site_url=db_site_module.site.url
    )

@router.delete("/{site_id}/modules/{module_id}", status_code=204)
async def remove_site_module(
    site_id: int,
    module_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> None:
    """
    Remove a module from a site.
    """
    # Check if site exists and user has access
    site = await crud.get_site(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Check organization access
    if not current_user.is_superuser and current_user.organization_id != site.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_site_module = await crud_site_module.delete_site_module(
        db, site_id, module_id, current_user.id
    )
    if not db_site_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site-module association not found"
        )

@router.get("/{site_id}/modules/stats", response_model=SiteModuleStatsResponse)
async def get_site_module_stats(
    site_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    Get statistics for modules on a site.
    """
    # Check if site exists and user has access
    site = await crud.get_site(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Check organization access
    if not current_user.is_superuser and current_user.organization_id != site.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    stats = await crud_site_module.get_site_module_stats(db, site_id)
    
    return SiteModuleStatsResponse(**stats)

