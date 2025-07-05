# Postman Testing Guide

## Overview
This document covers the Postman collection testing strategy for the FastAPI monitoring platform, including local testing, CI/CD integration, and data-driven testing.

## Collection Structure

### Current Collections
- **Main Collection**: `postman/FastAPI Monitoring Platform.postman_collection.json`
- **Environment File**: `postman/FastAPI_Testing_Environment.postman_environment.json`
- **Legacy Collection**: `postman/FastAPI_Testing_Collection.json` (deprecated)

### Collection Contents
The main collection includes:
- Authentication workflow (login, token management)
- User management endpoints (CRUD operations)
- Organization management endpoints
- Site management endpoints
- Module submission endpoints
- Comprehensive error handling tests

## Running Tests Locally

### Prerequisites
```bash
# Install Newman CLI
npm install -g newman

# Or use npx (no installation needed)
npx newman run ...
```

### Basic Test Run
```bash
# Run the main API testing collection
newman run "postman/FastAPI Monitoring Platform.postman_collection.json" \
  --environment postman/FastAPI_Testing_Environment.postman_environment.json \
  --reporters cli,json \
  --reporter-json-export postman-results.json
```

### Docker Alternative
```bash
# Run with Docker if Newman is not installed
docker run --rm -v $(pwd)/postman:/etc/newman \
  postman/newman run "FastAPI Monitoring Platform.postman_collection.json" \
  --environment FastAPI_Testing_Environment.postman_environment.json
```

## Environment Configuration

### Key Environment Variables
```json
{
  "baseUrl": "http://localhost:8000",      // API base URL
  "adminEmail": "admin@example.com",        // Admin credentials
  "adminPassword": "admin123",
  "authToken": "",                          // Auto-populated by login
  "testUserId": "",                         // Auto-populated during tests
  "testOrgId": "",                          // Auto-populated during tests
  "testSiteId": ""                          // Auto-populated during tests
}
```

### Dynamic Variables
The collection automatically manages these variables:
- `{{authToken}}`: JWT token from login
- `{{testUserId}}`: Created user's ID
- `{{testOrgId}}`: Created organization's ID
- `{{testSiteId}}`: Created site's ID

## Token Management

### Automatic Token Handling
```javascript
// In login request's Test tab
const response = pm.response.json();
if (response.access_token) {
    pm.environment.set("authToken", response.access_token);
}
```

### Token Usage
All authenticated requests automatically include:
```
Authorization: Bearer {{authToken}}
```

### Token Expiration
- Default expiration: 30 minutes
- Re-run login request to refresh
- Consider implementing auto-refresh in pre-request scripts

## Data-Driven Testing

### Using Mock Data Files
Newman supports data-driven testing using external JSON files, particularly useful for testing bulk operations.

#### Running with Mock Data
```bash
# Test with minimal dataset
newman run "postman/FastAPI Monitoring Platform.postman_collection.json" \
  --environment postman/FastAPI_Testing_Environment.postman_environment.json \
  --iteration-data examples/drupal-submissions/minimal-site.json

# Test with standard dataset (~50 modules)
newman run "postman/FastAPI Monitoring Platform.postman_collection.json" \
  --environment postman/FastAPI_Testing_Environment.postman_environment.json \
  --iteration-data examples/drupal-submissions/standard-site.json

# Test with large dataset (100+ modules)
newman run "postman/FastAPI Monitoring Platform.postman_collection.json" \
  --environment postman/FastAPI_Testing_Environment.postman_environment.json \
  --iteration-data examples/drupal-submissions/large-site.json
```

### Mock Data Structure
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
- **minimal-site.json**: Basic Drupal site (5-10 modules)
- **standard-site.json**: Typical Drupal site (~50 modules)
- **large-site.json**: Enterprise Drupal site (100+ modules)
- **schema.json**: JSON Schema for validation

## Writing Postman Tests

