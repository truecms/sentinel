# Issue 1.1: Implement Module Database Models

**Type**: Feature
**Priority**: P0 - Critical
**Epic**: Core Module Monitoring System
**Estimated Effort**: 3 days
**Labels**: `backend`, `database`, `models`, `priority-critical`

## Description
Create the foundational database models required for tracking Drupal modules, their versions, and the relationship between sites and modules. These models will form the core data structure for the entire monitoring system.

## Background
The monitoring platform needs to track:
- All Drupal modules across the ecosystem
- Version history for each module
- Which modules are installed on which sites
- Current vs available versions
- Security update status

## Technical Specification

### Database Models to Create

#### 1. Module Model (`app/models/module.py`)
```python
class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    machine_name = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    drupal_org_link = Column(String(500), nullable=True)
    module_type = Column(String(50), nullable=False, default="contrib")  # contrib, custom, core
    description = Column(Text, nullable=True)
    
    # Relationships
    versions = relationship("ModuleVersion", back_populates="module", cascade="all, delete-orphan")
    site_modules = relationship("SiteModule", back_populates="module")
```

#### 2. ModuleVersion Model (`app/models/module_version.py`)
```python
class ModuleVersion(Base):
    __tablename__ = "module_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    version_string = Column(String(50), nullable=False)
    semantic_version = Column(String(50), nullable=True)  # Normalized version for comparison
    release_date = Column(DateTime, nullable=True)
    is_security_update = Column(Boolean, default=False, nullable=False)
    release_notes_link = Column(String(500), nullable=True)
    drupal_core_compatibility = Column(JSON, nullable=True)  # ["9.x", "10.x"]
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('module_id', 'version_string', name='uq_module_version'),
        Index('idx_module_version_security', 'module_id', 'is_security_update'),
        Index('idx_module_version_date', 'module_id', 'release_date'),
    )
    
    # Relationships
    module = relationship("Module", back_populates="versions")
    site_modules = relationship("SiteModule", back_populates="current_version")
```

#### 3. SiteModule Model (`app/models/site_module.py`)
```python
class SiteModule(Base):
    __tablename__ = "site_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    current_version_id = Column(Integer, ForeignKey("module_versions.id"), nullable=False)
    
    # Status fields
    enabled = Column(Boolean, default=True, nullable=False)
    update_available = Column(Boolean, default=False, nullable=False)
    security_update_available = Column(Boolean, default=False, nullable=False)
    latest_version_id = Column(Integer, ForeignKey("module_versions.id"), nullable=True)
    
    # Tracking fields
    first_seen = Column(DateTime, nullable=False, server_default=text('now()'))
    last_seen = Column(DateTime, nullable=False, server_default=text('now()'))
    last_updated = Column(DateTime, nullable=True)  # When version actually changed
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('site_id', 'module_id', name='uq_site_module'),
        Index('idx_site_module_updates', 'site_id', 'update_available', 'security_update_available'),
    )
    
    # Relationships
    site = relationship("Site", back_populates="modules")
    module = relationship("Module", back_populates="site_modules")
    current_version = relationship("ModuleVersion", foreign_keys=[current_version_id])
    latest_version = relationship("ModuleVersion", foreign_keys=[latest_version_id])
```

### Schema Files to Create

#### 1. Module Schemas (`app/schemas/module.py`)
```python
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime

class ModuleBase(BaseModel):
    machine_name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    drupal_org_link: Optional[HttpUrl] = None
    module_type: str = Field(default="contrib", pattern="^(contrib|custom|core)$")
    description: Optional[str] = None

class ModuleCreate(ModuleBase):
    pass

class ModuleUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    drupal_org_link: Optional[HttpUrl] = None
    description: Optional[str] = None

class ModuleInDB(ModuleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ModuleResponse(ModuleInDB):
    versions_count: int = 0
    sites_count: int = 0
    latest_version: Optional[str] = None
    has_security_update: bool = False
```

#### 2. ModuleVersion Schemas (`app/schemas/module_version.py`)
```python
class ModuleVersionBase(BaseModel):
    version_string: str = Field(..., min_length=1, max_length=50)
    semantic_version: Optional[str] = Field(None, max_length=50)
    release_date: Optional[datetime] = None
    is_security_update: bool = False
    release_notes_link: Optional[HttpUrl] = None
    drupal_core_compatibility: Optional[List[str]] = None

class ModuleVersionCreate(ModuleVersionBase):
    module_id: int

class ModuleVersionInDB(ModuleVersionBase):
    id: int
    module_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ModuleVersionResponse(ModuleVersionInDB):
    module_name: str
```

