from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import joinedload

from app.models.module_version import ModuleVersion
from app.models.module import Module
from app.schemas.module_version import ModuleVersionCreate, ModuleVersionUpdate


async def get_module_version(db: AsyncSession, version_id: int) -> Optional[ModuleVersion]:
    """Get module version by ID."""
    result = await db.execute(
        select(ModuleVersion).filter(
            ModuleVersion.id == version_id, 
            ModuleVersion.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def get_module_version_with_module(db: AsyncSession, version_id: int) -> Optional[ModuleVersion]:
    """Get module version with module information."""
    result = await db.execute(
        select(ModuleVersion)
        .options(joinedload(ModuleVersion.module))
        .filter(
            ModuleVersion.id == version_id, 
            ModuleVersion.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def get_module_versions(
    db: AsyncSession,
    module_id: int,
    skip: int = 0,
    limit: int = 100,
    only_security: bool = False,
    drupal_core: Optional[str] = None
) -> tuple[List[ModuleVersion], int]:
    """Get versions for a specific module with filtering."""
    
    # Base query and count query
    query = select(ModuleVersion).filter(
        ModuleVersion.module_id == module_id,
        ModuleVersion.is_deleted == False
    )
    
    count_query = select(ModuleVersion).filter(
        ModuleVersion.module_id == module_id,
        ModuleVersion.is_deleted == False
    )
    
    # Apply security filter
    if only_security:
        query = query.filter(ModuleVersion.is_security_update == True)
        count_query = count_query.filter(ModuleVersion.is_security_update == True)
    
    # Apply Drupal core compatibility filter
    if drupal_core:
        # Check if drupal_core is in the JSON array
        query = query.filter(
            ModuleVersion.drupal_core_compatibility.contains([drupal_core])
        )
        count_query = count_query.filter(
            ModuleVersion.drupal_core_compatibility.contains([drupal_core])
        )
    
    # Order by release date descending (newest first)
    query = query.order_by(desc(ModuleVersion.release_date)).offset(skip).limit(limit)
    
    # Execute queries
    result = await db.execute(query)
    versions = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    return versions, total


async def get_latest_version(db: AsyncSession, module_id: int) -> Optional[ModuleVersion]:
    """Get the latest version for a module."""
    result = await db.execute(
        select(ModuleVersion)
        .filter(
            ModuleVersion.module_id == module_id,
            ModuleVersion.is_deleted == False
        )
        .order_by(desc(ModuleVersion.release_date))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_security_version(db: AsyncSession, module_id: int) -> Optional[ModuleVersion]:
    """Get the latest security version for a module."""
    result = await db.execute(
        select(ModuleVersion)
        .filter(
            ModuleVersion.module_id == module_id,
            ModuleVersion.is_security_update == True,
            ModuleVersion.is_deleted == False
        )
        .order_by(desc(ModuleVersion.release_date))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_version_by_module_and_string(
    db: AsyncSession, 
    module_id: int, 
    version_string: str
) -> Optional[ModuleVersion]:
    """Get specific version by module ID and version string."""
    result = await db.execute(
        select(ModuleVersion).filter(
            ModuleVersion.module_id == module_id,
            ModuleVersion.version_string == version_string,
            ModuleVersion.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def create_module_version(
    db: AsyncSession, 
    version: ModuleVersionCreate, 
    created_by: int
) -> ModuleVersion:
    """Create a new module version."""
    db_version = ModuleVersion(
        module_id=version.module_id,
        version_string=version.version_string,
        semantic_version=version.semantic_version,
        release_date=version.release_date,
        is_security_update=version.is_security_update,
        release_notes_link=str(version.release_notes_link) if version.release_notes_link else None,
        drupal_core_compatibility=version.drupal_core_compatibility,
        created_by=created_by,
        updated_by=created_by
    )
    db.add(db_version)
    await db.commit()
    await db.refresh(db_version)
    return db_version


async def update_module_version(
    db: AsyncSession,
    version_id: int,
    version_update: ModuleVersionUpdate,
    updated_by: int
) -> Optional[ModuleVersion]:
    """Update an existing module version."""
    db_version = await get_module_version(db, version_id)
    if not db_version:
        return None
    
    update_data = version_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "release_notes_link" and value:
            value = str(value)
        setattr(db_version, field, value)
    
    db_version.updated_by = updated_by
    await db.commit()
    await db.refresh(db_version)
    return db_version


async def delete_module_version(
    db: AsyncSession, 
    version_id: int, 
    updated_by: int
) -> Optional[ModuleVersion]:
    """Soft delete a module version."""
    db_version = await get_module_version(db, version_id)
    if not db_version:
        return None
    
    db_version.is_deleted = True
    db_version.updated_by = updated_by
    await db.commit()
    await db.refresh(db_version)
    return db_version


async def get_security_versions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[ModuleVersion]:
    """Get all security update versions."""
    result = await db.execute(
        select(ModuleVersion)
        .options(joinedload(ModuleVersion.module))
        .filter(
            ModuleVersion.is_security_update == True,
            ModuleVersion.is_deleted == False
        )
        .order_by(desc(ModuleVersion.release_date))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_versions_by_drupal_core(
    db: AsyncSession,
    drupal_core: str,
    skip: int = 0,
    limit: int = 100
) -> List[ModuleVersion]:
    """Get versions compatible with specific Drupal core version."""
    result = await db.execute(
        select(ModuleVersion)
        .options(joinedload(ModuleVersion.module))
        .filter(
            ModuleVersion.drupal_core_compatibility.contains([drupal_core]),
            ModuleVersion.is_deleted == False
        )
        .order_by(desc(ModuleVersion.release_date))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def check_version_exists(
    db: AsyncSession, 
    module_id: int, 
    version_string: str
) -> bool:
    """Check if a version already exists for a module."""
    result = await db.execute(
        select(ModuleVersion.id).filter(
            ModuleVersion.module_id == module_id,
            ModuleVersion.version_string == version_string,
            ModuleVersion.is_deleted == False
        )
    )
    return result.scalar_one_or_none() is not None