# Issue 1.3: Implement Data Ingestion Endpoint

**Type**: Feature
**Priority**: P0 - Critical
**Epic**: Core Module Monitoring System
**Estimated Effort**: 5 days
**Labels**: `backend`, `api`, `data-ingestion`, `priority-critical`, `performance`
**Dependencies**: Issue 1.1 (Database Models), Issue 1.2 (Module Management APIs)

## Description
Implement a high-performance data ingestion endpoint that allows Drupal sites to push their module information to the monitoring platform. This endpoint must handle large payloads efficiently, validate data integrity, and update the database with minimal latency.

## Background
Drupal sites will push module data during cron runs, potentially containing:
- 200-500 modules for a typical site
- 1000+ modules for large enterprise sites
- Version information for each module
- Security update status
- Custom module metadata

The endpoint must be resilient, scalable, and provide clear feedback about the ingestion process.

## Technical Specification

### Primary Ingestion Endpoint

#### POST /api/v1/sites/{site_id}/modules/sync
Main endpoint for module data synchronization

```python
@router.post("/sites/{site_id}/modules/sync", response_model=SyncResponse)
async def sync_site_modules(
    site_id: int,
    sync_data: ModuleSyncRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis)
) -> Any:
    """
    Synchronize module data for a Drupal site.
    
    This endpoint accepts module information from Drupal sites and updates
    the monitoring database. It handles:
    - New module discovery
    - Version updates
    - Security status changes
    - Module removal detection
    
    Authentication: API Key required
    Rate Limit: 60 requests per hour per site
    """
```

### Request/Response Models

#### Ingestion Request Model (`app/schemas/module_sync.py`)
```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime

class ModuleInfo(BaseModel):
    """Individual module information from Drupal."""
    machine_name: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., regex="^(core|contrib|custom)$")
    version: str = Field(..., min_length=1, max_length=50)
    status: bool = Field(..., description="Is module enabled")
    schema_version: Optional[int] = Field(None, description="Database schema version")
    package: Optional[str] = Field(None, max_length=255)
    core_compatibility: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    project_link: Optional[str] = None
    security_coverage: bool = Field(default=True)
    
    @validator('version')
    def validate_version(cls, v):
        """Validate version format."""
        # Allow various Drupal version formats
        # Examples: 8.x-1.0, 1.0.0, 2.0.0-beta1, 3.x-dev
        import re
        pattern = r'^(\d+\.x-)?(\d+\.)?(\d+\.)?(\*|\d+)(-\w+)?$'
        if not re.match(pattern, v):
            raise ValueError(f"Invalid version format: {v}")
        return v

class ModuleSyncRequest(BaseModel):
    """Complete sync request from a Drupal site."""
    site_info: Dict[str, Any] = Field(..., description="Site metadata")
    modules: List[ModuleInfo] = Field(..., min_items=1, max_items=2000)
    sync_timestamp: datetime = Field(..., description="When data was collected")
    drupal_version: str = Field(..., regex="^(\d+)\.(\d+)\.(\d+)$")
    php_version: str = Field(..., regex="^(\d+)\.(\d+)\.(\d+)$")
    sync_type: str = Field(default="full", regex="^(full|partial)$")
    
    class Config:
        schema_extra = {
            "example": {
                "site_info": {
                    "name": "Example Site",
                    "environment": "production",
                    "last_cron": "2024-01-15T10:30:00Z"
                },
                "modules": [
                    {
                        "machine_name": "views",
                        "name": "Views",
                        "type": "core",
                        "version": "8.9.0",
                        "status": true,
                        "core_compatibility": ["8.x", "9.x"]
                    }
                ],
                "sync_timestamp": "2024-01-15T10:35:00Z",
                "drupal_version": "9.5.11",
                "php_version": "8.1.0",
                "sync_type": "full"
            }
        }

class SyncResponse(BaseModel):
    """Response after processing sync request."""
    success: bool
    sync_id: str = Field(..., description="Unique sync operation ID")
    site_id: int
    processed_count: int
    new_modules: int = 0
    updated_modules: int = 0
    removed_modules: int = 0
    security_updates_found: int = 0
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    processing_time_ms: int
    next_sync_after: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": true,
                "sync_id": "sync_123e4567-e89b-12d3-a456-426614174000",
                "site_id": 1,
                "processed_count": 245,
                "new_modules": 3,
                "updated_modules": 12,
                "removed_modules": 1,
                "security_updates_found": 2,
                "warnings": ["Unknown module: custom_internal_module"],
                "errors": [],
                "processing_time_ms": 1250,
                "next_sync_after": "2024-01-15T11:35:00Z"
            }
        }
```

