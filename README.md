# FastAPI Backend Service

## Overview
Backend service providing REST API endpoints for user, organization, and site management with role-based access control.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)

## Features
- User Management with RBAC
- Organization Management
- Site Management
- JWT Authentication
- Rate Limiting
- API Versioning
- Automated Testing
- Docker Deployment

## Prerequisites
- Docker and Docker Compose
- PostgreSQL client (psql) for database management
- Make (optional)

## Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create .env file:
```bash
cp .env.example .env
```

## Database Setup
Before starting the application, you need to create the database manually:

1. First, stop any running containers and remove volumes:
```bash
docker-compose down -v
```

2. Start the database container:
```bash
docker-compose up db -d
```

3. Wait for PostgreSQL to initialize (check logs until you see "database system is ready"):
```bash
docker-compose logs -f db
```

4. Create the database (in a new terminal):
```bash
docker-compose exec -u postgres db psql -c "CREATE DATABASE application_db;"
```

5. Verify the database was created:
```bash
docker-compose exec -u postgres db psql -c "\l"
```

6. Start the API service:
```bash
docker-compose up -d
```

7. Run database migrations:
```bash
docker-compose exec api alembic upgrade head
```

## Running the Application

1. The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- OpenAPI Spec: http://localhost:8000/openapi.json

2. Health check:
```bash
curl http://localhost:8000/health
```

## Development

### Making Database Changes
1. Create a new migration:
```bash
docker-compose exec api alembic revision --autogenerate -m "description"
```

2. Apply migrations:
```bash
docker-compose exec api alembic upgrade head
```

3. Rollback migrations:
```bash
docker-compose exec api alembic downgrade -1
```

### Common Commands
```bash
# View logs
docker-compose logs -f api

# Restart services
docker-compose restart api

# Rebuild services
docker-compose up -d --build

# Connect to database
docker-compose exec -u postgres db psql -d application_db
```

## Testing
Run tests using:
```bash
docker-compose exec api pytest
```

## API Documentation

### API Versioning
- Current version: v1
- Version format: /api/v{version_number}/
- Version header: X-API-Version

### Authentication
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password"
}
```

### Response Format
All API responses follow the standard envelope:
```json
{
    "data": {},
    "meta": {
        "page": 1,
        "per_page": 10,
        "total": 100
    },
    "links": {
        "self": "/api/v1/resource",
        "next": "/api/v1/resource?page=2",
        "prev": null
    }
}
```

### Pagination
- Default page size: 10
- Maximum page size: 100
- Query parameters:
  - page: Page number
  - per_page: Items per page

## Development Setup

### Prerequisites
- Docker
- Docker Compose
- Python 3.11+
- Make (optional)

### Local Setup
1. Clone the repository:
```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

2. Create .env file:
```bash
cp .env.example .env
```

3. Initialize database:
```bash
./scripts/init-db.sh
```

4. Start services:
```bash
docker-compose up -d
```

5. Run migrations:
```bash
docker-compose exec api alembic upgrade head
```

### Development Commands
```bash
# Run tests
make test

# Run linting
make lint

# Generate API documentation
make docs

# Create database migrations
make migrations
```

## Testing

The project includes a comprehensive test suite using pytest. Tests are run in a dedicated Docker container with its own PostgreSQL database instance.

### Test Structure
```
tests/
├── conftest.py           # Test configuration and fixtures
├── test_api/            # API endpoint tests
│   ├── test_auth.py     # Authentication tests
│   ├── test_organizations.py
│   ├── test_sites.py
│   └── test_users.py
└── test_core/           # Core functionality tests
```

### Test Dependencies
Required packages are listed in `requirements-test.txt`:
- pytest
- pytest-asyncio
- pytest-cov
- httpx
- pytest-env
- faker
- pytest-mock
- aiosqlite
- asgi-lifespan

### Running Tests

#### Using Docker (Recommended)
The project includes a dedicated test container with all necessary dependencies and configurations. Here's how to use it:

1. Start the test environment:
```bash
docker-compose up -d test
```

2. Execute tests in the running container:
```bash
# Run all tests
docker-compose exec test pytest

# Run specific test file
docker-compose exec test pytest tests/test_api/test_auth.py

# Run specific test function
docker-compose exec test pytest tests/test_api/test_auth.py -k test_login

# Run tests with coverage report
docker-compose exec test pytest --cov=app --cov-report=term-missing
```

The test container remains running and ready for executing tests at any time. This is particularly useful for:
- Development: Quick test execution during development
- CI/CD: Integration with continuous integration pipelines
- Manual Testing: Ad-hoc test execution as needed

#### Test Configuration
Tests are configured via `pytest.ini`:
- Minimum coverage requirement: 80%
- Coverage reports: Terminal and HTML
- Environment variables for testing
- Async test mode enabled

#### Test Environment
Tests run with these environment variables:
- TESTING=True
- POSTGRES_USER=test_user
- POSTGRES_PASSWORD=test_password
- POSTGRES_DB=test_db
- JWT_SECRET_KEY=testing_secret_key_123
- ACCESS_TOKEN_EXPIRE_MINUTES=30
- SUPERUSER_EMAIL - Admin user email from .env
- SUPERUSER_PASSWORD - Admin user password from .env

