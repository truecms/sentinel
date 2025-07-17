from typing import List, Optional, Union
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps
from app.crud import crud_site, crud_site_module, crud_module, crud_module_version
from app.models.user import User
from app.models.site import Site
from app.schemas.site_module import (
    SiteModuleCreate,
    SiteModuleUpdate,
    SiteModuleResponse,
    SiteModuleListResponse,
    SiteModuleStatsResponse
)
from app.schemas.site import SiteOverview, SitesOverviewResponse
from app.schemas.module_version import ModuleVersionResponse
from app.schemas.drupal_sync import DrupalSiteSync, ModuleSyncResult
from app.api.v1.dependencies.rate_limit import check_rate_limit
from app.services.cache import ModuleCacheService
from app.services.update_detector import UpdateDetector
from app.tasks.sync_tasks import sync_site_modules_task
from app.core.config import settings
from app.core.permissions import require_resource_action_dependency
import json

router = APIRouter()


@router.get("/", response_model=List[schemas.SiteResponse])
async def read_sites(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Retrieve sites."""
    sites = await crud_site.get_sites(db, skip=skip, limit=limit)
    return sites


@router.post("/", response_model=schemas.SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    *,
    db: AsyncSession = Depends(deps.get_db),
    site_in: schemas.SiteCreate,
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Create new site."""
    site = await crud_site.get_site_by_url(db, url=site_in.url)
    if site:
        raise HTTPException(
            status_code=409,
            detail="The site with this URL already exists."
        )
    site = await crud_site.create_site(
        db=db,
        site=site_in,
        created_by=current_user.id
    )
    return site


@router.get("/overview", response_model=SitesOverviewResponse)
async def get_sites_overview(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search by site name"),
    sort_by: str = Query("name", description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    Get sites overview with security metrics and update tracking.
    
    Provides a comprehensive view of all sites with:
    - Security scores and status
    - Module counts and update requirements
    - Data freshness timestamps
    - Search and sorting capabilities
    """
    # Build filters
    filters = {}
    if search:
        filters['search'] = search
    
    # Get sites with overview data
    try:
        sites_data, total = await crud_site.get_sites_overview(
            db=db,
            user=current_user,
            skip=skip,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    # Convert to response format
    site_overviews = []
    for site in sites_data:
        # Calculate status based on security score and updates using configurable thresholds
        status = "healthy"
        if site.security_updates_count > 0:
            status = "critical"
        elif (site.security_score < settings.SECURITY_SCORE_CRITICAL_THRESHOLD or 
              site.non_security_updates_count > settings.NON_SECURITY_UPDATES_WARNING_THRESHOLD):
            status = "warning"
        
        overview = SiteOverview(
            id=site.id,
            name=site.name,
            url=site.url,
            security_score=site.security_score or 0,
            total_modules_count=site.total_modules_count or 0,
            security_updates_count=site.security_updates_count or 0,
            non_security_updates_count=site.non_security_updates_count or 0,
            last_data_push=site.last_data_push,
            last_drupal_org_check=site.last_drupal_org_check,
            status=status,
            organization_id=site.organization_id
        )
        site_overviews.append(overview)
    
    # Calculate pagination
    pages = ceil(total / limit) if limit > 0 else 1
    page = (skip // limit) + 1 if limit > 0 else 1
    
    pagination = {
        "page": page,
        "per_page": limit,
        "total": total,
        "total_pages": pages
    }
    
    # Build response filters
    response_filters = {
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order
    }
    
    return SitesOverviewResponse(
        sites=site_overviews,
        pagination=pagination,
        filters=response_filters
    )

@router.get("/{site_id}", response_model=schemas.SiteResponse)
async def read_site(
    site_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Get a specific site by id."""
    site = await crud_site.get_site(db, site_id=site_id)
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
    site = await crud_site.get_site(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    site = await crud_site.update_site(
        db=db,
        site_id=site_id,
        site=site_in,
        updated_by=current_user.id
    )
    return site

@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    *,
    db: AsyncSession = Depends(deps.get_db),
    site_id: int,
    current_user: schemas.UserResponse = Depends(deps.get_current_user)
):
    """Delete a site."""
    site = await crud_site.get_site(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    await crud_site.delete_site(
        db=db,
        site_id=site_id,
        updated_by=current_user.id
    )

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
    site = await crud_site.get_site(db, site_id)
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

@router.post("/{site_id}/modules")
async def sync_site_modules(
    site_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    payload: DrupalSiteSync,
    auth_subject: Union[User, Site] = Depends(require_resource_action_dependency("site", "sync")),
    request: Request
):
    """
    Sync module data from a Drupal site with rate limiting and performance optimizations.
    
    This endpoint supports both user authentication (JWT) and site authentication (API key):
    - **User Authentication**: JWT token via Authorization header
    - **Site Authentication**: API key via X-API-Key or X-Site-Token header
    
    This endpoint handles:
    - Rate limiting: 4 requests per hour per site
    - Caching: Module and version lookups are cached in Redis
    - Background processing: Large payloads (>500 modules) are processed asynchronously
    - Creating new modules if they don't exist
    - Creating new module versions if they don't exist
    - Updating site-module associations
    - Tracking enabled/disabled status
    
    Required permissions:
    - site:sync permission (checked by RBAC system)
    
    Returns:
    - 200: Sync completed successfully (for small payloads)
    - 202: Sync accepted for background processing (for large payloads)
    - 429: Rate limit exceeded
    """
    # Check if site exists
    site = await crud_site.get_site(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Additional authorization checks based on auth subject type
    if isinstance(auth_subject, User):
        # User authentication - check organization access
        if not auth_subject.is_superuser and auth_subject.organization_id != site.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions - organization access denied"
            )
        current_user_id = auth_subject.id
    elif isinstance(auth_subject, Site):
        # Site authentication - must match the site in the URL
        if auth_subject.id != site_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Site authentication mismatch - cannot sync to different site"
            )
        # For site authentication, we'll use the site's created_by as the user ID
        current_user_id = site.created_by
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication type"
        )
    
    # Check rate limit
    await check_rate_limit(site_id, request)
    
    # Validate site URL matches
    if site.url != payload.site.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Site URL mismatch. Expected {site.url}, got {payload.site.url}"
        )
    
    # Check if we should process in background (>500 modules)
    if len(payload.modules) > 500:
        # Serialize payload for background task
        payload_json = json.dumps({
            "site": payload.site.dict(),
            "drupal_info": payload.drupal_info.dict(),
            "modules": [m.dict() for m in payload.modules]
        })
        
        # Queue background task
        task = sync_site_modules_task.delay(
            site_id=site_id,
            payload_json=payload_json,
            user_id=current_user_id
        )
        
        # Return 202 Accepted with task ID
        return {
            "status": "accepted",
            "task_id": task.id,
            "message": f"Sync of {len(payload.modules)} modules queued for processing",
            "status_url": f"/api/v1/tasks/{task.id}/status"
        }
    
    # Process synchronously for smaller payloads
    modules_processed = 0
    modules_created = 0
    modules_updated = 0
    modules_unchanged = 0
    errors = []
    
    for module_info in payload.modules:
        try:
            modules_processed += 1
            
            # Check if module exists (with caching)
            module = await ModuleCacheService.get_module_by_machine_name(
                db, module_info.machine_name
            )
            if not module:
                # Create new module
                module_create = schemas.ModuleCreate(
                    machine_name=module_info.machine_name,
                    display_name=module_info.display_name,
                    module_type=module_info.module_type,
                    description=module_info.description
                )
                module = await crud_module.create_module(db, module_create, current_user_id)
                modules_created += 1
                
                # Invalidate cache
                await ModuleCacheService.invalidate_module_cache(module_info.machine_name)
            
            # Check if version exists (with caching)
            version = await ModuleCacheService.get_version_by_module_and_string(
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
                    db, version_create, current_user_id
                )
                
                # Invalidate cache
                await ModuleCacheService.invalidate_version_cache(
                    module.id, module_info.version
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
                        db, site_id, module.id, update_data, current_user_id
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
                site_module = await crud_site_module.create_site_module(
                    db, site_module_create, current_user_id
                )
                modules_created += 1
            
            # Check for available updates using version comparison
            if site_module and module_info.enabled:
                try:
                    detector = UpdateDetector()
                    update_info = await detector.check_module_updates(
                        db, module.id, module_info.version
                    )
                    
                    # Update site module with update availability
                    if (update_info.update_available or 
                        update_info.security_update_available):
                        await detector.update_site_module_flags(
                            db, site_module, update_info
                        )
                except Exception as e:
                    # Log update check error but don't fail the sync
                    errors.append({
                        "module": module_info.machine_name,
                        "error": f"Update check failed: {str(e)}",
                        "type": "update_check"
                    })
                
        except Exception as e:
            errors.append({
                "module": module_info.machine_name,
                "error": str(e)
            })
    
    # Handle full sync - detect removed modules
    if payload.full_sync:
        # Get all currently active modules for this site
        current_modules, _ = await crud_site_module.get_site_modules(
            db=db,
            site_id=site_id,
            skip=0,
            limit=10000,  # Get all modules
            enabled_only=False
        )
        
        # Create set of module IDs from payload
        payload_module_names = {m.machine_name for m in payload.modules}
        
        # Find modules that are no longer in the payload
        for site_module in current_modules:
            if site_module.module.machine_name not in payload_module_names:
                # Mark as removed (soft delete)
                await crud_site_module.delete_site_module(
                    db, site_id, site_module.module_id, current_user_id
                )
    
    # Update site's last sync time
    site_update = schemas.SiteUpdate(
        name=payload.site.name  # Update site name if changed
    )
    await crud_site.update_site(db, site_id, site_update, current_user_id)
    
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
    site = await crud_site.get_site(db, site_id)
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
    site = await crud_site.get_site(db, site_id)
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
    site = await crud_site.get_site(db, site_id)
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