#### 3. SiteModule Schemas (`app/schemas/site_module.py`)
```python
class SiteModuleBase(BaseModel):
    enabled: bool = True

class SiteModuleCreate(SiteModuleBase):
    site_id: int
    module_id: int
    current_version_id: int

class SiteModuleUpdate(BaseModel):
    enabled: Optional[bool] = None
    current_version_id: Optional[int] = None

class SiteModuleInDB(SiteModuleBase):
    id: int
    site_id: int
    module_id: int
    current_version_id: int
    update_available: bool
    security_update_available: bool
    latest_version_id: Optional[int]
    first_seen: datetime
    last_seen: datetime
    last_updated: Optional[datetime]
    
    class Config:
        from_attributes = True

class SiteModuleResponse(SiteModuleInDB):
    module: ModuleResponse
    current_version: ModuleVersionResponse
    latest_version: Optional[ModuleVersionResponse] = None
```

### Database Migrations

Create Alembic migration:
```bash
docker-compose exec api alembic revision --autogenerate -m "Add module tracking models"
```

### Update Model Relationships

#### Update Site Model (`app/models/site.py`)
Add relationship:
```python
modules = relationship("SiteModule", back_populates="site", cascade="all, delete-orphan")
```

## Acceptance Criteria

### Functional Requirements
- [ ] All three models created with proper fields and types
- [ ] Relationships properly defined between models
- [ ] Unique constraints prevent duplicate entries
- [ ] Indexes created for performance-critical queries
- [ ] Cascade delete configured appropriately
- [ ] Models inherit from Base with audit fields

### Schema Requirements
- [ ] Pydantic schemas created for all models
- [ ] Input validation implemented
- [ ] Response models include calculated fields
- [ ] Proper serialization configured

### Database Requirements
- [ ] Alembic migration created and tested
- [ ] Migration runs successfully on clean database
- [ ] Migration is reversible (down migration works)
- [ ] Foreign key constraints properly defined
- [ ] Indexes created for all foreign keys

### Code Quality
- [ ] Type hints on all methods and properties
- [ ] Docstrings for all classes and complex methods
- [ ] Follow existing code patterns and conventions
- [ ] No linting errors (using project's linting config)

## Test Requirements

### Unit Tests (`tests/test_models/`)

#### test_module_model.py
- Test module creation with all fields
- Test unique constraint on machine_name
- Test relationship to versions
- Test cascade delete behavior
- Test module_type validation

#### test_module_version_model.py
- Test version creation
- Test unique constraint on module_id + version_string
- Test relationship to module
- Test semantic version parsing
- Test security update flag

#### test_site_module_model.py
- Test site-module association
- Test unique constraint on site_id + module_id
- Test update detection flags
- Test timestamp updates
- Test relationships to all related models

### Integration Tests (`tests/test_integration/`)

#### test_module_relationships.py
- Test creating module with versions
- Test associating modules with sites
- Test updating module versions
- Test cascade operations
- Test complex queries across relationships

### Schema Tests (`tests/test_schemas/`)

#### test_module_schemas.py
- Test validation of all fields
- Test optional vs required fields
- Test response serialization
- Test computed fields in responses

### Migration Tests
- Test migration on empty database
- Test migration rollback
- Test migration with existing data
- Test foreign key constraints

### Performance Tests
- Query performance with 10,000 modules
- Query performance with 100,000 module versions
- Index effectiveness tests

## Implementation Steps

1. **Create model files**
   - Start with Module model
   - Add ModuleVersion model
   - Add SiteModule model
   - Update Site model relationship

2. **Create schema files**
   - Implement base schemas
   - Add validation rules
   - Create response models

3. **Generate and test migration**
   - Run autogenerate
   - Review generated migration
   - Test up and down migrations

4. **Write comprehensive tests**
   - Unit tests for each model
   - Integration tests for relationships
   - Schema validation tests

5. **Documentation**
   - Update model documentation
   - Add ER diagram
   - Document query patterns

## Dependencies
- Base model class must be working
- Site model must exist
- Alembic must be configured

## Definition of Done
- [ ] All models implemented with proper fields
- [ ] All relationships working bidirectionally
- [ ] Migration tested and working
- [ ] All tests passing with 80%+ coverage
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] No performance regressions

## Notes
- Consider adding a `module_metadata` JSONB field for extensibility
- May need to add full-text search on module names/descriptions later
- Version comparison logic will be implemented in a separate issue
- Consider adding a cache table for expensive calculations