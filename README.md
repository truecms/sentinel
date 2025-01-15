# FastAPI Backend Service

## Overview
Backend service providing REST API endpoints for user, organization, and site management with role-based access control.

## Table of Contents
- [Features](#features)
- [API Documentation](#api-documentation)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features
- User Management with RBAC
- Organization Management
- Site Management
- JWT Authentication
- Rate Limiting
- API Versioning
- Automated Testing
- Docker Deployment

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

3. Start services:
```bash
docker-compose up -d
```

4. Run migrations:
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
