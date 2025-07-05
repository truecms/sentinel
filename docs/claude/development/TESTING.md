# Testing Guide

## Overview
This document covers the complete testing strategy for the FastAPI monitoring platform, including unit tests, integration tests, and coverage requirements.

## Test Environment

### Architecture
- **Dedicated test container**: Isolated environment with test database
- **Async test support**: Full async/await testing capability
- **Fixture-based**: Shared test data and authentication
- **Coverage requirements**: 80% minimum with reports

### Test Container Configuration
The test container uses separate credentials to avoid conflicts:
- Database: `test_db`
- User: `test_user`
- Password: `test_password`

## Running Tests

### All Tests
```bash
# Run all tests
docker-compose exec test pytest

# Run with verbose output
docker-compose exec test pytest -v

# Run with captured output (show print statements)
docker-compose exec test pytest -s
```

### Specific Test Files
```bash
# Run specific test file
docker-compose exec test pytest tests/test_api/test_auth.py

# Run multiple test files
docker-compose exec test pytest tests/test_api/test_auth.py tests/test_api/test_users.py
```

### Specific Test Functions
```bash
# Run specific test function
docker-compose exec test pytest tests/test_api/test_auth.py -k test_login

# Run tests matching pattern
docker-compose exec test pytest -k "login or register"

# Exclude tests matching pattern
docker-compose exec test pytest -k "not slow"
```

### Test Coverage
```bash
# Run with coverage report
docker-compose exec test pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
docker-compose exec test pytest --cov=app --cov-report=html

# Generate XML coverage report (for CI)
docker-compose exec test pytest --cov=app --cov-report=xml
```

**Note**: Tests require 80% minimum coverage

## Test Structure

### Directory Layout
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_api/               # API endpoint tests
│   ├── test_auth.py        # Authentication tests
│   ├── test_users.py       # User management tests
│   ├── test_organizations.py # Organization tests
│   └── test_sites.py       # Site management tests
├── test_crud/              # CRUD operation tests
│   ├── test_user_crud.py
│   └── test_org_crud.py
├── test_models/            # Model tests
└── test_utils/             # Utility function tests
```

### Writing Tests

#### Basic Test Example
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, superuser_token_headers):
    """Test creating a new user."""
    response = await client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
```

#### Using Fixtures
```python
@pytest.mark.asyncio
async def test_with_fixtures(
    client: AsyncClient,
    normal_user_token_headers,
    test_organization
):
    """Test using multiple fixtures."""
    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
```

## Common Test Fixtures

### Authentication Fixtures
- `superuser_token_headers`: Headers with superuser JWT token
- `normal_user_token_headers`: Headers with regular user JWT token
- `org_admin_token_headers`: Headers with organization admin JWT token

### Data Fixtures
- `test_user`: Creates a test user
- `test_organization`: Creates a test organization
- `test_site`: Creates a test site

### Client Fixtures
- `client`: Async HTTP client for making requests
- `db`: Async database session

## Testing Best Practices

### DO:
- ✅ Use async/await for all database operations
- ✅ Test both success and failure cases
- ✅ Test permission boundaries
- ✅ Use fixtures for common test data
- ✅ Clean up test data after tests

### DON'T:
- ❌ Use production database for testing
- ❌ Hard-code test data
- ❌ Skip error case testing
- ❌ Leave test data in database

## Debugging Tests

### View Test Output
```bash
# Show print statements
docker-compose exec test pytest -s

# Show local variables on failure
docker-compose exec test pytest -l

# Stop on first failure
docker-compose exec test pytest -x

# Enter debugger on failure
docker-compose exec test pytest --pdb
```

### Check Test Database
```bash
# Connect to test database
docker-compose exec -u postgres db psql -d test_db

# View test data
SELECT * FROM users;
SELECT * FROM organizations;
```

## CI/CD Testing

Tests automatically run in GitHub Actions:
- On every push to main branch
- On every pull request
- Must pass before merging
- Coverage report generated

### Local CI Simulation
```bash
# Run tests as CI would
docker-compose -f docker-compose.yml -f docker-compose.ci.yml up -d
docker-compose exec test pytest --cov=app --cov-report=xml
```

## Performance Testing

### Load Testing
```bash
# Use locust for load testing
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

### Profiling
```bash
# Profile specific endpoints
docker-compose exec test pytest tests/test_api/test_users.py --profile
```

## Troubleshooting

### Tests Won't Run
- Ensure test container is running: `docker-compose ps test`
- Check test database exists: `docker-compose exec -u postgres db psql -c "\l"`
- Verify migrations ran: `docker-compose exec test alembic current`

### Import Errors
- Check PYTHONPATH: Should include `/app`
- Verify all dependencies installed
- Rebuild test container: `docker-compose build test`

### Database Errors
- Test database might be corrupted
- Reset: `docker-compose down -v && docker-compose up -d`

## Related Documentation
- Development Setup: `docs/claude/development/DEVELOPMENT_SETUP.md`
- Database Management: `docs/claude/development/DATABASE_MANAGEMENT.md`
- CI/CD Configuration: `.github/workflows/`