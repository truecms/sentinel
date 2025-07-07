# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based monitoring and reporting platform providing REST API endpoints for user, organization, and site management with role-based access control (RBAC).

## Repository Information

- Github repository for this project: https://github.com/truecms/sentinel

## 📚 Documentation Index

### Development
- **Setup Guide**: `docs/claude/development/DEVELOPMENT_SETUP.md` - Environment setup, Docker configuration
- **Testing Guide**: `docs/claude/development/TESTING.md` - Unit tests, integration tests, coverage
- **Database Management**: `docs/claude/development/DATABASE_MANAGEMENT.md` - Migrations, PostgreSQL operations

### Architecture
- **API Design**: `docs/claude/architecture/API_DESIGN.md` - Design patterns, structure, best practices
- **Authentication**: `docs/claude/api/AUTHENTICATION.md` - JWT, Drupal site auth, RBAC

### Tools
- **Postman Testing**: `docs/claude/tools/POSTMAN_TESTING.md` - Newman, collections, CI/CD integration

### Troubleshooting
- **Common Issues**: `docs/claude/troubleshooting/COMMON_ISSUES.md` - Solutions to frequent problems

## Quick Start

```bash
# Start services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Access API documentation
# http://localhost:8000/docs
```

## Key Points

### Database
- Uses `postgres` database (NOT `application_db`)
- Alembic handles all migrations
- No manual table creation

### Authentication
- JWT tokens for users
- Site UUID + API Token for Drupal sites
- Module data only from authenticated sites

### Testing
- 80% minimum coverage required
- Dedicated test container
- Postman collection for API testing

## Common Pitfalls

1. **Database initialization**: The app uses the default `postgres` database
2. **Circular dependencies**: Comment out circular FKs in migrations
3. **Table creation conflicts**: Don't use `Base.metadata.create_all()`
4. **Module creation**: Only via authenticated Drupal site submissions

## Environment Variables

Key variables (see `.env.example`):
- `POSTGRES_DB=postgres` (default database)
- `JWT_SECRET_KEY` (generate secure key)
- `SUPERUSER_EMAIL/PASSWORD` (initial admin)