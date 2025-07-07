# API Architecture & Design Patterns

## Overview
This document describes the architectural decisions, design patterns, and structure of the FastAPI monitoring platform.

## Core Architecture

### Technology Stack
- **FastAPI**: Modern async Python web framework
- **SQLAlchemy 2.0**: Async ORM with type hints
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and serialization
- **JWT**: Token-based authentication
- **Redis**: Caching and rate limiting
- **Celery**: Async task processing

### Application Structure
```
app/
├── api/                    # API layer
│   └── v1/                # Version 1 API
│       ├── endpoints/     # Route handlers
│       └── dependencies/  # Shared dependencies
├── core/                  # Core functionality
│   ├── config.py         # Settings management
│   ├── security.py       # Auth utilities
│   └── celery_app.py     # Task queue config
├── crud/                  # Database operations
├── models/               # SQLAlchemy models
├── schemas/              # Pydantic schemas
└── main.py              # Application entry
```

## Key Design Patterns

### 1. Repository Pattern
CRUD classes handle all database operations, separating business logic from data access.

```python
# Example CRUD class
class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(
            select(User).filter(User.email == email)
        )
        return result.scalar_one_or_none()
```

### 2. Dependency Injection
FastAPI's dependency system provides clean separation of concerns.

```python
# Common dependencies
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    # Token validation logic
    return user
```

### 3. Response Envelopes
Standardized API responses with consistent structure.

```python
{
    "data": {...},           # Actual response data
    "meta": {               # Metadata
        "total": 100,
        "page": 1,
        "per_page": 20
    },
    "links": {              # HATEOAS links
        "self": "/api/v1/users?page=1",
        "next": "/api/v1/users?page=2"
    }
}
```

### 4. Soft Deletes
Records are marked inactive instead of being physically deleted.

```python
# Soft delete implementation
async def remove(self, db: AsyncSession, *, id: UUID) -> Optional[ModelType]:
    obj = await self.get(db, id=id)
    if obj:
        obj.is_active = False
        await db.commit()
    return obj
```

### 5. Audit Trail
Automatic tracking of record creation and updates.

```python
class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID, primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(UUID, ForeignKey("users.id"))
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(UUID, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
```

## API Layer Structure

### Endpoints Organization
```
api/v1/endpoints/
├── auth.py          # Authentication endpoints
├── users.py         # User management
├── organizations.py # Organization management
├── sites.py         # Site management
└── modules.py       # Module tracking
```

### Route Structure
- RESTful design: `/api/v1/resource`
- Consistent naming: plural for collections
- Nested resources where logical: `/api/v1/organizations/{id}/users`

### Common Endpoint Patterns
```python
# List with pagination
GET /api/v1/users?page=1&per_page=20

# Get single resource
GET /api/v1/users/{user_id}

# Create resource
POST /api/v1/users

# Update resource
PUT /api/v1/users/{user_id}

# Delete (soft) resource
DELETE /api/v1/users/{user_id}
```

## Authentication & Authorization

### JWT Token Flow
1. User logs in with credentials
2. Server validates and returns JWT token
3. Client includes token in Authorization header
4. Server validates token on each request

### Role-Based Access Control (RBAC)
- **Superuser**: Full system access
- **Organization Admin**: Manage organization and its resources
- **Regular User**: Access to assigned resources only

### Permission Dependencies
```python
# Superuser only
current_superuser = Depends(get_current_active_superuser)

# Organization member
current_org_member = Depends(get_current_organization_member)

# Resource owner
current_owner = Depends(get_resource_owner)
```

## Database Design

### Model Relationships
- **Users ↔ Organizations**: Many-to-Many through membership
- **Organizations → Sites**: One-to-Many
- **Sites → Modules**: One-to-Many
- **All Models**: Audit fields from BaseModel

### Performance Considerations
- Async operations throughout
- Connection pooling
- Lazy loading by default
- Explicit eager loading where needed

## API Versioning

### URL-Based Versioning
- Current: `/api/v1/`
- Future: `/api/v2/`

### Version Header Support
```http
X-API-Version: 1
```

### Backward Compatibility
- Deprecation warnings in headers
- Gradual migration periods
- Clear upgrade documentation

## Error Handling

### Consistent Error Format
```json
{
    "detail": "Resource not found",
    "status_code": 404,
    "type": "not_found",
    "field_errors": [
        {
            "field": "email",
            "message": "Invalid email format"
        }
    ]
}
```

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Performance & Scalability

### Caching Strategy
- Redis for frequently accessed data
- Cache invalidation on updates
- TTL-based expiration

### Rate Limiting
- Redis-based rate limiting
- Per-user and per-IP limits
- Configurable thresholds

### Async Processing
- Celery for background tasks
- Email sending
- Data aggregation
- Report generation

## Security Considerations

### Input Validation
- Pydantic schemas validate all inputs
- SQL injection prevention via ORM
- XSS prevention in responses

### Authentication Security
- Bcrypt password hashing
- JWT token expiration
- Refresh token rotation

### API Security
- CORS configuration
- Rate limiting
- Request size limits
- HTTPS enforcement

## Monitoring & Observability

### Health Checks
```python
@app.get("/health")
def health_check():
    return {"status": "OK"}
```

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking
- Performance metrics

### Metrics
- Request duration
- Database query time
- Cache hit rates
- Error rates

## Best Practices

### DO:
- ✅ Use async/await throughout
- ✅ Validate all inputs with Pydantic
- ✅ Follow RESTful conventions
- ✅ Include proper error messages
- ✅ Document with OpenAPI

### DON'T:
- ❌ Mix sync and async operations
- ❌ Bypass the ORM for queries
- ❌ Return sensitive data in errors
- ❌ Skip permission checks
- ❌ Ignore rate limits

## Related Documentation
- Authentication: `docs/claude/api/AUTHENTICATION.md`
- Database Models: `docs/claude/development/DATABASE_MANAGEMENT.md`
- Testing: `docs/claude/development/TESTING.md`