from datetime import datetime
from math import ceil
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import crud_module, crud_module_version, crud_site_module
from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.site import Site
from app.models.site_module import SiteModule
from app.models.user import User
from app.schemas.base import PaginatedResponse, get_pagination_params
from app.schemas.module import (
    ModuleCreate,
    ModuleListResponse,
    ModuleResponse,
    ModuleStatusItem,
    ModuleStatusResponse,
    ModuleUpdate,
    ModuleUpdateInfo,
)

router = APIRouter()


@router.get("/", response_model=ModuleListResponse)
async def get_modules(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of records to return"
    ),
    search: Optional[str] = Query(None, description="Search in name and description"),
    module_type: Optional[str] = Query(
        None, regex="^(contrib|custom|core)$", description="Filter by module type"
    ),
    has_security_update: Optional[bool] = Query(
        None, description="Filter modules with security updates"
    ),
    sort_by: str = Query(
        "display_name",
        regex="^(display_name|machine_name|created_at|updated_at)$",
        description="Field to sort by",
    ),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
    current_user: User = Depends(deps.get_current_user),
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
    try:
        modules, total = await crud_module.get_modules(
            db=db,
            skip=skip,
            limit=limit,
            search=search,
            module_type=module_type,
            has_security_update=has_security_update,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Calculate additional response fields for each module
    module_responses = []
    for module in modules:
        # Get versions count
        versions_result = await crud_module_version.get_module_versions(
            db, module.id, limit=1000
        )
        versions_count = len(versions_result[0])

        # Get sites count
        sites_result = await crud_site_module.get_module_sites(
            db, module.id, limit=1000
        )
        sites_count = len(sites_result[0])

        # Get latest version
        latest_version = await crud_module_version.get_latest_version(db, module.id)
        latest_version_string = (
            latest_version.version_string if latest_version else None
        )

        # Check for security updates
        has_security = (
            await crud_module_version.get_latest_security_version(db, module.id)
            is not None
        )

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
            has_security_update=has_security,
        )
        module_responses.append(module_response)

    pages = ceil(total / limit) if limit > 0 else 1
    page = (skip // limit) + 1 if limit > 0 else 1

    return ModuleListResponse(
        data=module_responses, total=total, page=page, per_page=limit, pages=pages
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
    current_user: User = Depends(deps.get_current_user),
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    # Calculate additional fields
    versions_list, versions_count = await crud_module_version.get_module_versions(
        db, module.id, limit=1000
    )

    sites_list, sites_count = await crud_site_module.get_module_sites(
        db, module.id, limit=1000
    )

    latest_version = await crud_module_version.get_latest_version(db, module.id)
    latest_version_string = latest_version.version_string if latest_version else None

    has_security = (
        await crud_module_version.get_latest_security_version(db, module.id) is not None
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
        versions_count=versions_count,
        sites_count=sites_count,
        latest_version=latest_version_string,
        has_security_update=has_security,
    )


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    *,
    db: AsyncSession = Depends(deps.get_db),
    module_id: int,
    module_update: ModuleUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update module information (superuser only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    module = await crud_module.update_module(
        db, module_id, module_update, current_user.id
    )
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    # Calculate additional fields
    versions_list, versions_count = await crud_module_version.get_module_versions(
        db, module.id, limit=1000
    )

    sites_list, sites_count = await crud_site_module.get_module_sites(
        db, module.id, limit=1000
    )

    latest_version = await crud_module_version.get_latest_version(db, module.id)
    latest_version_string = latest_version.version_string if latest_version else None

    has_security = (
        await crud_module_version.get_latest_security_version(db, module.id) is not None
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
        versions_count=versions_count,
        sites_count=sites_count,
        latest_version=latest_version_string,
        has_security_update=has_security,
    )


@router.delete("/{module_id}", response_model=ModuleResponse)
async def delete_module(
    *,
    db: AsyncSession = Depends(deps.get_db),
    module_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Soft delete a module (superuser only).

    This will mark the module as inactive but preserve historical data.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    module = await crud_module.delete_module(db, module_id, current_user.id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
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
        has_security_update=False,
    )


# Note: Bulk module operations are handled via the Drupal site sync endpoint
# POST /api/v1/sites/{site_id}/modules
# The bulk endpoint has been removed as per requirements


# Dashboard-specific endpoints
@router.get("/dashboard/status", response_model=PaginatedResponse[ModuleStatusItem])
async def get_dashboard_module_status(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    pagination=Depends(get_pagination_params),
    search: Optional[str] = Query(None, description="Search modules by name"),
    security_only: bool = Query(
        False, description="Show only modules with security updates"
    ),
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
) -> Any:
    """Get module status overview for dashboard table."""

    # Base query to get module status with aggregated data
    # Group by module AND current version to show multiple rows per module
    query = (
        select(
            Module.id,
            Module.machine_name,
            Module.display_name,
            Module.module_type,
            ModuleVersion.version_string.label("current_version_string"),
            func.count(SiteModule.id).label("total_sites"),
            func.count(
                case((SiteModule.update_available == True, SiteModule.id), else_=None)
            ).label("sites_needing_update"),
            func.count(
                case(
                    (SiteModule.security_update_available == True, SiteModule.id),
                    else_=None,
                )
            ).label("sites_with_security_updates"),
            func.max(SiteModule.updated_at).label("last_updated"),
        )
        .select_from(Module)
        .join(SiteModule, Module.id == SiteModule.module_id)
        .join(ModuleVersion, SiteModule.current_version_id == ModuleVersion.id)
        .join(Site, SiteModule.site_id == Site.id)
    )

    # Apply organization filter if provided
    if org_id:
        query = query.where(Site.organization_id == org_id)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Module.display_name.ilike(search_term),
                Module.machine_name.ilike(search_term),
            )
        )

    # Apply security filter
    if security_only:
        query = query.having(
            func.count(
                case(
                    (SiteModule.security_update_available == True, SiteModule.id),
                    else_=None,
                )
            )
            > 0
        )

    # Group by module AND current version to show multiple rows per module
    query = query.group_by(
        Module.id,
        Module.machine_name,
        Module.display_name,
        Module.module_type,
        ModuleVersion.version_string,
    )

    # Order by security updates first, then by sites needing updates
    query = query.order_by(
        desc("sites_with_security_updates"),
        desc("sites_needing_update"),
        Module.display_name,
    )

    # Get total count for pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.offset(pagination.skip).limit(pagination.limit)

    # Execute query
    result = await db.execute(query)
    modules_data = result.all()

    # Process results - each row now represents a module+version combination
    modules = []
    for row in modules_data:
        # Get latest version for this module (highest version number)
        all_versions_query = select(ModuleVersion.version_string).where(
            and_(ModuleVersion.module_id == row.id, ModuleVersion.is_active == True)
        )
        all_versions_result = await db.execute(all_versions_query)
        all_versions = [v for (v,) in all_versions_result.all()]

        # Sort versions properly and get the highest
        if all_versions:
            from app.services.version_comparator import VersionComparator

            comparator = VersionComparator()
            latest_version = comparator.get_latest_version(all_versions) or "Unknown"
        else:
            latest_version = "Unknown"

        # Create unique ID for module+version combination
        unique_id = f"{row.id}_{row.current_version_string.replace('.', '_')}"

        modules.append(
            ModuleStatusItem(
                id=unique_id,
                name=row.display_name or row.machine_name,
                machine_name=row.machine_name,
                module_type=row.module_type,
                current_version=row.current_version_string,  # Use current version from query
                latest_version=latest_version,
                security_update=row.sites_with_security_updates > 0,
                sites_affected=row.sites_needing_update,
                total_sites=row.total_sites,
                last_updated=row.last_updated or datetime.utcnow(),
                update_info=ModuleUpdateInfo(
                    has_security_update=row.sites_with_security_updates > 0,
                    sites_with_security_updates=row.sites_with_security_updates,
                    sites_needing_regular_update=row.sites_needing_update
                    - row.sites_with_security_updates,
                ),
            )
        )

    return PaginatedResponse(
        items=modules,
        total=total,
        page=pagination.page,
        page_size=pagination.limit,
        pages=((total - 1) // pagination.limit) + 1 if total > 0 else 0,
    )


@router.get("/dashboard/overview", response_model=ModuleStatusResponse)
async def get_dashboard_module_overview(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
) -> Any:
    """Get module overview statistics for dashboard."""

    # Get total modules
    total_modules_query = (
        select(func.count(func.distinct(Module.id)))
        .select_from(Module)
        .join(SiteModule, Module.id == SiteModule.module_id)
        .join(Site, SiteModule.site_id == Site.id)
    )

    # Get modules with updates needed
    modules_with_updates_query = (
        select(func.count(func.distinct(Module.id)))
        .select_from(Module)
        .join(SiteModule, Module.id == SiteModule.module_id)
        .join(Site, SiteModule.site_id == Site.id)
        .where(SiteModule.update_available == True)
    )

    # Get modules with security updates
    modules_with_security_query = (
        select(func.count(func.distinct(Module.id)))
        .select_from(Module)
        .join(SiteModule, Module.id == SiteModule.module_id)
        .join(Site, SiteModule.site_id == Site.id)
        .where(SiteModule.security_update_available == True)
    )

    # Apply organization filter if provided
    if org_id:
        total_modules_query = total_modules_query.where(Site.organization_id == org_id)
        modules_with_updates_query = modules_with_updates_query.where(
            Site.organization_id == org_id
        )
        modules_with_security_query = modules_with_security_query.where(
            Site.organization_id == org_id
        )

    # Execute queries
    total_modules_result = await db.execute(total_modules_query)
    modules_with_updates_result = await db.execute(modules_with_updates_query)
    modules_with_security_result = await db.execute(modules_with_security_query)

    total_modules = total_modules_result.scalar() or 0
    modules_with_updates = modules_with_updates_result.scalar() or 0
    modules_with_security = modules_with_security_result.scalar() or 0

    return ModuleStatusResponse(
        total_modules=total_modules,
        modules_with_updates=modules_with_updates,
        modules_with_security_updates=modules_with_security,
        modules_up_to_date=total_modules - modules_with_updates,
        last_updated=datetime.utcnow(),
    )
