from math import ceil
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import crud_module, crud_module_version
from app.models.user import User
from app.schemas.module_version import (
    ModuleVersionListResponse,
    ModuleVersionResponse,
)

router = APIRouter()


@router.get("/{module_id}/versions", response_model=ModuleVersionListResponse)
async def get_module_versions(
    module_id: int,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of records to return"
    ),
    only_security: bool = Query(False, description="Show only security updates"),
    drupal_core: Optional[str] = Query(
        None, description="Filter by Drupal core version"
    ),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get version history for a specific module.

    - **only_security**: Show only security updates
    - **drupal_core**: Filter by Drupal core compatibility
    """
    # Check if module exists
    module = await crud_module.get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    versions, total = await crud_module_version.get_module_versions(
        db=db,
        module_id=module_id,
        skip=skip,
        limit=limit,
        only_security=only_security,
        drupal_core=drupal_core,
    )

    # Convert to response format with module information
    version_responses = []
    for version in versions:
        # Convert database string to list for API response
        compatibility_list = []
        if version.drupal_core_compatibility:
            compatibility_list = version.drupal_core_compatibility.split(",")
        
        version_response = ModuleVersionResponse(
            id=version.id,
            module_id=version.module_id,
            version_string=version.version_string,
            release_date=version.release_date,
            is_security_update=version.is_security_update,
            release_notes=version.release_notes,
            drupal_core_compatibility=compatibility_list,
            is_active=version.is_active,
            is_deleted=version.is_deleted,
            created_at=version.created_at,
            updated_at=version.updated_at,
            created_by=version.created_by,
            updated_by=version.updated_by,
            module_name=module.display_name,
            module_machine_name=module.machine_name,
        )
        version_responses.append(version_response)

    pages = ceil(total / limit) if limit > 0 else 1
    page = (skip // limit) + 1 if limit > 0 else 1

    return ModuleVersionListResponse(
        data=version_responses, total=total, page=page, per_page=limit, pages=pages
    )


@router.get("/{module_id}/latest-version", response_model=ModuleVersionResponse)
async def get_latest_module_version(
    module_id: int,
    db: AsyncSession = Depends(deps.get_db),
    security_only: bool = Query(False, description="Get latest security version only"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get the latest version for a module.

    - **security_only**: Get latest security version instead of latest overall version
    """
    # Check if module exists
    module = await crud_module.get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    if security_only:
        version = await crud_module_version.get_latest_security_version(db, module_id)
    else:
        version = await crud_module_version.get_latest_version(db, module_id)

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No versions found for this module",
        )

    # Convert database string to list for API response
    compatibility_list = []
    if version.drupal_core_compatibility:
        compatibility_list = version.drupal_core_compatibility.split(",")
    
    return ModuleVersionResponse(
        id=version.id,
        module_id=version.module_id,
        version_string=version.version_string,
        release_date=version.release_date,
        is_security_update=version.is_security_update,
        release_notes=version.release_notes,
        drupal_core_compatibility=compatibility_list,
        is_active=version.is_active,
        is_deleted=version.is_deleted,
        created_at=version.created_at,
        updated_at=version.updated_at,
        created_by=version.created_by,
        updated_by=version.updated_by,
        module_name=module.display_name,
        module_machine_name=module.machine_name,
    )
