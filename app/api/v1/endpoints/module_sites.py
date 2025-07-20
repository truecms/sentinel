from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import crud_module, crud_site_module
from app.models.user import User
from app.schemas.module_version import ModuleVersionResponse
from app.schemas.site import SiteResponse
from app.schemas.site_module import SiteModuleResponse

router = APIRouter()


@router.get("/{module_id}/sites", response_model=List[SiteResponse])
async def get_module_sites(
    module_id: int,
    db: AsyncSession = Depends(deps.get_db),
    version_id: Optional[int] = Query(None, description="Filter by specific version"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of records to return"
    ),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all sites using a specific module.

    - **version_id**: Filter by specific version
    """
    # Check if module exists
    module = await crud_module.get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    site_modules, total = await crud_site_module.get_module_sites(
        db=db, module_id=module_id, version_id=version_id, skip=skip, limit=limit
    )

    # Filter sites based on user permissions (non-superusers see only their org's sites)
    accessible_sites = []
    for site_module in site_modules:
        site = site_module.site
        if (
            current_user.is_superuser
            or current_user.organization_id == site.organization_id
        ):
            accessible_sites.append(site)

    return [
        SiteResponse(
            id=site.id,
            name=site.name,
            url=site.url,
            description=site.description,
            organization_id=site.organization_id,
            is_active=site.is_active,
            is_deleted=site.is_deleted,
            created_at=site.created_at,
            updated_at=site.updated_at,
            created_by=site.created_by,
            updated_by=site.updated_by,
        )
        for site in accessible_sites
    ]


@router.get("/{module_id}/site-modules", response_model=List[SiteModuleResponse])
async def get_module_site_modules(
    module_id: int,
    db: AsyncSession = Depends(deps.get_db),
    version_id: Optional[int] = Query(None, description="Filter by specific version"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of records to return"
    ),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all site-module relationships for a specific module.

    - **version_id**: Filter by specific version
    """
    # Check if module exists
    module = await crud_module.get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    site_modules, total = await crud_site_module.get_module_sites(
        db=db, module_id=module_id, version_id=version_id, skip=skip, limit=limit
    )

    # Filter based on user permissions and convert to response format
    accessible_site_modules = []
    for site_module in site_modules:
        site = site_module.site
        if (
            current_user.is_superuser
            or current_user.organization_id == site.organization_id
        ):
            # Create current version response
            current_version_response = ModuleVersionResponse(
                id=site_module.current_version.id,
                module_id=site_module.current_version.module_id,
                version_string=site_module.current_version.version_string,
                release_date=site_module.current_version.release_date,
                is_security_update=site_module.current_version.is_security_update,
                release_notes=site_module.current_version.release_notes,
                drupal_core_compatibility=(
                    site_module.current_version.drupal_core_compatibility.split(",") 
                    if site_module.current_version.drupal_core_compatibility else []
                ),
                is_active=site_module.current_version.is_active,
                is_deleted=site_module.current_version.is_deleted,
                created_at=site_module.current_version.created_at,
                updated_at=site_module.current_version.updated_at,
                created_by=site_module.current_version.created_by,
                updated_by=site_module.current_version.updated_by,
                module_name=site_module.module.display_name,
                module_machine_name=site_module.module.machine_name,
            )

            # Create latest version response if exists
            latest_version_response = None
            if site_module.latest_version:
                latest_version_response = ModuleVersionResponse(
                    id=site_module.latest_version.id,
                    module_id=site_module.latest_version.module_id,
                    version_string=site_module.latest_version.version_string,
                    release_date=site_module.latest_version.release_date,
                    is_security_update=site_module.latest_version.is_security_update,
                    release_notes=site_module.latest_version.release_notes,
                    drupal_core_compatibility=(
                        site_module.latest_version.drupal_core_compatibility.split(",") 
                        if site_module.latest_version.drupal_core_compatibility else []
                    ),
                    is_active=site_module.latest_version.is_active,
                    is_deleted=site_module.latest_version.is_deleted,
                    created_at=site_module.latest_version.created_at,
                    updated_at=site_module.latest_version.updated_at,
                    created_by=site_module.latest_version.created_by,
                    updated_by=site_module.latest_version.updated_by,
                    module_name=site_module.module.display_name,
                    module_machine_name=site_module.module.machine_name,
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
                site_name=site.name,
                site_url=site.url,
            )
            accessible_site_modules.append(module_response)

    return accessible_site_modules
