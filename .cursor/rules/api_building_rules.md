API Building Approach and Project Rules
========================================

1. Overview
-----------
This document outlines the guiding principles for building the API for the Monitoring and Reporting Platform. It defines the structure of the API endpoints, business logic for data retrieval and persistence, error handling, security controls, and performance considerations.

2. Design Principles
--------------------
- RESTful Design: Use standard HTTP methods (GET, POST, PUT, DELETE) to operate on well-defined resources.
- Consistent Naming and Versioning: All endpoints are prefixed with /api/v1/ for versioning and backward compatibility.
- Standard Response Envelope: Responses include "data", "meta", and "links" sections for consistency.
- Asynchronous Operations: Leverage FastAPI's async capabilities for high throughput.
- Modular Architecture: Separate endpoints (controllers), business logic (services), and data access (models).

3. API Endpoints and Logic
---------------------------

A. User Management
   ----------------
   - POST /api/v1/users/add
     * Purpose: Create a new user.
     * Logic: Validate input; ensure email uniqueness; hash password (bcrypt/passlib); assign default role; persist the user; associate with an organization.

   - GET /api/v1/users/{user_id}
     * Purpose: Retrieve detailed user information.
     * Logic: Query Users table with joins to Organizations and Roles; return data in the response envelope.

   - PUT /api/v1/users/update/{user_id}
     * Purpose: Update user details.
     * Logic: Validate input and potential conflicts, update user fields, refresh timestamps, and save changes.

   - DELETE /api/v1/users/delete/{user_id}
     * Purpose: Soft-delete a user.
     * Logic: Mark user record as deleted (is_deleted = TRUE) while preserving historical data.

B. Authentication
   -----------------
   - POST /api/v1/auth/login
     * Purpose: Authenticate user credentials and generate a JWT token.
     * Logic: Validate credentials; compare hashed password; generate and return a JWT with an expiry.

   - POST /api/v1/auth/logout
     * Purpose: Log out a user.
     * Logic: (For stateless JWT, log the event if needed and instruct client to remove token.)

C. Organization Management
   --------------------------
   - POST /api/v1/organizations
     * Purpose: Create a new organization.
     * Logic: Validate organization data; check for unique name; record creator details; save organization with timestamps.

   - GET /api/v1/organizations
     * Purpose: Retrieve a list of organizations (with pagination).
     * Logic: Query Organizations table; apply pagination filters; return results with meta information.

   - GET /api/v1/organizations/{org_id}
     * Purpose: Retrieve detailed information for a specific organization.
     * Logic: Fetch organization record by ID; include relevant associated data if necessary.

   - PUT /api/v1/organizations/{org_id}
     * Purpose: Update organization details.
     * Logic: Validate input; update fields; log modification details; save changes.

   - DELETE /api/v1/organizations/{org_id}
     * Purpose: Soft-delete an organization.
     * Logic: Mark organization as deleted; cascade deactivation for related users and sites.

D. Site Management
   -----------------
   - POST /api/v1/sites
     * Purpose: Register a new site.
     * Logic: Validate site details; enforce URL uniqueness; link site to an organization; persist site record.

   - GET /api/v1/sites
     * Purpose: Retrieve a list of sites (optionally by organization) with pagination.
     * Logic: Query Sites table; filter as necessary; return paginated data.

   - GET /api/v1/sites/{site_id}
     * Purpose: Retrieve detailed information for a specific site.
     * Logic: Fetch site record by ID and include additional site information.

   - PUT /api/v1/sites/{site_id}
     * Purpose: Update site details.
     * Logic: Validate updates; update fields and timestamps; persist modifications.

   - DELETE /api/v1/sites/{site_id}
     * Purpose: Soft-delete a site.
     * Logic: Mark the site record as deleted to retain historical data.

E. Module Management
   --------------------
   - POST /api/v1/sites/{site_id}/modules
     * Purpose: Upload module version data from a Drupal site.
     * Logic: Parse JSON payload; validate module names, versions, and update flags; update or insert records in Site Modules and Module Versions tables.

   - GET /api/v1/sites/{site_id}/modules
     * Purpose: Retrieve current module data for a site.
     * Logic: Join Site Modules with Modules and Module Versions; return consolidated module information.

   - GET /api/v1/modules/{module_id}/versions
     * Purpose: Retrieve historical version data for a module.
     * Logic: Query Module Versions table for records matching the module_id.

F. Patch Run Management
   -----------------------
   - POST /api/v1/sites/{site_id}/patch-run
     * Purpose: Record a patch run cycle detailing module updates.
     * Logic: Log patch run details with timestamps into the Patch Runs table.

   - GET /api/v1/sites/{site_id}/patch-run
     * Purpose: Retrieve historical patch run records.
     * Logic: Query Patch Runs table by site_id with optional filters for analysis.

G. Audit Logs
   ------------
   - GET /api/v1/audit-logs
     * Purpose: Retrieve audit logs for monitoring and troubleshooting.
     * Logic: Query Audit Logs table, support filtering by date/status (admin access only).

H. Reporting
   -----------
   - GET /api/v1/reports/module-updates
     * Purpose: Generate reports for modules with available updates, prioritizing security updates.
     * Logic: Aggregate data from Sites, Site Modules, and Module Versions; format and return report in response envelope.

   - GET /api/v1/reports/patch-run
     * Purpose: Generate historical patch run reports.
     * Logic: Aggregate patch run data; compute metrics such as update lag and trends.

4. Response Standards and Error Handling
-----------------------------------------
- All endpoints must return responses in a standardized envelope with "data", "meta", and "links".
- Errors must include status_code, error, message, details, and timestamp.
- HTTP status codes: 400, 401, 403, 404, 409, 422, 429, 500 should be used appropriately.

5. Security and Rate Limiting
-----------------------------
- Use JWT authentication and enforce RBAC for all endpoints.
- Implement API keys for inter-service communication when needed.
- Apply rate limiting globally and on specific endpoints (e.g., for authentication, with a burst allowance).

6. Testing, Logging, and Monitoring
-------------------------------------
- Write unit and integration tests targeting 80%+ code coverage.
- Use structured JSON logging and include correlation IDs for tracing.
- Monitor performance to ensure response times meet SLA targets (e.g., 95th percentile < 200ms).

7. Development Workflow
-----------------------
- Follow minimal and modular changes; adhere to coding standards, use type hints and docstrings.
- Maintain proper environment configuration and use migration tools (Alembic) for database changes.

This document is the definitive guide for our API development efforts and should be followed by all team members to ensure a consistent, secure, and high-performance system. 