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

### Running Tests
```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# Coverage report
pytest --cov=app tests/
```

### Performance Testing
```bash
# Load testing
locust -f tests/performance/locustfile.py

# Benchmark specific endpoint
pytest tests/performance/test_endpoints.py
```

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
