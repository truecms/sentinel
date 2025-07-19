from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import crud_module, crud_module_version
from app.models.user import User
from app.schemas.module_version import (
    ModuleVersionCreate,
    ModuleVersionResponse,
    ModuleVersionUpdate,
)

router = APIRouter()


@router.post("/", response_model=ModuleVersionResponse, status_code=201)
async def create_module_version(
    *,
    db: AsyncSession = Depends(deps.get_db),
    version: ModuleVersionCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Register a new module version (superuser only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Check if module exists
    module = await crud_module.get_module(db, version.module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    # Check if version already exists for this module
    existing_version = await crud_module_version.check_version_exists(
        db, version.module_id, version.version_string
    )
    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Version already exists for this module",
        )

    db_version = await crud_module_version.create_module_version(
        db, version, current_user.id
    )

    # Convert database string to list for API response
    compatibility_list = []
    if db_version.drupal_core_compatibility:
        compatibility_list = db_version.drupal_core_compatibility.split(",")
    
    # Ensure we're within the session context when accessing attributes
    response_data = {
        "id": db_version.id,
        "module_id": db_version.module_id,
        "version_string": db_version.version_string,
        "release_date": db_version.release_date,
        "is_security_update": db_version.is_security_update,
        "release_notes": db_version.release_notes,
        "drupal_core_compatibility": compatibility_list,
        "is_active": db_version.is_active,
        "is_deleted": db_version.is_deleted,
        "created_at": db_version.created_at,
        "updated_at": db_version.updated_at,
        "created_by": db_version.created_by,
        "updated_by": db_version.updated_by,
        "module_name": module.display_name,
        "module_machine_name": module.machine_name,
    }

    return ModuleVersionResponse(**response_data)


@router.get("/{version_id}", response_model=ModuleVersionResponse)
async def get_module_version(
    version_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get detailed information about a specific module version.
    """
    version = await crud_module_version.get_module_version(db, version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module version not found"
        )

    # Get module information separately to avoid relationship access issues
    module = await crud_module.get_module(db, version.module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    # Convert database string to list for API response
    compatibility_list = []
    if version.drupal_core_compatibility:
        compatibility_list = version.drupal_core_compatibility.split(",")

    # Ensure we're within the session context when accessing attributes
    response_data = {
        "id": version.id,
        "module_id": version.module_id,
        "version_string": version.version_string,
        "release_date": version.release_date,
        "is_security_update": version.is_security_update,
        "release_notes": version.release_notes,
        "drupal_core_compatibility": compatibility_list,
        "is_active": version.is_active,
        "is_deleted": version.is_deleted,
        "created_at": version.created_at,
        "updated_at": version.updated_at,
        "created_by": version.created_by,
        "updated_by": version.updated_by,
        "module_name": module.display_name,
        "module_machine_name": module.machine_name,
    }

    return ModuleVersionResponse(**response_data)


@router.put("/{version_id}", response_model=ModuleVersionResponse)
async def update_module_version(
    *,
    db: AsyncSession = Depends(deps.get_db),
    version_id: int,
    version_update: ModuleVersionUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a module version (superuser only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    version = await crud_module_version.update_module_version(
        db, version_id, version_update, current_user.id
    )
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module version not found"
        )

    # Get module information separately to avoid relationship access issues
    module = await crud_module.get_module(db, version.module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    # Convert database string to list for API response
    compatibility_list = []
    if version.drupal_core_compatibility:
        compatibility_list = version.drupal_core_compatibility.split(",")

    # Ensure we're within the session context when accessing attributes
    response_data = {
        "id": version.id,
        "module_id": version.module_id,
        "version_string": version.version_string,
        "release_date": version.release_date,
        "is_security_update": version.is_security_update,
        "release_notes": version.release_notes,
        "drupal_core_compatibility": compatibility_list,
        "is_active": version.is_active,
        "is_deleted": version.is_deleted,
        "created_at": version.created_at,
        "updated_at": version.updated_at,
        "created_by": version.created_by,
        "updated_by": version.updated_by,
        "module_name": module.display_name,
        "module_machine_name": module.machine_name,
    }

    return ModuleVersionResponse(**response_data)


@router.delete("/{version_id}", response_model=ModuleVersionResponse)
async def delete_module_version(
    *,
    db: AsyncSession = Depends(deps.get_db),
    version_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Soft delete a module version (superuser only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    version = await crud_module_version.delete_module_version(
        db, version_id, current_user.id
    )
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module version not found"
        )

    # Get module information separately to avoid relationship access issues
    module = await crud_module.get_module(db, version.module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    # Convert database string to list for API response
    compatibility_list = []
    if version.drupal_core_compatibility:
        compatibility_list = version.drupal_core_compatibility.split(",")

    # Ensure we're within the session context when accessing attributes
    response_data = {
        "id": version.id,
        "module_id": version.module_id,
        "version_string": version.version_string,
        "release_date": version.release_date,
        "is_security_update": version.is_security_update,
        "release_notes": version.release_notes,
        "drupal_core_compatibility": compatibility_list,
        "is_active": version.is_active,
        "is_deleted": version.is_deleted,
        "created_at": version.created_at,
        "updated_at": version.updated_at,
        "created_by": version.created_by,
        "updated_by": version.updated_by,
        "module_name": module.display_name,
        "module_machine_name": module.machine_name,
    }

    return ModuleVersionResponse(**response_data)