### Basic Test Example
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('data');
    pm.expect(jsonData).to.have.property('meta');
});
```

### Advanced Testing
```javascript
// Test response time
pm.test("Response time is less than 500ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

// Test array contents
pm.test("All users have required fields", function () {
    const users = pm.response.json().data;
    users.forEach(user => {
        pm.expect(user).to.have.property('id');
        pm.expect(user).to.have.property('email');
        pm.expect(user).to.have.property('is_active');
    });
});

// Store data for next request
const response = pm.response.json();
if (response.data && response.data.id) {
    pm.environment.set("lastCreatedId", response.data.id);
}
```

### Pre-request Scripts
```javascript
// Generate random data
pm.variables.set("randomEmail", `test${Date.now()}@example.com`);
pm.variables.set("randomName", `Test User ${Date.now()}`);

// Access iteration data
if (pm.iterationData.has("site")) {
    const siteData = pm.iterationData.get("site");
    pm.variables.set("siteUrl", siteData.url);
}
```

## CI/CD Integration

### GitHub Actions Workflow
The collection runs automatically in CI:
```yaml
- name: Run Postman Collection
  run: newman run "postman/FastAPI_Monitoring_Updated.postman_collection.json" \
    -e postman/FastAPI_Testing_Environment.postman_environment.json
```

### CI Test Reports
```bash
# Generate multiple report formats
newman run collection.json \
  --reporters cli,json,html \
  --reporter-json-export results.json \
  --reporter-html-export results.html
```

## When to Update Collections

Update the Postman collection when:

1. **New API endpoints are added**
   - Add corresponding requests
   - Include positive and negative test cases

2. **Request/response schemas change**
   - Update request bodies
   - Adjust test assertions

3. **Authentication flow changes**
   - Modify login procedures
   - Update token handling

4. **Environment variables change**
   - Add new variables to environment
   - Update variable usage in requests

5. **API versioning updates**
   - Ensure URLs use correct version
   - Update version headers if needed

## Troubleshooting

### Common Issues

#### Connection Refused
```bash
# Ensure services are running
docker-compose up -d

# Check service health
docker-compose ps
```

#### Authentication Failed
- Verify credentials in environment file
- Check token expiration
- Ensure login request runs first

#### 404 Errors
- Verify endpoint URLs match current routes
- Check API version in URLs
- Ensure required path parameters are set

#### Schema Validation Errors
- Update request bodies to match Pydantic schemas
- Check required vs optional fields
- Verify data types

### Debug Tips

#### Verbose Output
```bash
# Show detailed request/response info
newman run collection.json -e environment.json --verbose
```

#### Inspect Variables
```javascript
// In test scripts
console.log("Current token:", pm.environment.get("authToken"));
console.log("All variables:", pm.variables.toObject());
```

#### Export Results
```bash
# Export detailed results for analysis
newman run collection.json \
  --reporters json \
  --reporter-json-export detailed-results.json
```

## Best Practices

### Collection Organization
- ✅ Group related requests in folders
- ✅ Use descriptive request names
- ✅ Order requests logically
- ✅ Clean up test data after tests

### Test Writing
- ✅ Test both success and error cases
- ✅ Validate response structure
- ✅ Check response times
- ✅ Use meaningful test names

### Environment Management
- ✅ Use initial values for defaults
- ✅ Clear sensitive data after tests
- ✅ Document all variables
- ✅ Version control environment files

### Maintenance
- ✅ Keep collections in sync with API
- ✅ Run tests before committing
- ✅ Update mock data regularly
- ✅ Review and refactor tests

## Updating Process

1. **Make API changes** in FastAPI
2. **Test manually** with Postman GUI
3. **Update collection**:
   - Add/modify requests
   - Update test assertions
   - Adjust pre-request scripts
4. **Export collection** from Postman
5. **Replace file** in `postman/` directory
6. **Update environment** if needed
7. **Test with Newman** locally
8. **Update mock data** if schemas changed
9. **Commit and push** to trigger CI

## Related Documentation
- API Design: `docs/claude/architecture/API_DESIGN.md`
- Authentication: `docs/claude/api/AUTHENTICATION.md`
- Testing Guide: `docs/claude/development/TESTING.md`