### Data Processing Service

#### Module Sync Service (`app/services/module_sync_service.py`)
```python
import asyncio
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from app.models import Module, ModuleVersion, SiteModule, Site
from app.schemas.module_sync import ModuleSyncRequest, SyncResponse, ModuleInfo
from app.core.config import settings
from app.crud import crud_module, crud_module_version, crud_site_module

logger = logging.getLogger(__name__)

class ModuleSyncService:
    """Service for processing module sync requests."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._module_cache: Dict[str, Module] = {}
        self._version_cache: Dict[Tuple[int, str], ModuleVersion] = {}
        
    async def process_sync(
        self,
        site_id: int,
        sync_request: ModuleSyncRequest
    ) -> SyncResponse:
        """Process a complete module sync request."""
        start_time = datetime.utcnow()
        sync_id = self._generate_sync_id()
        
        try:
            # Validate site exists and is active
            site = await self._validate_site(site_id)
            
            # Pre-load existing data for performance
            await self._preload_cache(site_id, sync_request.modules)
            
            # Process modules in batches
            results = await self._process_modules_batch(
                site_id,
                sync_request.modules,
                sync_request.sync_type
            )
            
            # Handle removed modules if full sync
            if sync_request.sync_type == "full":
                removed_count = await self._handle_removed_modules(
                    site_id,
                    {m.machine_name for m in sync_request.modules}
                )
                results["removed_modules"] = removed_count
            
            # Update site last sync timestamp
            await self._update_site_sync_info(site, sync_request)
            
            # Calculate processing time
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Create response
            return SyncResponse(
                success=True,
                sync_id=sync_id,
                site_id=site_id,
                processed_count=len(sync_request.modules),
                new_modules=results["new_modules"],
                updated_modules=results["updated_modules"],
                removed_modules=results.get("removed_modules", 0),
                security_updates_found=results["security_updates"],
                warnings=results["warnings"],
                errors=results["errors"],
                processing_time_ms=processing_time,
                next_sync_after=datetime.utcnow() + timedelta(hours=1)
            )
            
        except Exception as e:
            logger.error(f"Sync failed for site {site_id}: {str(e)}")
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            return SyncResponse(
                success=False,
                sync_id=sync_id,
                site_id=site_id,
                processed_count=0,
                errors=[str(e)],
                processing_time_ms=processing_time
            )
    
    async def _process_modules_batch(
        self,
        site_id: int,
        modules: List[ModuleInfo],
        sync_type: str
    ) -> Dict[str, Any]:
        """Process modules in batches for efficiency."""
        results = {
            "new_modules": 0,
            "updated_modules": 0,
            "security_updates": 0,
            "warnings": [],
            "errors": []
        }
        
        # Process in batches of 100
        batch_size = 100
        for i in range(0, len(modules), batch_size):
            batch = modules[i:i + batch_size]
            batch_results = await asyncio.gather(*[
                self._process_single_module(site_id, module)
                for module in batch
            ], return_exceptions=True)
            
            # Aggregate results
            for result in batch_results:
                if isinstance(result, Exception):
                    results["errors"].append(str(result))
                else:
                    results["new_modules"] += result["is_new"]
                    results["updated_modules"] += result["is_updated"]
                    results["security_updates"] += result["has_security_update"]
                    if result.get("warning"):
                        results["warnings"].append(result["warning"])
        
        return results
    
    async def _process_single_module(
        self,
        site_id: int,
        module_info: ModuleInfo
    ) -> Dict[str, Any]:
        """Process a single module update."""
        result = {
            "is_new": False,
            "is_updated": False,
            "has_security_update": False,
            "warning": None
        }
        
        try:
            # Get or create module
            module = await self._get_or_create_module(module_info)
            
            # Get or create version
            version = await self._get_or_create_version(module, module_info)
            
            # Update site-module relationship
            site_module = await self._update_site_module(
                site_id,
                module.id,
                version.id,
                module_info.status
            )
            
            # Check for updates
            if site_module["is_new"]:
                result["is_new"] = True
            elif site_module["version_changed"]:
                result["is_updated"] = True
            
            # Check for security updates
            if await self._check_security_updates(module.id, version.id):
                result["has_security_update"] = True
            
        except Exception as e:
            logger.warning(f"Error processing module {module_info.machine_name}: {str(e)}")
            result["warning"] = f"Module {module_info.machine_name}: {str(e)}"
        
        return result
    
    async def _get_or_create_module(self, module_info: ModuleInfo) -> Module:
        """Get existing module or create new one."""
        # Check cache first
        if module_info.machine_name in self._module_cache:
            return self._module_cache[module_info.machine_name]
        
        # Check database
        module = await crud_module.get_by_machine_name(
            self.db,
            machine_name=module_info.machine_name
        )
        
        if not module:
            # Create new module
            module_data = {
                "machine_name": module_info.machine_name,
                "display_name": module_info.name,
                "module_type": module_info.type,
                "description": module_info.description,
                "drupal_org_link": module_info.project_link
            }
            module = await crud_module.create(self.db, obj_in=module_data)
        
        # Update cache
        self._module_cache[module_info.machine_name] = module
        return module
    
    async def _get_or_create_version(
        self,
        module: Module,
        module_info: ModuleInfo
    ) -> ModuleVersion:
        """Get existing version or create new one."""
        cache_key = (module.id, module_info.version)
        
        # Check cache first
        if cache_key in self._version_cache:
            return self._version_cache[cache_key]
        
        # Check database
        query = select(ModuleVersion).where(
            and_(
                ModuleVersion.module_id == module.id,
                ModuleVersion.version_string == module_info.version
            )
        )
        result = await self.db.execute(query)
        version = result.scalar_one_or_none()
        
        if not version:
            # Create new version
            version_data = {
                "module_id": module.id,
                "version_string": module_info.version,
                "semantic_version": self._parse_semantic_version(module_info.version),
                "drupal_core_compatibility": module_info.core_compatibility,
                "release_date": datetime.utcnow()  # Will be updated later from drupal.org
            }
            version = await crud_module_version.create(self.db, obj_in=version_data)
        
        # Update cache
        self._version_cache[cache_key] = version
        return version
    
    async def _update_site_module(
        self,
        site_id: int,
        module_id: int,
        version_id: int,
        enabled: bool
    ) -> Dict[str, Any]:
        """Update or create site-module relationship."""
        result = {
            "is_new": False,
            "version_changed": False
        }
        
        # Get existing relationship
        site_module = await crud_site_module.get_by_site_and_module(
            self.db,
            site_id=site_id,
            module_id=module_id
        )
        
        if not site_module:
            # Create new relationship
            site_module_data = {
                "site_id": site_id,
                "module_id": module_id,
                "current_version_id": version_id,
                "enabled": enabled,
                "first_seen": datetime.utcnow(),
                "last_seen": datetime.utcnow()
            }
            await crud_site_module.create(self.db, obj_in=site_module_data)
            result["is_new"] = True
        else:
            # Update existing relationship
            update_data = {
                "enabled": enabled,
                "last_seen": datetime.utcnow()
            }
            
            if site_module.current_version_id != version_id:
                update_data["current_version_id"] = version_id
                update_data["last_updated"] = datetime.utcnow()
                result["version_changed"] = True
            
            await crud_site_module.update(
                self.db,
                db_obj=site_module,
                obj_in=update_data
            )
        
        return result
    
    async def _handle_removed_modules(
        self,
        site_id: int,
        current_module_names: Set[str]
    ) -> int:
        """Mark modules as removed that are no longer reported."""
        # Get all active modules for the site
        query = select(SiteModule).join(Module).where(
            and_(
                SiteModule.site_id == site_id,
                SiteModule.enabled == True
            )
        )
        result = await self.db.execute(query)
        site_modules = result.scalars().all()
        
        removed_count = 0
        for site_module in site_modules:
            if site_module.module.machine_name not in current_module_names:
                # Mark as disabled/removed
                await crud_site_module.update(
                    self.db,
                    db_obj=site_module,
                    obj_in={"enabled": False, "last_seen": datetime.utcnow()}
                )
                removed_count += 1
        
        return removed_count
    
    @staticmethod
    def _parse_semantic_version(version_string: str) -> str:
        """Parse Drupal version string to semantic version."""
        # Convert Drupal versions like "8.x-1.0" to "1.0.0"
        # This is a simplified version, real implementation would be more complex
        import re
        
        # Remove Drupal core prefix
        version = re.sub(r'^\d+\.x-', '', version_string)
        
        # Remove suffixes like -dev, -beta1, etc
        version = re.sub(r'-\w+\d*$', '', version)
        
        # Ensure three parts
        parts = version.split('.')
        while len(parts) < 3:
            parts.append('0')
        
        return '.'.join(parts[:3])
    
    @staticmethod
    def _generate_sync_id() -> str:
        """Generate unique sync operation ID."""
        import uuid
        return f"sync_{uuid.uuid4()}"
```

