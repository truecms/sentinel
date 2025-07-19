# Test Coverage Improvement Plan

## Current State
- **Current Coverage**: 41%
- **Target Coverage**: 80%
- **Gap**: 39%

## Priority Areas for Improvement

### 1. Critical Services (Current: 10-20%)
These services contain core business logic and should be prioritized:

#### Version Comparator Service (10% coverage)
- **File**: `app/services/version_comparator.py`
- **Missing Tests**:
  - Drupal version comparison logic
  - Semantic version parsing
  - Pre-release version handling
  - Security update detection
- **Estimated Coverage Gain**: +3%

#### Dashboard Aggregator Service (18% coverage)
- **File**: `app/services/dashboard_aggregator.py`
- **Missing Tests**:
  - Security metrics aggregation
  - Module update statistics
  - Organization-level rollups
  - Site health scoring
- **Estimated Coverage Gain**: +4%

#### Update Detector Service (20% coverage)
- **File**: `app/services/update_detector.py`
- **Missing Tests**:
  - Drupal.org API integration
  - Security advisory parsing
  - Update availability detection
- **Estimated Coverage Gain**: +2%

### 2. CRUD Operations (Current: 16-26%)
Database operations that need comprehensive testing:

#### Module CRUD (16% coverage)
- **File**: `app/crud/crud_module.py`
- **Missing Tests**:
  - Module search functionality
  - Batch operations
  - Complex filtering
- **Estimated Coverage Gain**: +3%

#### Site Module CRUD (17% coverage)
- **File**: `app/crud/crud_site_module.py`
- **Missing Tests**:
  - Module-site associations
  - Version tracking
  - Update flagging
- **Estimated Coverage Gain**: +3%

### 3. API Endpoints (Current: 20-27%)
REST API endpoints need integration tests:

#### Organizations Endpoint (20% coverage)
- **File**: `app/api/v1/endpoints/organizations.py`
- **Missing Tests**:
  - User management within orgs
  - Permission checks
  - Filtering and pagination
- **Estimated Coverage Gain**: +2%

#### Sites Endpoint (20% coverage)
- **File**: `app/api/v1/endpoints/sites.py`
- **Missing Tests**:
  - Site CRUD operations
  - Module synchronization
  - API token validation
- **Estimated Coverage Gain**: +3%

### 4. WebSocket Features (Current: 0-24%)
Real-time features are completely untested:

#### WebSocket Schema (0% coverage)
- **File**: `app/schemas/ws.py`
- **Missing Tests**:
  - Message validation
  - Channel subscription schemas
- **Estimated Coverage Gain**: +1%

#### WebSocket Core (23% coverage)
- **File**: `app/core/websocket.py`
- **Missing Tests**:
  - Connection management
  - Channel broadcasting
  - Error handling
- **Estimated Coverage Gain**: +2%

### 5. Background Tasks (Current: 19%)
Async task processing needs testing:

#### Sync Tasks (19% coverage)
- **File**: `app/tasks/sync_tasks.py`
- **Missing Tests**:
  - Drupal data synchronization
  - Scheduled update checks
  - Error recovery
- **Estimated Coverage Gain**: +2%

## Implementation Strategy

### Phase 1: Critical Services (Week 1)
Focus on services that contain business logic:
1. Version Comparator tests
2. Dashboard Aggregator tests
3. Update Detector tests
**Expected Coverage**: 41% → 50%

### Phase 2: CRUD Operations (Week 2)
Test database operations thoroughly:
1. Module CRUD tests
2. Site Module CRUD tests
3. Organization CRUD tests
**Expected Coverage**: 50% → 58%

### Phase 3: API Integration (Week 3)
Complete API endpoint testing:
1. Organizations API tests
2. Sites API tests
3. Modules API tests
**Expected Coverage**: 58% → 68%

### Phase 4: Real-time Features (Week 4)
Test WebSocket and async features:
1. WebSocket connection tests
2. Channel subscription tests
3. Background task tests
**Expected Coverage**: 68% → 75%

### Phase 5: Edge Cases & Polish (Week 5)
Fill remaining gaps:
1. Error handling scenarios
2. Permission edge cases
3. Performance tests
**Expected Coverage**: 75% → 80%+

## Quick Wins (Can implement immediately)

1. **WebSocket Schema Tests** (1% gain, 30 minutes)
   - Simple schema validation tests
   
2. **Basic CRUD Tests** (5% gain, 2 hours)
   - Happy path tests for each CRUD operation
   
3. **Service Unit Tests** (8% gain, 4 hours)
   - Core logic testing without external dependencies

## Test Structure Template

```python
import pytest
from unittest.mock import Mock, patch

class TestServiceName:
    """Test suite for ServiceName functionality."""
    
    @pytest.fixture
    def service(self):
        """Create service instance with mocked dependencies."""
        return ServiceName()
    
    async def test_happy_path(self, service):
        """Test normal operation succeeds."""
        result = await service.operation()
        assert result.success
    
    async def test_error_handling(self, service):
        """Test error scenarios are handled gracefully."""
        with pytest.raises(ExpectedException):
            await service.failing_operation()
    
    @patch('external.dependency')
    async def test_integration(self, mock_dep, service):
        """Test integration with external services."""
        mock_dep.return_value = {"status": "ok"}
        result = await service.integrated_operation()
        assert result.processed
```

## Success Metrics

1. **Coverage Target**: 80% overall coverage
2. **Critical Path Coverage**: 95% for authentication/authorization
3. **Service Layer Coverage**: 85% for business logic
4. **API Coverage**: 90% for all endpoints
5. **Error Path Coverage**: 70% for error handling

## Next Steps

1. Start with quick wins to boost morale and coverage
2. Focus on critical services first (highest impact)
3. Use TDD for new features going forward
4. Set up coverage gates in CI/CD pipeline
5. Regular coverage reviews in sprint planning