from typing import Any, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import crud_module_version
from app.models.user import User
from app.schemas.module_version import ModuleVersionResponse

router = APIRouter()


@router.get("/security-versions", response_model=List[ModuleVersionResponse])
async def get_security_versions(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of records to return"
    ),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all security update versions across all modules.
    """
    versions = await crud_module_version.get_security_versions(db, skip, limit)

    return [
        ModuleVersionResponse(
            id=version.id,
            module_id=version.module_id,
            version_string=version.version_string,
            semantic_version=version.semantic_version,
            release_date=version.release_date,
            is_security_update=version.is_security_update,
            release_notes_link=version.release_notes_link,
            drupal_core_compatibility=version.drupal_core_compatibility,
            is_active=version.is_active,
            is_deleted=version.is_deleted,
            created_at=version.created_at,
            updated_at=version.updated_at,
            created_by=version.created_by,
            updated_by=version.updated_by,
            module_name=version.module.display_name,
            module_machine_name=version.module.machine_name,
        )
        for version in versions
    ]


@router.get(
    "/drupal-core/{core_version}/versions", response_model=List[ModuleVersionResponse]
)
async def get_versions_by_drupal_core(
    core_version: str,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of records to return"
    ),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get module versions compatible with a specific Drupal core version.
    """
    versions = await crud_module_version.get_versions_by_drupal_core(
        db, core_version, skip, limit
    )

    return [
        ModuleVersionResponse(
            id=version.id,
            module_id=version.module_id,
            version_string=version.version_string,
            semantic_version=version.semantic_version,
            release_date=version.release_date,
            is_security_update=version.is_security_update,
            release_notes_link=version.release_notes_link,
            drupal_core_compatibility=version.drupal_core_compatibility,
            is_active=version.is_active,
            is_deleted=version.is_deleted,
            created_at=version.created_at,
            updated_at=version.updated_at,
            created_by=version.created_by,
            updated_by=version.updated_by,
            module_name=version.module.display_name,
            module_machine_name=version.module.machine_name,
        )
        for version in versions
    ]