### Background Processing

#### Async Queue Processing (`app/services/queue_processor.py`)
```python
from redis import Redis
import json
import asyncio
from typing import Dict, Any

class ModuleSyncQueueProcessor:
    """Process module sync requests from queue for large operations."""
    
    def __init__(self, redis_client: Redis, db_session_factory):
        self.redis = redis_client
        self.db_session_factory = db_session_factory
        self.queue_name = "module_sync_queue"
        
    async def enqueue_sync(self, site_id: int, sync_data: Dict[str, Any]) -> str:
        """Add sync request to processing queue."""
        job_id = f"job_{site_id}_{datetime.utcnow().timestamp()}"
        job_data = {
            "job_id": job_id,
            "site_id": site_id,
            "data": sync_data,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add to Redis queue
        self.redis.lpush(self.queue_name, json.dumps(job_data))
        
        # Store job status
        self.redis.setex(
            f"job_status:{job_id}",
            3600,  # 1 hour TTL
            json.dumps({"status": "pending"})
        )
        
        return job_id
    
    async def process_queue(self):
        """Continuously process sync queue."""
        while True:
            try:
                # Get job from queue
                job_data = self.redis.brpop(self.queue_name, timeout=5)
                if not job_data:
                    continue
                
                job = json.loads(job_data[1])
                await self._process_job(job)
                
            except Exception as e:
                logger.error(f"Queue processing error: {str(e)}")
                await asyncio.sleep(5)
```