The test environment includes a superuser account with full system permissions. This superuser can:
- Create, update, and delete any users
- Manage all organizations
- Access all endpoints without restrictions
- Perform system-wide administrative tasks

This superuser account is particularly useful for:
- Setting up test data
- Testing administrative functions
- Verifying role-based access controls

### Coverage Reports
After running tests, coverage reports are available:
- Terminal output shows missing lines
- HTML report in `htmlcov/` directory
- Minimum required coverage: 80%

### Continuous Integration
The test suite is designed to run in CI environments. The test containers are configured to:
- Use a separate test database
- Run independently of development services
- Generate coverage reports
- Fail if coverage is below 80%

## Deployment

### Production Setup
1. Update production configurations
2. Build production images
3. Deploy using Docker Compose or Kubernetes

### Health Checks
- Readiness: `/health/ready`
- Liveness: `/health/live`
- Dependencies: `/health/deps`

## Troubleshooting

### Common Issues
1. Database Connection
```bash
# Check database status
docker-compose ps db
# View database logs
docker-compose logs db
```

2. API Service
```bash
# Check API logs
docker-compose logs api
# Restart API service
docker-compose restart api
```

3. Authentication Issues
- Verify JWT token expiration
- Check user permissions
- Validate request headers

## Contributing

### Development Workflow
1. Create feature branch
2. Implement changes
3. Add tests
4. Submit PR

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Keep functions focused

### Commit Messages
Format: `type(scope): description`
Example: `feat(auth): add token refresh endpoint`

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

# Organization Management API Documentation

## Overview

The Organization Management API provides endpoints for creating, reading, updating, and deleting organizations. All endpoints require authentication using JWT tokens.

## Authentication

All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. List Organizations

**Endpoint:** `GET /api/v1/organizations/`

