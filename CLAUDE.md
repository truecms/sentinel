# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based monitoring and reporting platform providing REST API endpoints for user, organization, and site management with role-based access control (RBAC).

## Repository Information

- Github repository for this project: https://github.com/truecms/sentinel

## Key Commands

### Development Setup
```bash
# Create database (required first time)
docker-compose exec -u postgres db psql -c "CREATE DATABASE application_db;"

# Start services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Access API documentation
# http://localhost:8000/docs
```

### Testing
```bash
# Run all tests
docker-compose exec test pytest

# Run specific test file
docker-compose exec test pytest tests/test_api/test_auth.py

# Run specific test function
docker-compose exec test pytest tests/test_api/test_auth.py -k test_login

# Run with coverage report
docker-compose exec test pytest --cov=app --cov-report=term-missing

# Tests require 80% minimum coverage
```

### Database Management
```bash
# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback migration
docker-compose exec api alembic downgrade -1

# Connect to database
docker-compose exec -u postgres db psql -d application_db
```

### Common Development Tasks
```bash
# View logs
docker-compose logs -f api

# Restart services
docker-compose restart api

# Rebuild services
docker-compose up -d --build
```

## Architecture

### Core Structure
- **FastAPI Application**: Async REST API with automatic OpenAPI documentation
- **SQLAlchemy + Alembic**: Async ORM with PostgreSQL and migrations
- **JWT Authentication**: Token-based auth with role-based permissions
- **Docker Compose**: Multi-container setup with separate test environment

### Key Components

#### API Layer (`app/api/`)
- **v1/endpoints/**: REST endpoints organized by resource (users, organizations, sites)
- **deps.py**: Common dependencies (auth, database sessions)
- **v1/dependencies/**: Shared dependency injection functions

#### Business Logic (`app/`)
- **crud/**: Database operations with async SQLAlchemy
- **models/**: SQLAlchemy ORM models with audit fields
- **schemas/**: Pydantic models for request/response validation
- **core/**: Configuration and security utilities

#### Database Models
All models inherit from `BaseModel` providing:
- `id`: Primary key
- `created_at`, `created_by`: Creation audit
- `updated_at`, `updated_by`: Update audit
- `is_active`: Soft delete support

#### Authentication & Authorization
- JWT tokens with configurable expiration
- Role-based permissions (superuser, org admin, regular user)
- Organization-scoped access control
- Automatic user context injection via dependencies

### Testing Architecture
- **Dedicated test container**: Isolated environment with test database
- **Async test support**: Full async/await testing capability
- **Fixture-based**: Shared test data and authentication
- **Coverage requirements**: 80% minimum with reports

### Key Design Patterns

1. **Repository Pattern**: CRUD classes handle all database operations
2. **Dependency Injection**: FastAPI's dependency system for auth, db sessions
3. **Response Envelopes**: Standardized API responses with data/meta/links
4. **Soft Deletes**: Records marked inactive instead of deleted
5. **Audit Trail**: Automatic tracking of who created/updated records

## Environment Configuration

Key environment variables:
- `POSTGRES_*`: Database connection settings
- `JWT_SECRET_KEY`: Secret for token generation
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `SUPERUSER_EMAIL/PASSWORD`: Initial admin account

## API Versioning
- Current version: v1
- URL pattern: `/api/v1/[resource]`
- Version can be specified via header: `X-API-Version`

## Common Pitfalls

1. **Database initialization**: Must manually create database before first run
2. **Test isolation**: Tests use separate database and should not affect development data
3. **Async context**: All database operations must use async/await
4. **Permission checks**: Always verify user has access to organization resources
5. **Audit fields**: Let the system handle created_by/updated_by automatically

## Postman Testing

### Running Postman Tests Locally

```bash
# Install Newman CLI (if not already installed)
npm install -g newman

# Run the main API testing collection
newman run "postman/FastAPI Monitoring Platform.postman_collection.json" \
  --environment postman/FastAPI_Testing_Environment.postman_environment.json \
  --reporters cli,json \
  --reporter-json-export postman-results.json

# Alternative: Run with Docker (if Newman is not installed locally)
docker run --rm -v $(pwd)/postman:/etc/newman \
  postman/newman run "FastAPI Monitoring Platform.postman_collection.json" \
  --environment FastAPI_Testing_Environment.postman_environment.json
```

### Current Collection Status

- **Main Collection**: `postman/FastAPI Monitoring Platform.postman_collection.json`
- **Environment File**: `postman/FastAPI_Testing_Environment.postman_environment.json`
- **Legacy Collection**: `postman/FastAPI_Testing_Collection.json` (deprecated)

The main collection includes:
- Authentication workflow (login, token management)
- User management endpoints (CRUD operations)
- Organization management endpoints
- Site management endpoints
- Comprehensive error handling tests

### When to Update Postman Collections

Update the Postman collection when:

1. **New API endpoints are added**: Add corresponding requests to test new functionality
2. **Request/response schemas change**: Update request bodies and assertions
3. **Authentication flow changes**: Modify token management or login procedures
4. **Environment variables change**: Update the environment file with new variables
5. **API versioning updates**: Ensure version headers and URLs are current

### Token Management

The collection uses automatic token management:
- Login request stores JWT token in `{{authToken}}` environment variable
- Subsequent requests automatically include: `Authorization: Bearer {{authToken}}`
- Token expiration is handled by re-authentication when needed

### Environment Configuration

Key environment variables in `FastAPI_Testing_Environment.postman_environment.json`:
- `baseUrl`: API base URL (default: http://localhost:8000)
- `adminEmail`: Default admin user email (admin@example.com)
- `adminPassword`: Default admin password (admin123)
- `authToken`: JWT token (auto-populated by login request)

### Troubleshooting Common Issues

1. **Connection Refused**: Ensure Docker services are running (`docker-compose up -d`)
2. **Authentication Failed**: Check admin credentials in environment file
3. **404 Errors**: Verify API endpoints match current FastAPI routes
4. **Token Expired**: Re-run login request to refresh token
5. **Schema Validation**: Update request bodies to match current Pydantic schemas

### CI/CD Integration

The collection is automatically tested in GitHub Actions:
- Tests run on every PR and push to main
- Uses Docker Compose to start services
- Newman CLI executes the collection
- Results are reported in CI logs

### Updating Collections Process

1. **Make API changes** in the FastAPI application
2. **Test locally** with Postman GUI to verify new functionality
3. **Export updated collection** from Postman GUI
4. **Replace the collection file** in `postman/` directory
5. **Update environment variables** if needed
6. **Test with Newman CLI** to ensure automated tests pass
7. **Commit and push** changes to trigger CI validation