### Rate Limiting

#### Rate Limit Middleware (`app/middleware/rate_limit.py`)
```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting for sync endpoints."""
    
    def __init__(self, app, redis_client):
        super().__init__(app)
        self.redis = redis_client
        
    async def dispatch(self, request: Request, call_next):
        if request.url.path.endswith("/modules/sync"):
            # Extract site ID from path
            site_id = request.path_params.get("site_id")
            if site_id:
                # Check rate limit (60 requests per hour)
                key = f"rate_limit:sync:{site_id}"
                current = self.redis.incr(key)
                
                if current == 1:
                    self.redis.expire(key, 3600)  # 1 hour
                    
                if current > 60:
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Maximum 60 syncs per hour."
                    )
        
        response = await call_next(request)
        return response
```

## Acceptance Criteria

### Functional Requirements
- [ ] Endpoint accepts module data from Drupal sites
- [ ] Validates all incoming data according to schema
- [ ] Creates new modules automatically when discovered
- [ ] Updates existing module versions correctly
- [ ] Detects removed modules in full sync mode
- [ ] Handles partial sync for incremental updates
- [ ] Returns detailed sync results
- [ ] Processes 1000 modules in under 5 seconds

### Data Integrity
- [ ] No data loss during sync operations
- [ ] Duplicate modules prevented
- [ ] Version history maintained
- [ ] Site-module relationships accurate
- [ ] Concurrent syncs handled safely
- [ ] Transaction rollback on errors

### Performance Requirements
- [ ] Response time < 5s for 1000 modules
- [ ] Memory usage < 500MB per request
- [ ] Database queries optimized with bulk operations
- [ ] Caching reduces database load
- [ ] Queue processing for very large syncs

### Security Requirements
- [ ] API key authentication required
- [ ] Rate limiting enforced (60/hour per site)
- [ ] Input validation prevents injection
- [ ] Large payloads handled safely
- [ ] Audit logging of all syncs

### Error Handling
- [ ] Clear error messages for validation failures
- [ ] Partial success handling
- [ ] Retry logic for transient failures
- [ ] Dead letter queue for failed syncs
- [ ] Monitoring alerts for failures

## Test Requirements

### Unit Tests (`tests/test_services/test_module_sync_service.py`)

