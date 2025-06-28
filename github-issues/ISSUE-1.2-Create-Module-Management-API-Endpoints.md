# Issue 1.2: Create Module Management API Endpoints

**Type**: Feature
**Priority**: P0 - Critical
**Epic**: Core Module Monitoring System
**Estimated Effort**: 3 days
**Labels**: `backend`, `api`, `endpoints`, `priority-critical`
**Dependencies**: Issue 1.1 (Module Database Models)

## Description
Implement comprehensive REST API endpoints for managing modules, versions, and site-module relationships. These endpoints will provide CRUD operations and advanced querying capabilities for the module monitoring system.

## Background
The API needs to support:
- Module discovery and registration
- Version tracking and history
- Site-module association management
- Bulk operations for efficiency
- Advanced filtering and search capabilities

## Technical Specification

### API Endpoints to Implement

#### 1. Module Endpoints (`app/api/v1/endpoints/modules.py`)

##### GET /api/v1/modules
List all modules with pagination and filtering
```python
@router.get("/", response_model=List[ModuleResponse])
async def get_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="Search in name and description"),
    module_type: Optional[str] = Query(None, regex="^(contrib|custom|core)$"),
    has_security_update: Optional[bool] = Query(None),
    sort_by: str = Query("display_name", regex="^(display_name|machine_name|created_at|updated_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve modules with filtering and pagination.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **search**: Search term for module name/description
    - **module_type**: Filter by module type
    - **has_security_update**: Filter modules with security updates
    - **sort_by**: Field to sort by
    - **sort_order**: Sort direction
    """
```

##### POST /api/v1/modules
Create a new module
```python
@router.post("/", response_model=ModuleResponse, status_code=201)
async def create_module(
    module: ModuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Create a new module (superuser only).
    
    Module machine names must be unique across the system.
    """
```

##### GET /api/v1/modules/{module_id}
Get specific module details
```python
@router.get("/{module_id}", response_model=ModuleDetailResponse)
async def get_module(
    module_id: int,
    include_versions: bool = Query(True),
    include_sites: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get detailed information about a specific module.
    
    - **include_versions**: Include version history
    - **include_sites**: Include sites using this module
    """
```

##### PUT /api/v1/modules/{module_id}
Update module information
```python
@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: int,
    module_update: ModuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Update module information (superuser only).
    """
```

##### DELETE /api/v1/modules/{module_id}
Soft delete a module
```python
@router.delete("/{module_id}", response_model=ModuleResponse)
async def delete_module(
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Soft delete a module (superuser only).
    
    This will mark the module as inactive but preserve historical data.
    """
```

##### POST /api/v1/modules/bulk
Bulk create/update modules
```python
@router.post("/bulk", response_model=BulkOperationResponse)
async def bulk_upsert_modules(
    modules: List[ModuleCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Bulk create or update modules (superuser only).
    
    Maximum 1000 modules per request.
    """
```

#### 2. Module Version Endpoints (`app/api/v1/endpoints/module_versions.py`)

##### GET /api/v1/modules/{module_id}/versions
List versions for a module
```python
@router.get("/modules/{module_id}/versions", response_model=List[ModuleVersionResponse])
async def get_module_versions(
    module_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    only_security: bool = Query(False),
    drupal_core: Optional[str] = Query(None, description="Filter by Drupal core version"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get version history for a specific module.
    
    - **only_security**: Show only security updates
    - **drupal_core**: Filter by Drupal core compatibility
    """
```

##### POST /api/v1/module-versions
Create a new version
```python
@router.post("/module-versions", response_model=ModuleVersionResponse, status_code=201)
async def create_module_version(
    version: ModuleVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Register a new module version (superuser only).
    """
```

##### GET /api/v1/module-versions/{version_id}
Get specific version details
```python
@router.get("/module-versions/{version_id}", response_model=ModuleVersionDetailResponse)
async def get_module_version(
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get detailed information about a specific module version.
    """
```

#### 3. Site Module Endpoints (`app/api/v1/endpoints/site_modules.py`)

##### GET /api/v1/sites/{site_id}/modules
List modules for a site
```python
@router.get("/sites/{site_id}/modules", response_model=List[SiteModuleResponse])
async def get_site_modules(
    site_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    updates_only: bool = Query(False),
    security_only: bool = Query(False),
    enabled_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get all modules installed on a specific site.
    
    - **updates_only**: Show only modules with available updates
    - **security_only**: Show only modules with security updates
    - **enabled_only**: Show only enabled modules
    """
```

