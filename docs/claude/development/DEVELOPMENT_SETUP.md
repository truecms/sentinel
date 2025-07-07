# Development Setup Guide

## Overview
This document covers the complete development environment setup for the FastAPI monitoring platform, including Docker configuration, database initialization, and service management.

## Prerequisites
- Docker and Docker Compose installed
- Git for version control
- Node.js (for Newman/Postman testing)

## Initial Setup

### 1. Clone Repository
```bash
git clone https://github.com/truecms/sentinel.git
cd sentinel
```

### 2. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Key environment variables to configure:
# - POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
# - JWT_SECRET_KEY (generate a secure key)
# - SUPERUSER_EMAIL, SUPERUSER_PASSWORD
```

### 3. Database Initialization
```bash
# Start services
docker-compose up -d

# Create database (required first time only)
docker-compose exec -u postgres db psql -c "CREATE DATABASE application_db;"

# Run database migrations
docker-compose exec api alembic upgrade head
```

## Service Management

### Starting Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d api

# View logs
docker-compose logs -f api

# View all service statuses
docker-compose ps
```

### Stopping Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Rebuilding Services
```bash
# Rebuild after code changes
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build api
```

## Accessing the Application

- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **API Endpoint**: http://localhost:8000
- **Frontend** (if applicable): http://localhost:3000

## Common Development Tasks

### Database Access
```bash
# Connect to PostgreSQL
docker-compose exec -u postgres db psql -d application_db

# Common database commands:
\dt              # List all tables
\d+ table_name   # Describe table structure
\q               # Exit psql
```

### API Container Access
```bash
# Access API container shell
docker-compose exec api bash

# Run Python commands
docker-compose exec api python
```

### Restart Services
```bash
# Restart single service
docker-compose restart api

# Restart all services
docker-compose restart
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs api

# Common fixes:
# 1. Ensure .env file exists
# 2. Check port conflicts: lsof -i :8000
# 3. Rebuild: docker-compose up -d --build
```

### Database Connection Issues
```bash
# Verify database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Ensure database exists
docker-compose exec -u postgres db psql -c "\l"
```

### Migration Failures
```bash
# Check current migration status
docker-compose exec api alembic current

# View migration history
docker-compose exec api alembic history

# Rollback if needed
docker-compose exec api alembic downgrade -1
```

## Best Practices

### DO:
- ✅ Always run migrations after pulling new code
- ✅ Use docker-compose for all services
- ✅ Check logs when debugging issues
- ✅ Keep .env file secure and never commit it

### DON'T:
- ❌ Run services directly without Docker
- ❌ Modify database schema without migrations
- ❌ Commit sensitive environment variables
- ❌ Use production credentials locally

## Related Documentation
- Database Management: `docs/claude/development/DATABASE_MANAGEMENT.md`
- Testing Guide: `docs/claude/development/TESTING.md`
- API Architecture: `docs/claude/architecture/API_DESIGN.md`