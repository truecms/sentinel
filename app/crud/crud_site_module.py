from typing import List, Optional

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.site import Site
from app.models.site_module import SiteModule
from app.schemas.site_module import SiteModuleCreate, SiteModuleUpdate


async def get_site_module(
    db: AsyncSession, site_module_id: int
) -> Optional[SiteModule]:
    """Get site module by ID."""
    result = await db.execute(
        select(SiteModule).filter(
            SiteModule.id == site_module_id, SiteModule.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def get_site_module_by_site_and_module(
    db: AsyncSession, site_id: int, module_id: int
) -> Optional[SiteModule]:
    """Get site-module relationship by site and module IDs."""
    result = await db.execute(
        select(SiteModule).filter(
            SiteModule.site_id == site_id,
            SiteModule.module_id == module_id,
            SiteModule.is_deleted == False,
        )
    )
    return result.scalar_one_or_none()


async def get_site_modules(
    db: AsyncSession,
    site_id: int,
    skip: int = 0,
    limit: int = 100,
    updates_only: bool = False,
    security_only: bool = False,
    enabled_only: bool = True,
) -> tuple[List[SiteModule], int]:
    """Get all modules for a specific site with filtering."""

    # Base query with joins for efficient loading
    query = (
        select(SiteModule)
        .options(
            joinedload(SiteModule.module),
            joinedload(SiteModule.current_version),
            joinedload(SiteModule.latest_version),
            joinedload(SiteModule.site),
        )
        .filter(SiteModule.site_id == site_id, SiteModule.is_deleted == False)
    )

    count_query = select(func.count(SiteModule.id)).filter(
        SiteModule.site_id == site_id, SiteModule.is_deleted == False
    )

    # Apply enabled filter
    if enabled_only:
        query = query.filter(SiteModule.enabled == True)
        count_query = count_query.filter(SiteModule.enabled == True)

    # Apply updates filter
    if updates_only:
        query = query.filter(SiteModule.update_available == True)
        count_query = count_query.filter(SiteModule.update_available == True)

    # Apply security updates filter
    if security_only:
        query = query.filter(SiteModule.security_update_available == True)
        count_query = count_query.filter(SiteModule.security_update_available == True)

    # Order by module name
    query = query.join(Module).order_by(Module.display_name).offset(skip).limit(limit)

    # Execute queries
    result = await db.execute(query)
    site_modules = result.unique().scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return site_modules, total


async def get_module_sites(
    db: AsyncSession,
    module_id: int,
    version_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[List[SiteModule], int]:
    """Get all sites using a specific module, optionally filtered by version."""

    query = (
        select(SiteModule)
        .options(
            joinedload(SiteModule.site),
            joinedload(SiteModule.current_version),
            joinedload(SiteModule.module),
        )
        .filter(SiteModule.module_id == module_id, SiteModule.is_deleted == False)
    )

    count_query = select(func.count(SiteModule.id)).filter(
        SiteModule.module_id == module_id, SiteModule.is_deleted == False
    )

    # Filter by specific version if provided
    if version_id:
        query = query.filter(SiteModule.current_version_id == version_id)
        count_query = count_query.filter(SiteModule.current_version_id == version_id)

    # Order by site name
    query = query.join(Site).order_by(Site.name).offset(skip).limit(limit)

    # Execute queries
    result = await db.execute(query)
    site_modules = result.unique().scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return site_modules, total


async def create_site_module(
    db: AsyncSession, site_module: SiteModuleCreate, created_by: int
) -> SiteModule:
    """Create a new site-module association."""
    db_site_module = SiteModule(
        site_id=site_module.site_id,
        module_id=site_module.module_id,
        current_version_id=site_module.current_version_id,
        enabled=site_module.enabled,
        created_by=created_by,
        updated_by=created_by,
    )
    db.add(db_site_module)
    await db.commit()
    await db.refresh(db_site_module)

    # Update the latest version and availability flags
    await update_site_module_availability(db, db_site_module.id)

    return db_site_module


async def update_site_module(
    db: AsyncSession,
    site_id: int,
    module_id: int,
    site_module_update: SiteModuleUpdate,
    updated_by: int,
) -> Optional[SiteModule]:
    """Update a site-module association."""
    db_site_module = await get_site_module_by_site_and_module(db, site_id, module_id)
    if not db_site_module:
        return None

    update_data = site_module_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_site_module, field, value)

    db_site_module.updated_by = updated_by
    await db.commit()
    await db.refresh(db_site_module)

    # Update availability flags if version changed
    if "current_version_id" in update_data:
        await update_site_module_availability(db, db_site_module.id)

    return db_site_module


async def delete_site_module(
    db: AsyncSession, site_id: int, module_id: int, updated_by: int
) -> Optional[SiteModule]:
    """Remove a module from a site (soft delete)."""
    db_site_module = await get_site_module_by_site_and_module(db, site_id, module_id)
    if not db_site_module:
        return None

    db_site_module.is_deleted = True
    db_site_module.updated_by = updated_by
    await db.commit()
    await db.refresh(db_site_module)
    return db_site_module


async def update_site_module_availability(
    db: AsyncSession, site_module_id: int
) -> Optional[SiteModule]:
    """Update availability flags for a site module."""
    site_module = await get_site_module(db, site_module_id)
    if not site_module:
        return None

    # Get the latest version for this module
    latest_version = await db.execute(
        select(ModuleVersion)
        .filter(
            ModuleVersion.module_id == site_module.module_id,
            ModuleVersion.is_deleted == False,
        )
        .order_by(desc(ModuleVersion.release_date))
        .limit(1)
    )
    latest = latest_version.scalar_one_or_none()

    # Get the latest security version
    latest_security = await db.execute(
        select(ModuleVersion)
        .filter(
            ModuleVersion.module_id == site_module.module_id,
            ModuleVersion.is_security_update == True,
            ModuleVersion.is_deleted == False,
        )
        .order_by(desc(ModuleVersion.release_date))
        .limit(1)
    )
    latest_security_version = latest_security.scalar_one_or_none()

    # Update flags
    if latest:
        site_module.latest_version_id = latest.id
        site_module.update_available = latest.id != site_module.current_version_id

    if latest_security_version:
        # Check if current version is older than latest security version
        site_module.security_update_available = (
            latest_security_version.id != site_module.current_version_id
            and latest_security_version.release_date
            > site_module.current_version.release_date
        )
    else:
        site_module.security_update_available = False

    await db.commit()
    await db.refresh(site_module)
    return site_module


async def get_sites_needing_updates(
    db: AsyncSession, security_only: bool = False, skip: int = 0, limit: int = 100
) -> List[SiteModule]:
    """Get site modules that need updates."""
    query = (
        select(SiteModule)
        .options(
            joinedload(SiteModule.site),
            joinedload(SiteModule.module),
            joinedload(SiteModule.current_version),
            joinedload(SiteModule.latest_version),
        )
        .filter(SiteModule.is_deleted == False)
    )

    if security_only:
        query = query.filter(SiteModule.security_update_available == True)
    else:
        query = query.filter(SiteModule.update_available == True)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.unique().scalars().all()


async def get_site_module_stats(db: AsyncSession, site_id: int) -> dict:
    """Get statistics for modules on a site."""

    # Total modules
    total_result = await db.execute(
        select(func.count(SiteModule.id)).filter(
            SiteModule.site_id == site_id, SiteModule.is_deleted == False
        )
    )
    total_modules = total_result.scalar()

    # Enabled modules
    enabled_result = await db.execute(
        select(func.count(SiteModule.id)).filter(
            SiteModule.site_id == site_id,
            SiteModule.enabled == True,
            SiteModule.is_deleted == False,
        )
    )
    enabled_modules = enabled_result.scalar()

    # Modules with updates
    updates_result = await db.execute(
        select(func.count(SiteModule.id)).filter(
            SiteModule.site_id == site_id,
            SiteModule.update_available == True,
            SiteModule.is_deleted == False,
        )
    )
    modules_with_updates = updates_result.scalar()

    # Modules with security updates
    security_result = await db.execute(
        select(func.count(SiteModule.id)).filter(
            SiteModule.site_id == site_id,
            SiteModule.security_update_available == True,
            SiteModule.is_deleted == False,
        )
    )
    modules_with_security_updates = security_result.scalar()

    # Modules by type
    type_results = await db.execute(
        select(Module.module_type, func.count(SiteModule.id))
        .select_from(SiteModule)
        .join(Module)
        .filter(SiteModule.site_id == site_id, SiteModule.is_deleted == False)
        .group_by(Module.module_type)
    )

    type_counts = {row[0]: row[1] for row in type_results.fetchall()}

    return {
        "total_modules": total_modules,
        "enabled_modules": enabled_modules,
        "disabled_modules": total_modules - enabled_modules,
        "modules_with_updates": modules_with_updates,
        "modules_with_security_updates": modules_with_security_updates,
        "contrib_modules": type_counts.get("contrib", 0),
        "custom_modules": type_counts.get("custom", 0),
        "core_modules": type_counts.get("core", 0),
    }


async def check_site_module_exists(
    db: AsyncSession, site_id: int, module_id: int
) -> bool:
    """Check if a site-module association already exists."""
    result = await db.execute(
        select(SiteModule.id).filter(
            SiteModule.site_id == site_id,
            SiteModule.module_id == module_id,
            SiteModule.is_deleted == False,
        )
    )
    return result.scalar_one_or_none() is not None
