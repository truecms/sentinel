from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.schemas.module_version import ModuleVersionCreate, ModuleVersionUpdate
from app.services.version_comparator import VersionComparator
from app.services.version_parser import DrupalVersionParser


async def get_module_version(
    db: AsyncSession, version_id: int
) -> Optional[ModuleVersion]:
    """Get module version by ID."""
    result = await db.execute(
        select(ModuleVersion).filter(
            ModuleVersion.id == version_id, ModuleVersion.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def get_module_version_with_module(
    db: AsyncSession, version_id: int
) -> Optional[ModuleVersion]:
    """Get module version with module information."""
    result = await db.execute(
        select(ModuleVersion)
        .options(joinedload(ModuleVersion.module))
        .filter(ModuleVersion.id == version_id, ModuleVersion.is_deleted == False)
    )
    return result.unique().scalar_one_or_none()


async def get_module_versions(
    db: AsyncSession,
    module_id: int,
    skip: int = 0,
    limit: int = 100,
    only_security: bool = False,
    drupal_core: Optional[str] = None,
) -> tuple[List[ModuleVersion], int]:
    """Get versions for a specific module with filtering."""

    # Base query and count query
    query = select(ModuleVersion).filter(
        ModuleVersion.module_id == module_id, ModuleVersion.is_deleted == False
    )

    count_query = select(func.count(ModuleVersion.id)).filter(
        ModuleVersion.module_id == module_id, ModuleVersion.is_deleted == False
    )

    # Apply security filter
    if only_security:
        query = query.filter(ModuleVersion.is_security_update == True)
        count_query = count_query.filter(ModuleVersion.is_security_update == True)

    # Apply Drupal core compatibility filter
    if drupal_core:
        # Use PostgreSQL's JSONB ? operator for JSON array containment
        from sqlalchemy import text

        json_filter = text(f"drupal_core_compatibility::jsonb ? '{drupal_core}'")
        query = query.filter(json_filter)
        count_query = count_query.filter(json_filter)

    # Order by release date descending (newest first)
    query = query.order_by(desc(ModuleVersion.release_date)).offset(skip).limit(limit)

    # Execute queries
    result = await db.execute(query)
    versions = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return versions, total


async def get_latest_version(
    db: AsyncSession, module_id: int
) -> Optional[ModuleVersion]:
    """Get the latest version for a module."""
    result = await db.execute(
        select(ModuleVersion)
        .filter(ModuleVersion.module_id == module_id, ModuleVersion.is_deleted == False)
        .order_by(desc(ModuleVersion.release_date))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_security_version(
    db: AsyncSession, module_id: int
) -> Optional[ModuleVersion]:
    """Get the latest security version for a module."""
    result = await db.execute(
        select(ModuleVersion)
        .filter(
            ModuleVersion.module_id == module_id,
            ModuleVersion.is_security_update == True,
            ModuleVersion.is_deleted == False,
        )
        .order_by(desc(ModuleVersion.release_date))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_version_by_module_and_string(
    db: AsyncSession, module_id: int, version_string: str
) -> Optional[ModuleVersion]:
    """Get specific version by module ID and version string."""
    result = await db.execute(
        select(ModuleVersion).filter(
            ModuleVersion.module_id == module_id,
            ModuleVersion.version_string == version_string,
            ModuleVersion.is_deleted == False,
        )
    )
    return result.scalar_one_or_none()


async def create_module_version(
    db: AsyncSession, version: ModuleVersionCreate, created_by: int
) -> ModuleVersion:
    """Create a new module version."""
    db_version = ModuleVersion(
        module_id=version.module_id,
        version_string=version.version_string,
        semantic_version=version.semantic_version,
        release_date=version.release_date,
        is_security_update=version.is_security_update,
        release_notes_link=(
            str(version.release_notes_link) if version.release_notes_link else None
        ),
        drupal_core_compatibility=version.drupal_core_compatibility,
        created_by=created_by,
        updated_by=created_by,
    )
    db.add(db_version)
    await db.commit()
    await db.refresh(db_version)
    return db_version


async def update_module_version(
    db: AsyncSession,
    version_id: int,
    version_update: ModuleVersionUpdate,
    updated_by: int,
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
    db: AsyncSession, version_id: int, updated_by: int
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
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[ModuleVersion]:
    """Get all security update versions."""
    result = await db.execute(
        select(ModuleVersion)
        .options(joinedload(ModuleVersion.module))
        .filter(
            ModuleVersion.is_security_update == True, ModuleVersion.is_deleted == False
        )
        .order_by(desc(ModuleVersion.release_date))
        .offset(skip)
        .limit(limit)
    )
    return result.unique().scalars().all()


async def get_versions_by_drupal_core(
    db: AsyncSession, drupal_core: str, skip: int = 0, limit: int = 100
) -> List[ModuleVersion]:
    """Get versions compatible with specific Drupal core version."""
    from sqlalchemy import text

    # Use raw SQL with PostgreSQL JSON operators for more reliable querying
    # This approach handles JSON arrays of any length
    result = await db.execute(
        select(ModuleVersion)
        .options(joinedload(ModuleVersion.module))
        .filter(
            and_(
                # Check if the JSON array contains the drupal_core version
                # Using PostgreSQL's ? operator which works with JSON type
                text(f"drupal_core_compatibility::jsonb ? '{drupal_core}'"),
                ModuleVersion.is_deleted == False,
            )
        )
        .order_by(desc(ModuleVersion.release_date))
        .offset(skip)
        .limit(limit)
    )
    return result.unique().scalars().all()


async def check_version_exists(
    db: AsyncSession, module_id: int, version_string: str
) -> bool:
    """Check if a version already exists for a module."""
    result = await db.execute(
        select(ModuleVersion.id).filter(
            ModuleVersion.module_id == module_id,
            ModuleVersion.version_string == version_string,
            ModuleVersion.is_deleted == False,
        )
    )
    return result.scalar_one_or_none() is not None


async def get_latest_version_using_comparator(
    db: AsyncSession, module_id: int, stable_only: bool = True
) -> Optional[ModuleVersion]:
    """
    Get the latest version for a module using version comparison logic.

    Args:
        db: Database session
        module_id: Module ID
        stable_only: If True, only consider stable and security releases

    Returns:
        Latest ModuleVersion or None
    """
    # Get all versions for the module
    result = await db.execute(
        select(ModuleVersion).filter(
            ModuleVersion.module_id == module_id, ModuleVersion.is_deleted == False
        )
    )
    versions = result.scalars().all()

    if not versions:
        return None

    # Use comparator to find latest
    comparator = VersionComparator()
    version_strings = [v.version_string for v in versions]
    latest_string = comparator.get_latest_version(
        version_strings, stable_only=stable_only
    )

    if not latest_string:
        return None

    # Find and return the matching version object
    for version in versions:
        if version.version_string == latest_string:
            return version

    return None


async def compare_versions(db: AsyncSession, version1_id: int, version2_id: int) -> int:
    """
    Compare two versions.

    Args:
        db: Database session
        version1_id: First version ID
        version2_id: Second version ID

    Returns:
        -1 if version1 < version2
        0 if version1 == version2
        1 if version1 > version2

    Raises:
        ValueError: If either version not found
    """
    version1 = await get_module_version(db, version1_id)
    version2 = await get_module_version(db, version2_id)

    if not version1 or not version2:
        raise ValueError("Version not found")

    comparator = VersionComparator()
    return comparator.compare(version1.version_string, version2.version_string)


async def get_versions_for_comparison(
    db: AsyncSession,
    module_id: int,
    drupal_core: Optional[str] = None,
    major_version: Optional[int] = None,
) -> List[ModuleVersion]:
    """
    Get versions filtered by compatibility criteria.

    Args:
        db: Database session
        module_id: Module ID
        drupal_core: Drupal core version to filter by
        major_version: Major version to filter by

    Returns:
        List of compatible ModuleVersion objects
    """
    # Get all versions
    result = await db.execute(
        select(ModuleVersion).filter(
            ModuleVersion.module_id == module_id, ModuleVersion.is_deleted == False
        )
    )
    all_versions = result.scalars().all()

    if not all_versions:
        return []

    # Use comparator to filter
    comparator = VersionComparator()
    version_strings = [v.version_string for v in all_versions]
    compatible_strings = comparator.filter_compatible_versions(
        version_strings, drupal_core=drupal_core, major_version=major_version
    )

    # Return matching version objects
    compatible_versions = []
    for version in all_versions:
        if version.version_string in compatible_strings:
            compatible_versions.append(version)

    return compatible_versions


async def update_version_metadata(
    db: AsyncSession, version_id: int, updated_by: str
) -> Optional[ModuleVersion]:
    """
    Update version metadata using parser.

    Updates semantic_version field and drupal_core_compatibility.

    Args:
        db: Database session
        version_id: Version ID
        updated_by: User making the update

    Returns:
        Updated ModuleVersion or None
    """
    version = await get_module_version(db, version_id)
    if not version:
        return None

    parser = DrupalVersionParser()
    try:
        parsed = parser.parse(version.version_string)

        # Update semantic version
        version.semantic_version = parsed.to_semantic()

        # Update drupal core compatibility if detected
        if parsed.drupal_core:
            version.drupal_core_compatibility = [parsed.drupal_core]

        version.updated_by = updated_by
        await db.commit()
        await db.refresh(version)

        return version
    except ValueError:
        # Invalid version string, skip update
        return version