##### POST /api/v1/sites/{site_id}/modules
Add a module to a site
```python
@router.post("/sites/{site_id}/modules", response_model=SiteModuleResponse, status_code=201)
async def add_site_module(
    site_id: int,
    site_module: SiteModuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Add a module to a site.
    
    User must have permission to manage the site.
    """
```

##### PUT /api/v1/sites/{site_id}/modules/{module_id}
Update site-module relationship
```python
@router.put("/sites/{site_id}/modules/{module_id}", response_model=SiteModuleResponse)
async def update_site_module(
    site_id: int,
    module_id: int,
    update: SiteModuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a site-module relationship (e.g., version, enabled status).
    """
```

##### DELETE /api/v1/sites/{site_id}/modules/{module_id}
Remove a module from a site
```python
@router.delete("/sites/{site_id}/modules/{module_id}", status_code=204)
async def remove_site_module(
    site_id: int,
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Remove a module from a site.
    """
```

##### GET /api/v1/modules/{module_id}/sites
List sites using a module
```python
@router.get("/modules/{module_id}/sites", response_model=List[SiteResponse])
async def get_module_sites(
    module_id: int,
    version_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get all sites using a specific module.
    
    - **version_id**: Filter by specific version
    """
```

### CRUD Operations to Implement

#### 1. Module CRUD (`app/crud/crud_module.py`)
```python
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.crud.base import CRUDBase
from app.models.module import Module
from app.schemas.module import ModuleCreate, ModuleUpdate

class CRUDModule(CRUDBase[Module, ModuleCreate, ModuleUpdate]):
    async def get_by_machine_name(
        self, db: AsyncSession, *, machine_name: str
    ) -> Optional[Module]:
        """Get module by machine name."""
        query = select(Module).where(Module.machine_name == machine_name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def search(
        self,
        db: AsyncSession,
        *,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Module]:
        """Search modules by name or description."""
        query = select(Module).where(
            or_(
                Module.machine_name.ilike(f"%{search_term}%"),
                Module.display_name.ilike(f"%{search_term}%"),
                Module.description.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_with_security_updates(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Module]:
        """Get modules that have security updates available."""
        # Complex query involving joins with versions and site_modules
        pass
    
    async def bulk_upsert(
        self, db: AsyncSession, *, modules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Bulk create or update modules."""
        # Implementation for efficient bulk operations
        pass

module = CRUDModule(Module)
```

#### 2. ModuleVersion CRUD (`app/crud/crud_module_version.py`)
```python
class CRUDModuleVersion(CRUDBase[ModuleVersion, ModuleVersionCreate, ModuleVersionUpdate]):
    async def get_latest_version(
        self, db: AsyncSession, *, module_id: int
    ) -> Optional[ModuleVersion]:
        """Get the latest version for a module."""
        query = select(ModuleVersion).where(
            ModuleVersion.module_id == module_id
        ).order_by(ModuleVersion.release_date.desc()).limit(1)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_latest_security_version(
        self, db: AsyncSession, *, module_id: int
    ) -> Optional[ModuleVersion]:
        """Get the latest security version for a module."""
        query = select(ModuleVersion).where(
            ModuleVersion.module_id == module_id,
            ModuleVersion.is_security_update == True
        ).order_by(ModuleVersion.release_date.desc()).limit(1)
        result = await db.execute(query)
        return result.scalar_one_or_none()

module_version = CRUDModuleVersion(ModuleVersion)
```

#### 3. SiteModule CRUD (`app/crud/crud_site_module.py`)
```python
class CRUDSiteModule(CRUDBase[SiteModule, SiteModuleCreate, SiteModuleUpdate]):
    async def get_by_site_and_module(
        self, db: AsyncSession, *, site_id: int, module_id: int
    ) -> Optional[SiteModule]:
        """Get site-module relationship."""
        query = select(SiteModule).where(
            SiteModule.site_id == site_id,
            SiteModule.module_id == module_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_available_updates(
        self, db: AsyncSession, *, site_module_id: int
    ) -> SiteModule:
        """Check and update available updates for a site module."""
        # Logic to compare versions and set flags
        pass

site_module = CRUDSiteModule(SiteModule)
```

### Response Models

