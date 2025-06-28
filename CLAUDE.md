# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based monitoring and reporting platform providing REST API endpoints for user, organization, and site management with role-based access control (RBAC).

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

## Postman API Testing

### Running Postman Tests
```bash
# Install Newman (Postman CLI) if not already installed
npm install -g newman

# Run the updated Postman collection with proper environment
newman run "postman/FastAPI_Monitoring_Updated.postman_collection.json" -e postman/environment.json

# Run with verbose output for debugging
newman run "postman/FastAPI_Monitoring_Updated.postman_collection.json" -e postman/environment.json --verbose
```

### Postman Collection Maintenance

#### Current Collection Status
- **Active Collection**: `FastAPI_Monitoring_Updated.postman_collection.json` 
- **Environment File**: `postman/environment.json`
- **Legacy Collection**: `FastAPI Monitoring Platform.postman_collection.json` (deprecated)

#### Expected API Endpoint Patterns
The application uses RESTful endpoints with the following patterns:
- **Authentication**: `POST /api/v1/auth/access-token` (form-data: username/password)
- **Users**: `GET|POST /api/v1/users/`, `GET /api/v1/users/{id}`
- **Organizations**: `GET|POST /api/v1/organizations/`, `GET /api/v1/organizations/{id}`
- **Sites**: `GET|POST /api/v1/sites/`, `GET /api/v1/sites/{id}`
- **Health**: `GET /health`

#### When to Update Postman Collection

**ALWAYS update the Postman collection when:**
1. **New API endpoints** are added
2. **Endpoint URLs change** (e.g., `/users/add` → `/users/`)
3. **Request/response schemas change** (new required fields, data types)
4. **Authentication methods change** (token format, headers)
5. **Error response formats change**

#### Updating Postman Collection Process

1. **Test Current Endpoints**:
   ```bash
   # Verify API is running
   curl http://localhost:8000/health
   
   # Check OpenAPI documentation for current endpoints
   curl http://localhost:8000/api/v1/openapi.json | jq '.paths | keys'
   ```

2. **Update Collection Requirements**:
   - Match actual endpoint URLs exactly
   - Use correct HTTP methods (GET/POST/PUT/DELETE)
   - Include proper request headers (Content-Type, Authorization)
   - Set correct request body formats (JSON vs form-data)
   - Add response assertions for status codes and data validation

3. **Token Management**:
   ```javascript
   // In Login test script, use environment variables for token storage
   if (pm.response.code === 200) {
       const responseJson = pm.response.json();
       pm.environment.set('access_token', responseJson.access_token);
   }
   
   // In other requests, use Authorization header
   // Authorization: Bearer {{access_token}}
   ```

4. **Environment Configuration**:
   ```json
   // postman/environment.json should contain:
   {
     "values": [
       {"key": "base_url", "value": "http://localhost:8000"},
       {"key": "admin_email", "value": "admin@example.com"},
       {"key": "admin_password", "value": "admin123"}
     ]
   }
   ```

#### Critical Authentication Setup

**Admin User Password Synchronization:**
```bash
# If Postman auth fails, reset the superuser password
HASH=$(docker-compose exec -T api python -c "from app.core.security import get_password_hash; print(get_password_hash('admin123'))")
docker-compose exec -T db psql -U appuser832jdsf -d postgres -c "UPDATE users SET hashed_password = '$HASH' WHERE email = 'admin@example.com';"
```

#### Common Postman Issues and Solutions

1. **401 Unauthorized on all endpoints**:
   - Check if login is working and token is being set
   - Verify admin credentials in environment file
   - Reset superuser password as shown above

2. **404 Not Found errors**:
   - Check endpoint URLs match current API routes
   - Verify base_url in environment is correct
   - Use OpenAPI docs to confirm current endpoint structure

3. **422 Validation errors**:
   - Check request body schema matches API expectations
   - Verify required fields are included
   - Ensure data types match (integers vs strings)

4. **500 Internal Server errors**:
   - Check API logs: `docker-compose logs api | tail -20`
   - Verify database is running: `docker-compose logs db | tail -10`
   - Check for missing CRUD functions or schema mismatches

#### Integration with CI/CD

The GitHub Actions workflow runs Postman tests automatically:
- Collection: `FastAPI_Monitoring_Updated.postman_collection.json`
- Environment: `postman/environment.json`
- Prerequisites: Docker services must be running and healthy

## Common Pitfalls

1. **Database initialization**: Must manually create database before first run
2. **Test isolation**: Tests use separate database and should not affect development data
3. **Async context**: All database operations must use async/await
4. **Permission checks**: Always verify user has access to organization resources
5. **Audit fields**: Let the system handle created_by/updated_by automatically
6. **Postman collection drift**: Always update collection when API endpoints change
7. **Authentication token expiry**: Tokens expire after 30 minutes, regenerate for long test sessions