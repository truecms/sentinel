from typing import Any, List, Optional
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import crud_module, crud_module_version
from app.models.user import User
from app.schemas.module_version import (
    ModuleVersionCreate,
    ModuleVersionUpdate,
    ModuleVersionResponse,
    ModuleVersionListResponse
)

router = APIRouter()


@router.get("/modules/{module_id}/versions", response_model=ModuleVersionListResponse)
async def get_module_versions(
    module_id: int,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    only_security: bool = Query(False, description="Show only security updates"),
    drupal_core: Optional[str] = Query(None, description="Filter by Drupal core version"),
    current_user: User = Depends(deps.get_current_user)
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    versions, total = await crud_module_version.get_module_versions(
        db=db,
        module_id=module_id,
        skip=skip,
        limit=limit,
        only_security=only_security,
        drupal_core=drupal_core
    )
    
    # Convert to response format with module information
    version_responses = []
    for version in versions:
        version_response = ModuleVersionResponse(
            **version.__dict__,
            module_name=module.display_name,
            module_machine_name=module.machine_name
        )
        version_responses.append(version_response)
    
    pages = ceil(total / limit) if limit > 0 else 1
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return ModuleVersionListResponse(
        data=version_responses,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.post("/module-versions", response_model=ModuleVersionResponse, status_code=201)
async def create_module_version(
    *,
    db: AsyncSession = Depends(deps.get_db),
    version: ModuleVersionCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Register a new module version (superuser only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if module exists
    module = await crud_module.get_module(db, version.module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check if version already exists for this module
    existing_version = await crud_module_version.check_version_exists(
        db, version.module_id, version.version_string
    )
    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Version already exists for this module"
        )
    
    db_version = await crud_module_version.create_module_version(db, version, current_user.id)
    
    return ModuleVersionResponse(
        **db_version.__dict__,
        module_name=module.display_name,
        module_machine_name=module.machine_name
    )


@router.get("/module-versions/{version_id}", response_model=ModuleVersionResponse)
async def get_module_version(
    version_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get detailed information about a specific module version.
    """
    version = await crud_module_version.get_module_version_with_module(db, version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module version not found"
        )
    
    return ModuleVersionResponse(
        **version.__dict__,
        module_name=version.module.display_name,
        module_machine_name=version.module.machine_name
    )


@router.put("/module-versions/{version_id}", response_model=ModuleVersionResponse)
async def update_module_version(
    *,
    db: AsyncSession = Depends(deps.get_db),
    version_id: int,
    version_update: ModuleVersionUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Update a module version (superuser only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    version = await crud_module_version.update_module_version(
        db, version_id, version_update, current_user.id
    )
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module version not found"
        )
    
    # Get module information
    module = await crud_module.get_module(db, version.module_id)
    
    return ModuleVersionResponse(
        **version.__dict__,
        module_name=module.display_name,
        module_machine_name=module.machine_name
    )


@router.delete("/module-versions/{version_id}", response_model=ModuleVersionResponse)
async def delete_module_version(
    *,
    db: AsyncSession = Depends(deps.get_db),
    version_id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Soft delete a module version (superuser only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    version = await crud_module_version.delete_module_version(db, version_id, current_user.id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module version not found"
        )
    
    # Get module information
    module = await crud_module.get_module(db, version.module_id)
    
    return ModuleVersionResponse(
        **version.__dict__,
        module_name=module.display_name,
        module_machine_name=module.machine_name
    )


@router.get("/modules/{module_id}/latest-version", response_model=ModuleVersionResponse)
async def get_latest_module_version(
    module_id: int,
    db: AsyncSession = Depends(deps.get_db),
    security_only: bool = Query(False, description="Get latest security version only"),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get the latest version for a module.
    
    - **security_only**: Get latest security version instead of latest overall version
    """
    # Check if module exists
    module = await crud_module.get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    if security_only:
        version = await crud_module_version.get_latest_security_version(db, module_id)
    else:
        version = await crud_module_version.get_latest_version(db, module_id)
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No versions found for this module"
        )
    
    return ModuleVersionResponse(
        **version.__dict__,
        module_name=module.display_name,
        module_machine_name=module.machine_name
    )


@router.get("/security-versions", response_model=List[ModuleVersionResponse])
async def get_security_versions(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get all security update versions across all modules.
    """
    versions = await crud_module_version.get_security_versions(db, skip, limit)
    
    return [
        ModuleVersionResponse(
            **version.__dict__,
            module_name=version.module.display_name,
            module_machine_name=version.module.machine_name
        )
        for version in versions
    ]


@router.get("/drupal-core/{core_version}/versions", response_model=List[ModuleVersionResponse])
async def get_versions_by_drupal_core(
    core_version: str,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get module versions compatible with a specific Drupal core version.
    """
    versions = await crud_module_version.get_versions_by_drupal_core(
        db, core_version, skip, limit
    )
    
    return [
        ModuleVersionResponse(
            **version.__dict__,
            module_name=version.module.display_name,
            module_machine_name=version.module.machine_name
        )
        for version in versions
    ]