**Description:** Retrieves a paginated list of organizations with their associated users.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "name": "Organization Name",
    "description": null,
    "is_active": true,
    "id": 1,
    "created_at": "2025-02-22T12:07:52.945534",
    "created_by": 1,
    "updated_at": "2025-02-22T12:07:52.945536",
    "updated_by": 1,
    "users": []
  }
]
```

### 2. Create Organization

**Endpoint:** `POST /api/v1/organizations/`

**Description:** Creates a new organization.

**Request Body:**
```json
{
  "name": "Organization Name"
}
```

**Response:**
```json
{
  "name": "Organization Name",
  "description": null,
  "is_active": true,
  "id": 1,
  "created_at": "2025-02-22T12:07:52.945534",
  "created_by": 1,
  "updated_at": "2025-02-22T12:07:52.945536",
  "updated_by": 1,
  "users": []
}
```

**Error Responses:**
- `400 Bad Request`: If an organization with the same name already exists
- `401 Unauthorized`: If the authentication token is missing or invalid
- `403 Forbidden`: If the user doesn't have permission to create organizations

### 3. Get Organization Details

**Endpoint:** `GET /api/v1/organizations/{organization_id}`

**Description:** Retrieves detailed information about a specific organization.

**Path Parameters:**
- `organization_id`: The ID of the organization to retrieve

**Response:**
```json
{
  "name": "Organization Name",
  "description": null,
  "is_active": true,
  "id": 1,
  "created_at": "2025-02-22T12:07:52.945534",
  "created_by": 1,
  "updated_at": "2025-02-22T12:07:52.945536",
  "updated_by": 1,
  "users": []
}
```

**Error Responses:**
- `404 Not Found`: If the organization doesn't exist
- `401 Unauthorized`: If the authentication token is missing or invalid
- `403 Forbidden`: If the user doesn't have permission to view the organization

### 4. Update Organization

**Endpoint:** `PUT /api/v1/organizations/{organization_id}`

**Description:** Updates an existing organization.

**Path Parameters:**
- `organization_id`: The ID of the organization to update

**Request Body:**
```json
{
  "name": "Updated Organization Name",
  "description": "Updated description",
  "is_active": true
}
```

**Response:**
```json
{
  "name": "Updated Organization Name",
  "description": "Updated description",
  "is_active": true,
  "id": 1,
  "created_at": "2025-02-22T12:07:52.945534",
  "created_by": 1,
  "updated_at": "2025-02-22T12:07:52.945536",
  "updated_by": 1,
  "users": []
}
```

**Error Responses:**
- `404 Not Found`: If the organization doesn't exist
- `401 Unauthorized`: If the authentication token is missing or invalid
- `403 Forbidden`: If the user doesn't have permission to update the organization

### 5. Delete Organization

**Endpoint:** `DELETE /api/v1/organizations/{organization_id}`

**Description:** Soft deletes an organization by marking it as inactive.

**Path Parameters:**
- `organization_id`: The ID of the organization to delete

**Response:**
```json
{
  "name": "Organization Name",
  "description": null,
  "is_active": false,
  "id": 1,
  "created_at": "2025-02-22T12:07:52.945534",
  "created_by": 1,
  "updated_at": "2025-02-22T12:07:52.945536",
  "updated_by": 1,
  "users": []
}
```

**Error Responses:**
- `404 Not Found`: If the organization doesn't exist
- `401 Unauthorized`: If the authentication token is missing or invalid
- `403 Forbidden`: If the user doesn't have permission to delete the organization

## Data Models

### Organization Schema

```python
{
    "id": int,                    # Organization ID
    "name": str,                  # Organization name (required, unique)
    "description": str | null,    # Optional description
    "is_active": bool,           # Organization status
    "created_at": datetime,      # Creation timestamp
    "created_by": int,           # User ID who created the organization
    "updated_at": datetime,      # Last update timestamp
    "updated_by": int,           # User ID who last updated the organization
    "users": [                   # List of users in the organization
        {
            "id": int,
            "email": str,
            # ... other user fields
        }
    ]
}
```

## Error Handling

All endpoints follow a consistent error response format:

```json
{
    "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (e.g., validation errors)
- `401`: Unauthorized (missing or invalid token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `422`: Unprocessable Entity (validation errors)
- `500`: Internal Server Error

## Authentication

All endpoints require a valid JWT token obtained through the authentication endpoint:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/access-token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=your_email@example.com&password=your_password"
```

The token should be included in the Authorization header of subsequent requests:

```bash
curl -X GET "http://localhost:8000/api/v1/organizations/" \
     -H "Authorization: Bearer your_jwt_token"
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Clients should handle 429 Too Many Requests responses by implementing appropriate backoff strategies.

## Pagination

List endpoints support pagination through `skip` and `limit` query parameters. Clients should use these parameters to handle large datasets efficiently.

## Mock Data for Testing

The repository includes standardized mock JSON data that represents what Drupal modules will be sending to the monitoring platform. This data is used for:

- API testing with realistic payloads
- Development and debugging
- Documentation and reference for Drupal module developers
- Newman data-driven testing

### Mock Data Structure

Mock data files are located in `examples/drupal-submissions/` and follow this structure:

```json
{
  "site": {
    "url": "https://example.com",
    "name": "Example Drupal Site",
    "token": "site-auth-token-123"
  },
  "drupal_info": {
    "core_version": "10.3.8",
    "php_version": "8.3.2",
    "ip_address": "192.168.1.100"
  },
  "modules": [
    {
      "machine_name": "views",
      "display_name": "Views",
      "module_type": "core",
      "enabled": true,
      "version": "10.3.8"
    }
  ]
}
```

### Available Mock Data Files

- **minimal-site.json**: Basic Drupal site with 5-10 essential modules
- **standard-site.json**: Typical Drupal site with ~50 modules (mix of core, contrib, and custom)
- **large-site.json**: Enterprise Drupal site with 100+ modules
- **schema.json**: JSON Schema for validating the submission structure

### Using Mock Data with Newman

You can use these mock data files for data-driven testing with Newman:

```bash
# Test with minimal dataset
newman run "postman/FastAPI Monitoring Platform.postman_collection.json" \
  --environment postman/FastAPI_Testing_Environment.postman_environment.json \
  --iteration-data examples/drupal-submissions/minimal-site.json

# Test with standard dataset
newman run "postman/FastAPI Monitoring Platform.postman_collection.json" \
  --environment postman/FastAPI_Testing_Environment.postman_environment.json \
  --iteration-data examples/drupal-submissions/standard-site.json
```

### Module Types

The platform recognizes three types of modules:

- **core**: Drupal core modules (e.g., node, user, views)
- **contrib**: Community contributed modules from drupal.org
- **custom**: Site-specific custom modules

### Integration with Drupal

Drupal sites can submit their module information to this monitoring platform using the provided JSON structure. The `token` field in the site object will be used to authenticate and authorize submissions.

## Frontend Development

### Prerequisites
- Node.js 18+ (for local development without Docker)
- Docker and Docker Compose (for containerized development)

### Running Frontend with Docker

1. Start all services including frontend:
```bash
docker-compose up -d
```

2. Access the applications:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

3. View frontend logs:
```bash
docker-compose logs -f frontend
```

4. Rebuild frontend after changes:
```bash
docker-compose build frontend
docker-compose up -d frontend
```

### Production Build

Build the frontend for production:
```bash
docker-compose build --build-arg target=production frontend
```

### Development Commands

- Start only backend services (without frontend):
```bash
docker-compose up -d api db redis celery
```

- Access frontend container shell:
```bash
docker-compose exec frontend sh
```

- Install new frontend dependencies:
```bash
docker-compose exec frontend npm install <package-name>
docker-compose restart frontend
```

### Frontend Environment Variables

The frontend uses the following environment variables:
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000/api/v1)
- `VITE_WS_URL`: WebSocket URL (default: ws://localhost:8000/ws)
- `VITE_APP_NAME`: Application name
- `VITE_APP_VERSION`: Application version

These can be configured in:
- `frontend/.env.development` for development
- `frontend/.env.production` for production
- Docker Compose environment section
EOF < /dev/null