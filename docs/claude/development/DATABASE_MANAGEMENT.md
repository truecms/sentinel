# Database Management Guide

## Overview
This document covers database management for the FastAPI monitoring platform, including migrations, direct database access, and troubleshooting.

## Database Architecture

### Technology Stack
- **PostgreSQL**: Primary database
- **SQLAlchemy**: Async ORM
- **Alembic**: Database migrations
- **Redis**: Caching and rate limiting

### Database Configuration
- Default database: `postgres` (Note: NOT `application_db`)
- Connection pooling enabled
- Async operations throughout

## Alembic Migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
docker-compose exec api alembic revision --autogenerate -m "Add new field to users table"

# Create empty migration for manual changes
docker-compose exec api alembic revision -m "Custom database changes"
```

### Applying Migrations

```bash
# Apply all pending migrations
docker-compose exec api alembic upgrade head

# Apply to specific revision
docker-compose exec api alembic upgrade +1

# Apply up to specific revision
docker-compose exec api alembic upgrade ae1234
```

### Rolling Back Migrations

```bash
# Rollback one migration
docker-compose exec api alembic downgrade -1

# Rollback to specific revision
docker-compose exec api alembic downgrade ae1234

# Rollback all migrations (careful!)
docker-compose exec api alembic downgrade base
```

### Migration Management

```bash
# View current migration
docker-compose exec api alembic current

# View migration history
docker-compose exec api alembic history

# View detailed migration history
docker-compose exec api alembic history --verbose
```

## Direct Database Access

### PostgreSQL CLI Access

```bash
# Connect to database
docker-compose exec -u postgres db psql -d postgres

# Connect to test database
docker-compose exec -u postgres db psql -d test_db
```

### Common PostgreSQL Commands

```sql
-- List all tables
\dt

-- Describe table structure
\d+ users
\d+ organizations

-- List all databases
\l

-- Switch database
\c database_name

-- View table indexes
\di

-- View table constraints
\d+ table_name

-- Exit psql
\q
```

### Useful Queries

```sql
-- Count records by table
SELECT schemaname,tablename,n_live_tup 
FROM pg_stat_user_tables 
ORDER BY n_live_tup DESC;

-- View active connections
SELECT pid, usename, application_name, client_addr, state 
FROM pg_stat_activity 
WHERE state = 'active';

-- Database size
SELECT pg_database.datname,
       pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database;

-- Table sizes
SELECT
    schemaname AS table_schema,
    tablename AS table_name,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Database Models

### Base Model
All models inherit from `BaseModel` providing:
- `id`: UUID primary key
- `created_at`: Timestamp of creation
- `created_by`: User who created the record
- `updated_at`: Timestamp of last update
- `updated_by`: User who last updated
- `is_active`: Soft delete flag

### Model Relationships
```python
# One-to-Many
organization.users  # All users in organization
user.organizations  # All organizations user belongs to

# Many-to-Many (through association table)
user.sites  # Sites user has access to
site.users  # Users with access to site
```

## Database Operations

### Backup Database

```bash
# Backup entire database
docker-compose exec -u postgres db pg_dump postgres > backup.sql

# Backup specific tables
docker-compose exec -u postgres db pg_dump postgres -t users -t organizations > partial_backup.sql

# Compressed backup
docker-compose exec -u postgres db pg_dump postgres | gzip > backup.sql.gz
```

### Restore Database

```bash
# Restore from backup
docker-compose exec -u postgres db psql postgres < backup.sql

# Restore compressed backup
gunzip -c backup.sql.gz | docker-compose exec -T -u postgres db psql postgres
```

### Database Maintenance

```bash
# Analyze database for query optimization
docker-compose exec -u postgres db psql -d postgres -c "ANALYZE;"

# Vacuum database (clean up dead rows)
docker-compose exec -u postgres db psql -d postgres -c "VACUUM;"

# Full vacuum (locks tables, use carefully)
docker-compose exec -u postgres db psql -d postgres -c "VACUUM FULL;"
```

## Common Issues and Solutions

### Migration Conflicts

**Problem**: Migration fails due to conflicting changes
```bash
# Check current state
docker-compose exec api alembic current

# See pending migrations
docker-compose exec api alembic history

# Force to specific revision (data loss possible!)
docker-compose exec api alembic stamp head
```

### Circular Dependencies

**Problem**: Foreign key circular dependencies
```python
# In migration file, comment out circular FKs:
# op.create_foreign_key(None, 'organizations', 'users', ['created_by'], ['id'])
```

### Connection Pool Exhaustion

**Problem**: "Too many connections" error
```bash
# Check active connections
docker-compose exec -u postgres db psql -c "SELECT count(*) FROM pg_stat_activity;"

# Kill idle connections
docker-compose exec -u postgres db psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < current_timestamp - INTERVAL '10 minutes';"
```

### Database Locks

**Problem**: Migration or query hanging
```sql
-- Find blocking queries
SELECT blocked_locks.pid AS blocked_pid,
       blocked_activity.usename AS blocked_user,
       blocking_locks.pid AS blocking_pid,
       blocking_activity.usename AS blocking_user,
       blocked_activity.query AS blocked_statement,
       blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Kill blocking process
SELECT pg_terminate_backend(pid);
```

## Performance Optimization

### Indexes
```sql
-- Check missing indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND indexname NOT LIKE 'pg_toast%'
ORDER BY schemaname, tablename;

-- Create index
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_organizations_created_at ON organizations(created_at);
```

### Query Analysis
```sql
-- Enable query timing
\timing

-- Explain query plan
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- View slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Best Practices

### DO:
- ✅ Always use migrations for schema changes
- ✅ Test migrations locally before applying to production
- ✅ Keep migrations small and focused
- ✅ Use meaningful migration messages
- ✅ Backup before major changes

### DON'T:
- ❌ Modify database schema directly
- ❌ Use `Base.metadata.create_all()` in production
- ❌ Delete migration files after applying
- ❌ Share database between environments
- ❌ Use synchronous operations with async code

## Related Documentation
- Development Setup: `docs/claude/development/DEVELOPMENT_SETUP.md`
- Testing Guide: `docs/claude/development/TESTING.md`
- API Architecture: `docs/claude/architecture/API_DESIGN.md`