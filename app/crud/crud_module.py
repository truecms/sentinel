from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import joinedload

from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.site_module import SiteModule
from app.schemas.module import ModuleCreate, ModuleUpdate

# Define allowed sort fields for validation
ALLOWED_MODULE_SORT_FIELDS = [
    'machine_name', 'display_name', 'module_type', 
    'is_covered', 'created_at', 'updated_at'
]


async def get_module(db: AsyncSession, module_id: int) -> Optional[Module]:
    """Get module by ID."""
    result = await db.execute(select(Module).filter(Module.id == module_id, Module.is_deleted == False))
    return result.scalar_one_or_none()


async def get_module_by_machine_name(db: AsyncSession, machine_name: str) -> Optional[Module]:
    """Get module by machine name."""
    result = await db.execute(
        select(Module).filter(Module.machine_name == machine_name, Module.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def get_modules(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    module_type: Optional[str] = None,
    has_security_update: Optional[bool] = None,
    sort_by: str = "display_name",
    sort_order: str = "asc"
) -> tuple[List[Module], int]:
    """Get modules with filtering, pagination, and search."""
    
    # Validate sort field first to avoid unnecessary database queries
    if sort_by not in ALLOWED_MODULE_SORT_FIELDS:
        raise ValueError(f"Invalid sort field: {sort_by}. Allowed fields: {', '.join(ALLOWED_MODULE_SORT_FIELDS)}")
    
    # Base query
    query = select(Module).filter(Module.is_deleted == False)
    count_query = select(func.count(Module.id)).filter(Module.is_deleted == False)
    
    # Apply search filter
    if search:
        search_filter = or_(
            Module.machine_name.ilike(f"%{search}%"),
            Module.display_name.ilike(f"%{search}%"),
            Module.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
        count_query = count_query.filter(search_filter)
    
    # Apply module type filter
    if module_type:
        query = query.filter(Module.module_type == module_type)
        count_query = count_query.filter(Module.module_type == module_type)
    
    # Apply security update filter
    if has_security_update is not None:
        if has_security_update:
            # Modules that have security updates available
            security_subquery = select(ModuleVersion.module_id).filter(
                ModuleVersion.is_security_update == True,
                ModuleVersion.is_deleted == False
            )
            query = query.filter(Module.id.in_(security_subquery))
            count_query = count_query.filter(Module.id.in_(security_subquery))
        else:
            # Modules that don't have security updates
            security_subquery = select(ModuleVersion.module_id).filter(
                ModuleVersion.is_security_update == True,
                ModuleVersion.is_deleted == False
            )
            query = query.filter(~Module.id.in_(security_subquery))
            count_query = count_query.filter(~Module.id.in_(security_subquery))
    
    # Apply sorting
    sort_field = getattr(Module, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute queries
    result = await db.execute(query)
    modules = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return modules, total


async def get_module_with_details(
    db: AsyncSession, 
    module_id: int,
    include_versions: bool = True,
    include_sites: bool = False
) -> Optional[Module]:
    """Get module with optional nested data."""
    query = select(Module).filter(Module.id == module_id, Module.is_deleted == False)
    
    if include_versions:
        query = query.options(joinedload(Module.versions))
    
    if include_sites:
        query = query.options(joinedload(Module.site_modules))
    
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()


async def create_module(db: AsyncSession, module: ModuleCreate, created_by: int) -> Module:
    """Create a new module."""
    db_module = Module(
        machine_name=module.machine_name,
        display_name=module.display_name,
        drupal_org_link=str(module.drupal_org_link) if module.drupal_org_link else None,
        module_type=module.module_type,
        description=module.description,
        created_by=created_by,
        updated_by=created_by
    )
    db.add(db_module)
    await db.commit()
    await db.refresh(db_module)
    return db_module


async def update_module(
    db: AsyncSession, 
    module_id: int, 
    module_update: ModuleUpdate, 
    updated_by: int
) -> Optional[Module]:
    """Update an existing module."""
    db_module = await get_module(db, module_id)
    if not db_module:
        return None
    
    update_data = module_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "drupal_org_link" and value:
            value = str(value)
        setattr(db_module, field, value)
    
    db_module.updated_by = updated_by
    await db.commit()
    await db.refresh(db_module)
    return db_module


async def delete_module(db: AsyncSession, module_id: int, updated_by: int) -> Optional[Module]:
    """Soft delete a module."""
    db_module = await get_module(db, module_id)
    if not db_module:
        return None
    
    db_module.is_deleted = True
    db_module.updated_by = updated_by
    await db.commit()
    await db.refresh(db_module)
    return db_module


async def bulk_upsert_modules(
    db: AsyncSession, 
    modules: List[Dict[str, Any]], 
    created_by: int
) -> Dict[str, Any]:
    """Bulk create or update modules."""
    results = {
        "created": 0,
        "updated": 0,
        "failed": 0,
        "errors": []
    }
    
    for module_data in modules:
        try:
            machine_name = module_data.get("machine_name")
            if not machine_name:
                results["failed"] += 1
                results["errors"].append({
                    "module": module_data,
                    "error": "machine_name is required"
                })
                continue
            
            # Check if module exists
            existing_module = await get_module_by_machine_name(db, machine_name)
            
            if existing_module:
                # Update existing module
                update_data = ModuleUpdate(**{k: v for k, v in module_data.items() if k != "machine_name"})
                await update_module(db, existing_module.id, update_data, created_by)
                results["updated"] += 1
            else:
                # Create new module
                create_data = ModuleCreate(**module_data)
                await create_module(db, create_data, created_by)
                results["created"] += 1
                
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "module": module_data,
                "error": str(e)
            })
    
    return results


async def get_modules_with_security_updates(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> List[Module]:
    """Get modules that have security updates available."""
    security_modules_subquery = select(ModuleVersion.module_id).filter(
        ModuleVersion.is_security_update == True,
        ModuleVersion.is_deleted == False
    ).distinct()
    
    query = select(Module).filter(
        Module.id.in_(security_modules_subquery),
        Module.is_deleted == False
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def search_modules(
    db: AsyncSession,
    search_term: str,
    skip: int = 0,
    limit: int = 100
) -> List[Module]:
    """Search modules by name or description."""
    query = select(Module).filter(
        or_(
            Module.machine_name.ilike(f"%{search_term}%"),
            Module.display_name.ilike(f"%{search_term}%"),
            Module.description.ilike(f"%{search_term}%")
        ),
        Module.is_deleted == False
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_modules_by_machine_names(
    db: AsyncSession,
    machine_names: List[str]
) -> List[Module]:
    """Get multiple modules by their machine names."""
    if not machine_names:
        return []
    
    query = select(Module).filter(
        Module.machine_name.in_(machine_names),
        Module.is_deleted == False
    )
    
    result = await db.execute(query)
    return result.scalars().all()