# Authentication & Authorization Guide

## Overview
This document describes the authentication and authorization patterns used in the FastAPI monitoring platform, with special focus on how Drupal sites authenticate.

## Authentication Methods

### 1. User Authentication (JWT)
Standard JWT-based authentication for web users and API access.

#### Login Flow
```python
# POST /api/v1/auth/login
{
    "email": "user@example.com",
    "password": "secure_password"
}

# Response
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer"
}
```

#### Using the Token
```bash
# Include in Authorization header
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
     http://localhost:8000/api/v1/users/me
```

### 2. Drupal Site Authentication
Special authentication pattern for Drupal sites to submit module data.

#### How Drupal Sites Authenticate
Drupal sites authenticate using a combination of:
1. **Site UUID**: A unique identifier for the site (generated when site is created)
2. **API Token**: A secure token specific to that site

#### Authentication Flow
1. Site administrator creates/updates a site in the monitoring system
2. System generates a Site UUID and API Token for that site
3. Administrator copies both values to their Drupal site configuration
4. Drupal module uses these credentials to authenticate when sending data

#### Example Site Authentication
```python
# Drupal sends this header
headers = {
    "X-Site-UUID": "550e8400-e29b-41d4-a716-446655440000",
    "X-API-Token": "sk_live_abcdef123456..."
}

# POST /api/v1/modules/
{
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

### Important Authentication Notes
- **No superuser override**: Module creation is ONLY done through authenticated site submissions
- **No manual module entry**: Modules cannot be created manually by users, only through Drupal site payloads
- **Site-specific tokens**: Each site has its own unique authentication credentials
- **Module endpoint authentication**: The `/api/v1/modules/` POST endpoint uses the same site UUID + API token authentication

## Authorization Levels

### Role-Based Access Control (RBAC)

#### 1. Superuser
- Full system access
- Can create/manage organizations
- Can view all data
- Can manage users
- Cannot manually create modules (must come from sites)

```python
# Dependency for superuser-only endpoints
async def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403)
    return current_user
```

#### 2. Organization Admin
- Manage their organization
- Create/manage sites within organization
- View organization data
- Manage organization users

```python
# Check if user is org admin
def is_organization_admin(user: User, org: Organization) -> bool:
    membership = get_membership(user, org)
    return membership and membership.role == "admin"
```

#### 3. Regular User
- Access assigned resources only
- View data for assigned sites
- Limited to read operations

## JWT Token Details

### Token Structure
```python
# Token payload
{
    "sub": "user@example.com",  # Subject (user email)
    "exp": 1234567890,          # Expiration timestamp
    "iat": 1234567890,          # Issued at timestamp
    "user_id": "550e8400..."    # User UUID
}
```

### Token Configuration
```python
# Environment variables
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Token lifetime
JWT_SECRET_KEY=your-secret-key  # Signing key
```

### Token Validation
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await crud.user.get_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user
```

## Permission Patterns

### Resource-Level Permissions
```python
# Check if user can access organization
async def verify_organization_access(
    user: User,
    organization_id: UUID,
    db: AsyncSession
) -> Organization:
    org = await crud.organization.get(db, id=organization_id)
    if not org:
        raise HTTPException(status_code=404)
    
    if not user.is_superuser:
        # Check membership
        if not is_member(user, org):
            raise HTTPException(status_code=403)
    
    return org
```

### Operation-Level Permissions
```python
# Create site - requires org admin or superuser
@router.post("/sites/")
async def create_site(
    site_in: SiteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org = await verify_organization_access(
        current_user, site_in.organization_id, db
    )
    
    if not current_user.is_superuser:
        if not is_organization_admin(current_user, org):
            raise HTTPException(
                status_code=403,
                detail="Only organization admins can create sites"
            )
    
    return await crud.site.create(db, obj_in=site_in)
```

## Module Data Flow

### Drupal to API Flow
```
Drupal Site (with UUID + Token) 
    → POST /api/v1/modules/ (with array of modules)
    → System validates site credentials
    → Creates/updates modules and versions
```

### Important Notes
- The `/api/v1/modules/` endpoint ALWAYS accepts an array of modules
- No Drupal site exists with only one module
- Modules are tied to the authenticated site
- Module versions are tracked automatically

## Security Best Practices

### Token Security
- ✅ Use HTTPS in production
- ✅ Short token expiration times
- ✅ Secure token storage on client
- ✅ Rotate secrets regularly

### Password Security
- ✅ Bcrypt hashing with salt
- ✅ Minimum password requirements
- ✅ No password in responses

### API Security
- ✅ Rate limiting per user
- ✅ Request validation
- ✅ CORS configuration
- ✅ SQL injection prevention

## Common Authentication Errors

### 401 Unauthorized
- Missing token
- Expired token
- Invalid token format

### 403 Forbidden
- Valid token but insufficient permissions
- Trying to access other organization's data
- Non-admin trying admin operations

### Example Error Response
```json
{
    "detail": "Could not validate credentials",
    "status_code": 401,
    "type": "unauthorized"
}
```

## Testing Authentication

### Get Token for Testing
```python
# In tests
async def get_superuser_token_headers(client: AsyncClient) -> Dict:
    login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Test Different Roles
```python
# Test as regular user
headers = await get_normal_user_token_headers(client)

# Test as org admin
headers = await get_org_admin_token_headers(client)

# Test as superuser
headers = await get_superuser_token_headers(client)
```

## Related Documentation
- API Design: `docs/claude/architecture/API_DESIGN.md`
- Testing Guide: `docs/claude/development/TESTING.md`
- Security Configuration: `app/core/security.py`