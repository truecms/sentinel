# Troubleshooting Guide

## Overview
This document provides solutions to common issues encountered when developing and deploying the FastAPI monitoring platform.

## Development Environment Issues

### Docker Container Issues

#### Container Won't Start
```bash
# Check logs for specific service
docker-compose logs api
docker-compose logs db

# Common fixes:
# 1. Ensure .env file exists
cp .env.example .env

# 2. Check port conflicts
lsof -i :8000  # API port
lsof -i :5432  # Database port

# 3. Rebuild containers
docker-compose down
docker-compose up -d --build
```

#### Container Keeps Restarting
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs --tail=100 api

# Common causes:
# - Missing environment variables
# - Database connection failures
# - Python syntax errors
```

### Database Connection Issues

#### "Connection refused" Error
```bash
# Verify database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec -u postgres db psql -c "\l"

# Ensure correct environment variables
echo $POSTGRES_HOST  # Should be "db" in Docker
```

#### "Database does not exist" Error
```bash
# Note: The app uses 'postgres' database by default
# NOT 'application_db' as some docs may suggest

# Verify database exists
docker-compose exec -u postgres db psql -c "\l"

# If using custom database, create it:
docker-compose exec -u postgres db psql -c "CREATE DATABASE mydb;"
```

### Migration Issues

#### "Duplicate table" Error During Migrations
**Cause**: app/main.py has `Base.metadata.create_all()` conflicting with Alembic

**Solution**:
```python
# Remove from app/main.py:
# Base.metadata.create_all(bind=engine)  # DELETE THIS LINE
```

#### Circular Foreign Key Dependencies
**Cause**: Organizations table references users for audit fields

**Solution**: In migration file, comment out circular FKs:
```python
# Comment these out in the migration:
# op.create_foreign_key(None, 'organizations', 'users', ['created_by'], ['id'])
# op.create_foreign_key(None, 'organizations', 'users', ['updated_by'], ['id'])
```

#### Migration Not Found
```bash
# Check current migration
docker-compose exec api alembic current

# View migration history
docker-compose exec api alembic history

# Force to specific revision (careful!)
docker-compose exec api alembic stamp head
```

## API Issues

### Authentication Errors

#### 401 Unauthorized
```python
# Common causes:
# 1. Missing Authorization header
# 2. Expired token
# 3. Invalid token format

# Debug token:
import jwt
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    print(f"Token expires: {payload.get('exp')}")
except jwt.ExpiredSignatureError:
    print("Token has expired")
except jwt.InvalidTokenError:
    print("Invalid token")
```

#### 403 Forbidden
```python
# User authenticated but lacks permissions
# Check:
# - Is user a superuser?
# - Is user member of organization?
# - Is user admin of organization?
```

### Request Validation Errors

#### 422 Unprocessable Entity
```json
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "invalid email format",
            "type": "value_error.email"
        }
    ]
}
```

**Common fixes**:
- Check required vs optional fields
- Verify data types match schema
- Ensure enum values are valid

### Performance Issues

#### Slow API Responses
```python
# Enable SQL logging to find slow queries
# In .env:
LOG_LEVEL=DEBUG

# Check for N+1 queries
# Use eager loading:
query = select(User).options(selectinload(User.organizations))
```

#### Connection Pool Exhaustion
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND state_change < current_timestamp - INTERVAL '10 minutes';
```

## Testing Issues

### Test Database Errors

#### Tests Failing with Database Errors
```bash
# Reset test database
docker-compose down -v
docker-compose up -d

# Verify test database
docker-compose exec -u postgres db psql -c "\l" | grep test_db
```

#### Import Errors in Tests
```bash
# Check PYTHONPATH
docker-compose exec test echo $PYTHONPATH  # Should include /app

# Rebuild test container
docker-compose build test
```

### Coverage Issues

#### Coverage Below 80%
```bash
# Generate detailed coverage report
docker-compose exec test pytest --cov=app --cov-report=html

# View uncovered lines
docker-compose exec test pytest --cov=app --cov-report=term-missing
```

## CI/CD Issues

### GitHub Actions Failures

#### Database Creation Fails
```yaml
# In .github/workflows/postman-tests.yml
# Remove database creation - app uses 'postgres' DB:
# - name: Create application database
#   run: |
#     echo "Database 'postgres' already exists"
```

#### Migrations Fail in CI
Check startup order:
1. Database must be ready
2. Run migrations
3. Run ensure_superuser.py
4. Start API

### Postman Test Failures

#### Connection Refused
```bash
# Ensure API is accessible
curl http://localhost:8000/health

# Check Docker network
docker network ls
docker network inspect monitoring_app-network
```

#### Token Expiration in Long Test Runs
```javascript
// Add token refresh in Postman pre-request:
if (pm.environment.get("tokenExpiry") < Date.now()) {
    // Re-authenticate
    pm.sendRequest({
        url: pm.environment.get("baseUrl") + "/auth/login",
        method: "POST",
        // ... login details
    });
}
```

## Production Issues

### Memory Leaks
```python
# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024} MB")

# Common causes:
# - Unclosed database sessions
# - Large query results not paginated
# - Circular references in models
```

### High CPU Usage
```bash
# Profile the application
docker-compose exec api py-spy top --pid 1

# Common causes:
# - Inefficient queries
# - Missing database indexes
# - Synchronous operations in async code
```

## Quick Fixes Reference

### Reset Everything
```bash
# Complete reset (loses all data)
docker-compose down -v
docker-compose up -d --build
docker-compose exec api alembic upgrade head
```

### Fix Common Startup Issues
```bash
# 1. Check environment
cat .env

# 2. Verify services
docker-compose ps

# 3. Check logs
docker-compose logs --tail=50

# 4. Restart services
docker-compose restart
```

### Debug Database Issues
```bash
# Connect to database
docker-compose exec -u postgres db psql postgres

# Common queries:
\dt                    # List tables
\d+ users             # Describe table
SELECT * FROM users;  # View data
```

## Getting Help

### Logs to Collect
When reporting issues, include:
1. `docker-compose logs --tail=100`
2. Environment details: `docker-compose config`
3. Migration status: `docker-compose exec api alembic current`
4. Error messages and stack traces

### Debug Mode
Enable debug logging:
```bash
# In .env
LOG_LEVEL=DEBUG
DEBUG=True
```

## Related Documentation
- Development Setup: `docs/claude/development/DEVELOPMENT_SETUP.md`
- Database Management: `docs/claude/development/DATABASE_MANAGEMENT.md`
- Testing Guide: `docs/claude/development/TESTING.md`