```python
class TestModuleSyncService:
    """Test module sync service."""
    
    async def test_process_sync_success(self):
        """Test successful sync processing."""
        # Test with valid data
        # Verify modules created/updated
        # Check response accuracy
    
    async def test_process_new_modules(self):
        """Test discovery of new modules."""
        # Send unknown modules
        # Verify creation
        # Check relationships
    
    async def test_version_updates(self):
        """Test module version updates."""
        # Send updated versions
        # Verify version change tracking
        # Check update flags
    
    async def test_removed_module_detection(self):
        """Test detection of removed modules."""
        # Full sync with missing modules
        # Verify modules marked as removed
    
    async def test_partial_sync(self):
        """Test partial sync mode."""
        # Send subset of modules
        # Verify only specified modules updated
        # Check others remain unchanged
    
    async def test_concurrent_syncs(self):
        """Test handling of concurrent sync requests."""
        # Multiple syncs for same site
        # Verify data consistency
        # Check for race conditions
    
    async def test_large_payload_handling(self):
        """Test with maximum payload size."""
        # 2000 modules
        # Verify performance
        # Check memory usage
```

### Integration Tests (`tests/test_api/test_module_sync.py`)

```python
class TestModuleSyncAPI:
    """Test module sync API endpoint."""
    
    async def test_sync_endpoint_success(self):
        """Test successful sync via API."""
        # POST valid sync data
        # Verify response format
        # Check database updates
    
    async def test_api_key_authentication(self):
        """Test API key requirement."""
        # Request without key - 401
        # Request with invalid key - 401
        # Request with valid key - success
    
    async def test_rate_limiting(self):
        """Test rate limit enforcement."""
        # Send 60 requests - all succeed
        # Send 61st request - 429 error
        # Wait 1 hour - succeeds again
    
    async def test_validation_errors(self):
        """Test input validation."""
        # Invalid version format
        # Missing required fields
        # Invalid module type
        # Verify 422 responses
    
    async def test_site_not_found(self):
        """Test sync for non-existent site."""
        # Sync to invalid site_id
        # Verify 404 response
    
    async def test_database_error_handling(self):
        """Test handling of database errors."""
        # Simulate DB connection failure
        # Verify graceful error response
        # Check rollback behavior
```

### Performance Tests (`tests/test_performance/test_sync_performance.py`)

```python
class TestSyncPerformance:
    """Performance tests for sync endpoint."""
    
    async def test_sync_1000_modules(self):
        """Test sync with 1000 modules."""
        # Measure response time
        # Must complete in < 5 seconds
        # Check resource usage
    
    async def test_concurrent_site_syncs(self):
        """Test multiple sites syncing simultaneously."""
        # 10 sites sync at once
        # Verify all complete successfully
        # Check for performance degradation
    
    async def test_memory_usage(self):
        """Test memory consumption during sync."""
        # Monitor memory during large sync
        # Verify < 500MB usage
        # Check for memory leaks
```

### Load Tests
- Simulate 100 sites syncing within same hour
- Test with varying payload sizes
- Measure database connection pool usage
- Monitor Redis queue performance

## Implementation Steps

1. **Create sync request/response schemas**
   - Define validation rules
   - Add examples for documentation
   - Create error response models

2. **Implement sync service**
   - Module processing logic
   - Version comparison
   - Batch processing
   - Cache management

3. **Create API endpoint**
   - Route definition
   - Authentication check
   - Rate limiting
   - Error handling

4. **Add background processing**
   - Queue for large syncs
   - Async job processing
   - Status tracking

5. **Implement monitoring**
   - Sync metrics
   - Performance tracking
   - Error alerting

6. **Write comprehensive tests**
   - Unit tests for service
   - Integration tests for API
   - Performance benchmarks
   - Load testing

7. **Documentation**
   - API usage guide
   - Drupal module integration
   - Troubleshooting guide

## Dependencies
- Redis for caching and queuing
- API key authentication system
- Site management functionality
- Module models from Issue 1.1

## Definition of Done
- [ ] Endpoint implemented and working
- [ ] All validation rules enforced
- [ ] Performance requirements met
- [ ] Rate limiting functional
- [ ] Background processing for large syncs
- [ ] All tests passing with 80%+ coverage
- [ ] API documentation complete
- [ ] Monitoring and alerting configured
- [ ] Deployed to staging environment
- [ ] Load tested successfully

## Notes
- Consider implementing webhook notifications for completed syncs
- May need to add data compression for very large payloads
- Future: Add support for differential syncs to reduce payload size
- Consider adding sync scheduling to distribute load
- Drupal module will need clear documentation for integration