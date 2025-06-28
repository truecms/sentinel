# Software Requirements Specification Document

## System Design
- Centralized monitoring and reporting platform for multiple Drupal websites.
- Ingestion of module data and security patch updates pushed from Drupal sites.
- Headless API application with a separate front-end dashboard.
- Real-time and historical reporting on module updates, security patches, and SLA compliance.

## Architecture pattern
- Layered architecture separating presentation, business logic, and data storage.
- RESTful API design using FastAPI.
- Modular design supporting asynchronous processing and potential message queuing for data buffering.

## State management
- Stateless authentication using JWT tokens for user sessions.
- Front-end state management via React (with Redux or Context API) in future development.
- Server-side state maintained in PostgreSQL and cached via Redis.

## Data flow
- Data is pushed from Drupal sites to API endpoints.
- FastAPI validates and processes the incoming data.
- Processed data is stored in PostgreSQL and cached in Redis.
- Aggregated data is delivered to the front-end dashboard for real-time visualization and reporting.

## Technical Stack
- **Backend:** Python, FastAPI, SQLAlchemy, asyncpg.
- **Database:** PostgreSQL with JSONB support.
- **Caching/Buffering:** Redis.
- **Frontend (planned):** React.
- **Other Libraries:** pydantic, bcrypt, passlib.
- **Testing:** Pytest, HTTPX.

## Authentication Process
- User authentication via JWT tokens.
- API key-based authentication for system integrations.
- Support for two-factor authentication (2FA) and backup codes.
- Passwords securely stored using bcrypt hashing.

## Route Design
- RESTful endpoints organized under `/api/v1/` prefix.
- Endpoints grouped by resource: users, organizations, sites, modules, patch runs, and reports.
- Standard CRUD operations with pagination and filtering capabilities.

## API Design
- Consistent response envelope structure with fields for data, meta, and links.
- Endpoints include:
  - **User Management:** Create, read, update, and delete users.
  - **Authentication:** Login and logout functionality.
  - **Organization Management:** CRUD operations for organizations.
  - **Site Management:** CRUD operations for sites.
  - **Module Management:** Handling module version data, updates, and historical data.
  - **Patch Run Recording:** Logging and reporting patch application events.
  - **Audit Logs & Reports:** Aggregating security updates and compliance statistics.
- Robust error handling with standardized error responses.

## Database Design ERD
- **Organizations:** id, uuid, name, tax_id, created_at, updated_at, created_by, updated_by, is_active, is_deleted.
- **Users:** id, uuid, name, email, hashed_password, organization_id, role, created_at, updated_at, is_active, is_deleted, last_login, notification_preferences.
- **Sites:** id, uuid, url, name, description, organization_id, created_at, updated_at, created_by, updated_by, is_active, is_deleted.
- **Modules:** id, module_name, drupal_link.
- **Module Versions:** id, module_id, version_number, release_date.
- **Site Modules:** site_id, module_id, current_version_id, update_available, security_update.
- **Patch Runs:** id, site_id, run_date.
- **Audit Logs:** id, site_id, data, status, created_at.