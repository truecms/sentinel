# Data Ingestion Endpoint Documentation

## Overview

The data ingestion endpoint allows Drupal sites to synchronize their module information with the monitoring platform. This endpoint includes performance optimizations, rate limiting, and support for both partial and full synchronization modes.

## Endpoint

`POST /api/v1/sites/{site_id}/modules`

## Features

### 1. Rate Limiting
- **Limit**: 4 requests per hour per site
- **Headers**: Rate limit information is included in response headers
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining in current window
  - `X-RateLimit-Reset`: Unix timestamp when the rate limit resets
  - `Retry-After`: Seconds to wait before retrying (only on 429 responses)

### 2. Caching
- Module lookups are cached in Redis for 1 hour
- Version lookups are cached for 24 hours
- Significantly reduces database load for repeated syncs

### 3. Background Processing
- Payloads with more than 500 modules are automatically processed in the background
- Returns a 202 Accepted status with a task ID
- Task status can be checked at `/api/v1/tasks/{task_id}/status`

### 4. Full vs Partial Sync
- **Partial Sync** (`full_sync: false`): Only updates modules present in the payload
- **Full Sync** (`full_sync: true`): Removes modules not present in the payload

## Request Format

```json
{
  "site": {
    "url": "https://example.drupal.site",
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
      "version": "10.3.8",
      "description": "Create customized lists and queries from your database."
    }
  ],
  "full_sync": false  // Optional, defaults to false
}
```

## Response Formats

### Synchronous Response (< 500 modules)

```json
{
  "site_id": 123,
  "modules_processed": 150,
  "modules_created": 5,
  "modules_updated": 20,
  "modules_unchanged": 125,
  "errors": [],
  "message": "Successfully synced 150 modules"
}
```

### Asynchronous Response (> 500 modules)

```json
{
  "status": "accepted",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Sync of 750 modules queued for processing",
  "status_url": "/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/status"
}
```

### Rate Limit Error Response

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

## Task Status Endpoint

`GET /api/v1/tasks/{task_id}/status`

### Response Examples

#### Task Pending
```json
{
  "status": "pending",
  "message": "Task is pending execution"
}
```

#### Task In Progress
```json
{
  "status": "in_progress",
  "progress": {
    "current": 250,
    "total": 750,
    "status": "Processed 250/750 modules"
  }
}
```

#### Task Completed
```json
{
  "status": "completed",
  "result": {
    "site_id": 123,
    "modules_processed": 750,
    "modules_created": 50,
    "modules_updated": 100,
    "modules_unchanged": 600,
    "errors": [],
    "message": "Successfully synced 750 modules",
    "completed_at": 1640995200
  }
}
```

## Usage Examples

### Example 1: Small Site Partial Sync

```bash
curl -X POST https://api.example.com/api/v1/sites/123/modules \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "site": {
      "url": "https://small-site.com",
      "name": "Small Site",
      "token": "site-token"
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
  }'
```

### Example 2: Large Site with Background Processing

```bash
# Initial request
curl -X POST https://api.example.com/api/v1/sites/456/modules \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @large-site-modules.json

# Response: {"status": "accepted", "task_id": "abc123", ...}

# Check status
curl -X GET https://api.example.com/api/v1/tasks/abc123/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example 3: Full Sync with Module Removal

```bash
curl -X POST https://api.example.com/api/v1/sites/789/modules \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "site": { ... },
    "drupal_info": { ... },
    "modules": [ ... ],
    "full_sync": true
  }'
```

## Best Practices

1. **Use Full Sync Periodically**: Run a full sync daily or weekly to ensure removed modules are detected
2. **Handle Rate Limits**: Implement exponential backoff when receiving 429 responses
3. **Monitor Task Status**: For large syncs, poll the task status endpoint until completion
4. **Batch Module Updates**: Group module updates to minimize the number of sync requests
5. **Validate Site URL**: Ensure the site URL in the payload matches the registered site

## Performance Considerations

- **Caching**: First sync may be slower as caches are populated
- **Indexes**: Database indexes optimize lookups for machine_name, version strings, and site associations
- **Batch Processing**: Modules are processed in batches of 100 in background tasks
- **Memory Usage**: Background tasks are configured to handle up to 500MB per request

## Error Handling

Common error scenarios:

1. **Site Not Found** (404): The site_id doesn't exist
2. **Forbidden** (403): User doesn't have access to the site's organization
3. **Bad Request** (400): Site URL mismatch or invalid data
4. **Rate Limit** (429): Too many requests in the current window
5. **Server Error** (500): Database or internal errors

Always check the response status and handle errors appropriately in your Drupal module.