#### Enhanced Response Models (`app/schemas/module_responses.py`)
```python
class ModuleDetailResponse(ModuleResponse):
    """Detailed module response with relationships."""
    versions: List[ModuleVersionResponse] = []
    sites_using: int = 0
    latest_version: Optional[ModuleVersionResponse] = None
    latest_security_version: Optional[ModuleVersionResponse] = None

class SiteModuleDetailResponse(SiteModuleResponse):
    """Detailed site module response."""
    available_updates: List[ModuleVersionResponse] = []
    update_lag_days: Optional[int] = None
    security_lag_days: Optional[int] = None

class BulkOperationResponse(BaseModel):
    """Response for bulk operations."""
    created: int = 0
    updated: int = 0
    failed: int = 0
    errors: List[Dict[str, Any]] = []
```

## Acceptance Criteria

### API Requirements
- [ ] All specified endpoints implemented and functional
- [ ] Proper HTTP status codes returned
- [ ] Consistent error response format
- [ ] Request validation with meaningful error messages
- [ ] Pagination working correctly with proper metadata
- [ ] Filtering and search functionality working
- [ ] Sorting implemented for list endpoints

### Authentication & Authorization
- [ ] All endpoints require authentication
- [ ] Superuser-only endpoints properly restricted
- [ ] Organization-based access control for site modules
- [ ] User can only manage modules for their sites

### Performance Requirements
- [ ] List endpoints return within 200ms for 1000 records
- [ ] Bulk operations handle 1000 items within 5 seconds
- [ ] Database queries use eager loading to avoid N+1
- [ ] Proper indexing utilized in queries

### Data Integrity
- [ ] Duplicate modules prevented by unique constraints
- [ ] Version history maintained correctly
- [ ] Site-module relationships consistent
- [ ] Soft delete preserves historical data

### API Documentation
- [ ] OpenAPI/Swagger documentation auto-generated
- [ ] All parameters documented with descriptions
- [ ] Example requests and responses provided
- [ ] Error responses documented

## Test Requirements

### Unit Tests (`tests/test_crud/`)

#### test_crud_module.py
- Test create module with unique constraint
- Test get by machine name
- Test search functionality
- Test bulk operations
- Test soft delete

#### test_crud_module_version.py
- Test create version with validation
- Test get latest version
- Test get latest security version
- Test version ordering

#### test_crud_site_module.py
- Test create site-module relationship
- Test unique constraint
- Test update detection
- Test removal

### API Integration Tests (`tests/test_api/test_modules.py`)

#### Module Endpoints
- Test list modules with all filter combinations
- Test pagination boundaries
- Test search functionality
- Test create with validation
- Test update with partial data
- Test delete (soft delete behavior)
- Test bulk operations with mixed success/failure

#### Version Endpoints
- Test list versions with filters
- Test create version with duplicate check
- Test security version filtering

#### Site Module Endpoints
- Test list site modules with filters
- Test add module to site
- Test update module version
- Test remove module from site
- Test permission checks

### Performance Tests
- Load test with 10,000 modules
- Bulk operation with 1000 items
- Concurrent request handling
- Query optimization verification

### Security Tests
- Test authentication requirements
- Test authorization for different user roles
- Test SQL injection prevention
- Test input validation

## Implementation Steps

1. **Create CRUD classes**
   - Implement base CRUD operations
   - Add specialized query methods
   - Implement bulk operations

2. **Create API endpoints**
   - Module endpoints with filtering
   - Version endpoints
   - Site module endpoints
   - Add proper error handling

3. **Implement authorization**
   - Add permission checks
   - Implement organization-based access
   - Test with different user roles

4. **Add performance optimizations**
   - Implement eager loading
   - Add query optimization
   - Test with large datasets

5. **Write comprehensive tests**
   - Unit tests for CRUD
   - Integration tests for API
   - Performance tests
   - Security tests

6. **Documentation**
   - Update OpenAPI schemas
   - Add usage examples
   - Document common workflows

## Dependencies
- Issue 1.1 must be completed (database models)
- Authentication system must be working
- Base CRUD class must be available

## Definition of Done
- [ ] All endpoints implemented and working
- [ ] Authorization properly enforced
- [ ] All tests passing with 80%+ coverage
- [ ] Performance requirements met
- [ ] API documentation complete
- [ ] Code reviewed and approved
- [ ] No security vulnerabilities
- [ ] Deployed to staging environment

## Notes
- Consider implementing GraphQL endpoint in future
- May need to add caching layer for frequently accessed data
- Bulk operations should use database-specific features for efficiency
- Consider implementing webhooks for module updates