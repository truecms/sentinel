# FastAPI Application

## Overview

This project is a FastAPI-based backend application designed to interact with a PostgreSQL database using SQLAlchemy and Pydantic for data validation. It includes features such as user management, organization management, and role-based access controls. The application is containerized using Docker and orchestrated with Docker Compose for easy deployment and scalability.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing with Postman](#testing-with-postman)
- [Postman Collection](#postman-collection)
- [Database Migrations](#database-migrations)
- [Additional Scripts](#additional-scripts)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Management:** Create and authenticate users.
- **Organization Management:** Create and manage organizations with role-based access controls.
- **Database Integration:** Utilizes PostgreSQL for robust data storage.
- **Dockerized:** Easy setup and deployment using Docker and Docker Compose.
- **API Testing:** Comprehensive Postman collection for testing all endpoints.

## Technology Stack

1. **Back-End Framework:** **FastAPI (Python)**
   - Asynchronous processing for high throughput.
   - Integration with Redis and PostgreSQL.

2. **Database:** **PostgreSQL**
   - Relational database with support for JSONB fields.

3. **Migrations:** **Alembic**
   - Database migrations and version control.

4. **Containerization:** **Docker & Docker Compose**
   - Streamlined development and deployment environments.

5. **API Testing:** **Postman**
   - Comprehensive testing of all API endpoints.

## Prerequisites

- **Docker:** Ensure Docker is installed on your machine. [Download Docker](https://www.docker.com/get-started)
- **Docker Compose:** Typically included with Docker Desktop.
- **Git:** For version control. [Download Git](https://git-scm.com/downloads)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Create a `.env` File**

   Create a `.env` file in the `backend` directory to store environment variables.

   ```env
   POSTGRES_USER=your_postgres_user
   POSTGRES_PASSWORD=your_postgres_password
   POSTGRES_DB=your_postgres_db
   JWT_SECRET_KEY=your_jwt_secret_key
   VERSION=1.0.0
   ```

## Configuration

Ensure all necessary environment variables are set either in the `.env` file or your deployment environment. The following variables are required:

- `POSTGRES_SERVER`: Typically set to `db` as defined in `docker-compose.yml`.
- `POSTGRES_USER`: PostgreSQL username.
- `POSTGRES_PASSWORD`: PostgreSQL password.
- `POSTGRES_DB`: PostgreSQL database name.
- `JWT_SECRET_KEY`: Secret key for JWT token generation.
- `VERSION`: Application version.

## Running the Application

Use Docker Compose to build and run the application.

```bash
docker-compose up --build
```

This command will:

- Build the Docker images for the API and PostgreSQL database.
- Start the containers and initialize the database.
- Run database migrations using Alembic.
- Launch the FastAPI application on `http://localhost:8000`.

## API Endpoints

### 1. Health Check

- **Method:** GET
- **URL:** `/health`
- **Description:** Checks if the API is running.

**Example Request:**

```http
GET http://localhost:8000/health
```

**Expected Response:**

```json
{
    "status": "OK"
}
```

### 2. User Management

#### 1. User roles

- Organisation admin
  - Can create, update, delete users.
  - Can invite users to the organization via email.
  - Can create, update, delete organizations.
  - Can create, update, delete sites.
- Organisation user
  - Can create, update, delete sites.
- Organisation viewer
  - Can view sites.

#### 2. User management

##### a. Create User

- **Method:** POST
- **URL:** `/api/v1/users/add`
- **Description:** Registers a new user.
- **Body:** JSON
- **Fields:**
  - `email`: Email address of the user.
  - `password`: Password for the user. Encrypted before storing in database.
  - `user_id`: User ID of the user - incremental integer
  - `created_at`: Timestamp of when the user was created
  - `updated_at`: Timestamp of when the user was last updated
  - `organization_id`: Organization ID of the user.
  - `role_id`: Role ID of the user.
  - `role_name`: Role name of the user.
  - `is_active`: Boolean indicating if the user is active.
  - `is_deleted`: Boolean indicating if the user is deleted.
  - `last_login`: Timestamp of when the user was last logged in.

**Request Body:**

```json
{
    "email": "test@example.com",
    "password": "testpassword123",
    "organization_id": 1
}
```

**Example Request:**

```http
POST http://localhost:8000/api/v1/users/add
Content-Type: application/json

{
    "email": "test@example.com",
    "password": "testpassword123",
    "organization_id": 1
}
```

#### b. Get user details

- **Method:** GET
- **URL:** `/api/v1/users/get/<user_id>`
- **Description:** Get user details by user id.
- **Headers:** `Authorization: Bearer <access_token>`
- **Body:** JSON

**Request Body:**

```json
{
    "user_id": 1
}
```

**Example Request:**

```http
GET http://localhost:8000/api/v1/users/get/1
Authorization: Bearer your_jwt_token
```

**Expected Response:**

```json
{
    "user_id": 1,
    "email": "test@example.com",
    "created_at": "2024-11-06T09:08:24.005Z",
    "updated_at": "2024-11-06T09:08:24.005Z",
    "organization_id": 1,
    "role_id": 1,
    "role_name": "Administrator",
    "is_active": true,
    "is_deleted": false,
    "last_login": "2024-11-06T09:08:24.005Z"
}
```

#### b. User Login

- **Method:** POST
- **URL:** `/api/v1/auth/access-token`
- **Description:** Authenticates a user and returns a JWT token.
- **Body:** `application/x-www-form-urlencoded`
- **Fields:**
  - `username`: Email address of the user.
  - `password`: Password for the user. Encrypted before comparison.
- **Conditions:**
  - User must be active and not deleted.
  - User must belong to an organization.

**Request Body:**

| Key      | Value            |
|----------|------------------|
| username | test@example.com |
| password | testpassword123  |

**Example Request:**

```http
POST http://localhost:8000/api/v1/auth/access-token
Content-Type: application/x-www-form-urlencoded

username=test@example.com&password=testpassword123
```

**Expected Response:**

```json
{
    "access_token": "your_jwt_token",
    "token_type": "bearer"
}
```

#### c. User logout

- **Method:** POST
- **URL:** `/api/v1/auth/logout`
- **Description:** Logs out a user.
- **Headers:** `Authorization: Bearer <access_token>`

**Example Request:**

```http
POST http://localhost:8000/api/v1/auth/logout
Authorization: Bearer your_jwt_token
```

**Expected Response:**

```json
{
    "message": "Logged out successfully"
}
```

#### d. Delete User

- **Method:** DELETE
- **URL:** `/api/v1/users/delete/<user_id>`
- **Description:** Deletes a user.
- **Headers:** `Authorization: Bearer <access_token>`

**Example Request:**

```http
DELETE http://localhost:8000/api/v1/users/delete/1
Authorization: Bearer your_jwt_token
```

**Expected Response:**

```json
{
    "message": "User deleted successfully"
}
```

#### e. Update User

- **Method:** PUT
- **URL:** `/api/v1/users/update/<user_id>`
- **Description:** Updates a user.
- **Headers:** `Authorization: Bearer <access_token>`

**Request Body:**

```json
{
    "email": "test@example.com",
    "password": "testpassword123",
    "organization_id": 1
}
```

**Example Request:**

```http
PUT http://localhost:8000/api/v1/users/update/1
Authorization: Bearer your_jwt_token
Content-Type: application/json

{
    "email": "test@example.com",
    "password": "testpassword123",
    "organization_id": 1
}
```

**Expected Response:**

```json
{
    "message": "User updated successfully"
}
```

### 3. Organization Management

#### a. Create Organization

- **Method:** POST
- **URL:** `/api/v1/organizations/`
- **Description:** Creates a new organization.
- **Headers:** `Authorization: Bearer <access_token>`
- **Body:** JSON
- **Fields:**
  - `name`: Name of the organization.
  - `created_at`: Timestamp of when the organization was created.
  - `created_by`: User ID of the user who created the organization.
  - `updated_at`: Timestamp of when the organization was last updated.
  - `updated_by`: User ID of the user who last updated the organization.
  - `is_active`: Boolean indicating if the organization is active.
  - `is_deleted`: Boolean indicating if the organization is deleted.
  - `organization_id`: Organization ID of the organization.

**Request Body:**

```json
{
    "name": "Test Organization",
    "created_by": 1
}
```

**Example Request:**

```http
POST http://localhost:8000/api/v1/organizations/
Authorization: Bearer your_jwt_token
Content-Type: application/json

{
    "name": "Test Organization",
    "created_by": 1
}
```

**Expected Response:**

```json
{
    "organization_id": 1,
    "name": "Test Organization",
    "created_at": "2024-11-06T09:08:24.005Z",
    "created_by": 1,
    "updated_at": "2024-11-06T09:08:24.005Z",
    "updated_by": 1,
    "is_active": true,
    "is_deleted": false
}
```

#### b. Get Organizations

- **Method:** GET
- **URL:** `/api/v1/organizations/get`
- **Description:** Retrieves a list of organizations.
- **Headers:** `Authorization: Bearer <access_token>`

**Example Request:**

```http
GET http://localhost:8000/api/v1/organizations/get
Authorization: Bearer your_jwt_token
```

**Expected Response:**

```json
[
    {
        "organization_id": 1,
        "name": "Test Organization",
        "created_at": "2024-11-06T09:08:24.005Z",
        "created_by": 1,
        "updated_at": "2024-11-06T09:08:24.005Z",
        "updated_by": 1,
        "is_active": true,
        "is_deleted": false
    },
    {
        "organization_id": 2,
        "name": "Test two Organization",
        "created_at": "2024-11-06T09:08:24.005Z",
        "created_by": 1,
        "updated_at": "2024-11-06T09:08:24.005Z",
        "updated_by": 1,
        "is_active": true,
        "is_deleted": false
    }
]
```

#### c. Get organization details

- **Method:** GET
- **URL:** `/api/v1/organizations/get/<organization_id>`
- **Description:** Retrieves details of a specific organization.
- **Headers:** `Authorization: Bearer <access_token>`

**Example Request:**

```http
GET http://localhost:8000/api/v1/organizations/get/1
Authorization: Bearer your_jwt_token
```

**Expected Response:**

```json
{
    "organization_id": 1,
    "name": "Test Organization",
    "created_at": "2024-11-06T09:08:24.005Z",
    "created_by": 1,
    "updated_at": "2024-11-06T09:08:24.005Z",
    "updated_by": 1,
    "is_active": true,
    "is_deleted": false
}
```

#### d. Delete Organization

- **Method:** DELETE
- **URL:** `/api/v1/organizations/delete/<organization_id>`
- **Description:** Deletes a specific organization.
- **Headers:** `Authorization: Bearer <access_token>`

**Example Request:**

```http
DELETE http://localhost:8000/api/v1/organizations/delete/1
Authorization: Bearer your_jwt_token
```

**Expected Response:**

```json
{
    "message": "Organization deleted successfully",
    "organization_id": 1,
    "name": "Test Organization"
}
```

#### e. Update Organization

- **Method:** PUT
- **URL:** `/api/v1/organizations/update/<organization_id>`
- **Description:** Updates a specific organization.
- **Headers:** `Authorization: Bearer <access_token>`

**Request Body:**

```json
{
    "name": "Test Organization",
    "updated_by": 1,
    "organization_id": 1,
    "is_active": true,
    "is_deleted": false
}
```

### 4. Site Management

#### a. Create Site

- **Method:** POST
- **URL:** `/api/v1/sites/add`
- **Description:** Creates a new site.
- **Headers:** `Authorization: Bearer <access_token>`
- **Fields:**
  - `name`: Name of the site.
  - `created_at`: Timestamp of when the site was created.
  - `created_by`: User ID of the user who created the site.
  - `updated_at`: Timestamp of when the site was last updated.
  - `updated_by`: User ID of the user who last updated the site.
  - `is_active`: Boolean indicating if the site is active.
  - `is_deleted`: Boolean indicating if the site is deleted.
  - `site_id`: Site ID of the site (auto-generated)
  - `organization_id`: Organization ID of the organization the site belongs to.
  - `url`: URL of the site.
  - `description`: Description of the site.
  - `access_token`: Access token of the site.
  - `access_secret`: Access secret of the site.

**Request Body:**

```json
{
    "name": "Test Site",
    "organization_id": 1,
    "url": "https://test.com",
    "description": "Test site",
    "created_by": 1
}
```

**Example Request:**

```http
POST http://localhost:8000/api/v1/sites/add
Authorization: Bearer your_jwt_token
Content-Type: application/json

{
    "name": "Test Site",
    "organization_id": 1,
    "url": "https://test.com",
    "description": "Test site",
    "created_by": 1
}
```

**Expected Response:**

```json
{
    "site_id": 1,
    "name": "Test Site",
    "organization_id": 1,
    "url": "https://test.com",
    "description": "Test site",
    "created_at": "2024-11-06T09:08:24.005Z",
    "created_by": 1,
    "updated_at": "2024-11-06T09:08:24.005Z",
    "updated_by": 1,
    "is_active": true,
    "is_deleted": false,
    "message": "Site created successfully"
}
```

#### b. Get all Sites of organisation

- **Method:** GET
- **URL:** `/api/v1/sites/get/organisation/<organization_id>`
- **Description:** Retrieves all sites of an organisation.
- **Headers:** `Authorization: Bearer <access_token>`

**Example Request:**

```http
GET http://localhost:8000/api/v1/sites/get/organisation/1
Authorization: Bearer your_jwt_token
```

**Expected Response:**

```json
[
    {
        "site_id": 1,
        "name": "Test Site",
        "organization_id": 1,
        "url": "https://test.com",
        "description": "Test site",
        "created_at": "2024-11-06T09:08:24.005Z",
        "created_by": 1,
        "updated_at": "2024-11-06T09:08:24.005Z",
        "updated_by": 1,
        "is_active": true,
        "is_deleted": false
    },
    {
        "site_id": 2,
        "name": "Test two Site",
        "organization_id": 1,
        "url": "https://test2.com",
        "description": "Test two site",
        "created_at": "2024-11-06T09:08:24.005Z",
        "created_by": 1,
        "updated_at": "2024-11-06T09:08:24.005Z",
        "updated_by": 1,
        "is_active": true,
        "is_deleted": false
    }
]
```

#### c. Get Site Details

- **Method:** GET
- **URL:** `/api/v1/sites/get/<site_id>`
- **Description:** Retrieves details of a specific site.
- **Headers:** `Authorization: Bearer <access_token>`

**Example Request:**

```http
GET http://localhost:8000/api/v1/sites/get/1
Authorization: Bearer your_jwt_token
```

**Expected Response:**

```json
{
    "site_id": 1,
    "name": "Test Site",
    "organization_id": 1,
    "url": "https://test.com",
    "description": "Test site",
    "created_at": "2024-11-06T09:08:24.005Z",
    "created_by": 1,
    "updated_at": "2024-11-06T09:08:24.005Z",
    "updated_by": 1,
    "is_active": true,
    "is_deleted": false
}
```

#### d. Delete Site

- **Method:** DELETE
- **URL:** `/api/v1/sites/delete/<site_id>`
- **Description:** Deletes a specific site.
- **Headers:** `Authorization: Bearer <access_token>`

**Example Request:**

```http
DELETE http://localhost:8000/api/v1/sites/delete/1
Authorization: Bearer your_jwt_token
```

**Expected Response:**

```json
{
    "message": "Site deleted successfully",
    "site_id": 1,
    "name": "Test Site"
}
```

#### e. Update Site

- **Method:** PUT
- **URL:** `/api/v1/sites/update/<site_id>`
- **Description:** Updates a specific site.
- **Headers:** `Authorization: Bearer <access_token>`

**Request Body:**

```json
{
    "name": "Test Site", // Field managed by the organisation admin
    "updated_by": 1,
    "site_id": 1,
    "is_active": false, // Field managed by the organisation admin
    "is_deleted": true, // Field managed by the organisation admin
    "organization_id": 1, // Field managed by the organisation admin
    "description": "Test site" // Field managed by the organisation admin
}
```

## Testing with Postman

To facilitate testing all API routes, a Postman collection has been provided. Follow the steps below to import and use the collection.

### 1. Importing the Postman Collection

1. **Download the Collection File**

   The Postman collection JSON file is located in the `postman` directory of the repository.

   **File Path:** `backend/postman/FastAPI_Testing_Collection.json`

2. **Import into Postman**

   - Open Postman.
   - Click on the **Import** button in the top-left corner.
   - Select the `FastAPI_Testing_Collection.json` file from the `postman` directory.
   - Click **Import** to add the collection to your Postman workspace.

### 2. Setting Up Environment Variables in Postman

To manage the `access_token` and other dynamic variables, set up a Postman environment.

1. **Create a New Environment**

   - Click on the **Environments** tab on the left sidebar.
   - Click **New Environment** and name it `FastAPI Environment`.

2. **Add Variables**

   Add the following variables:

   | Variable Name  | Initial Value            | Current Value            |
   |----------------|--------------------------|--------------------------|
   | `base_url`     | `http://localhost:8000`  | `http://localhost:8000`  |
   | `access_token` | *(leave blank)*          | *(leave blank)*          |

3. **Save the Environment**

   Click **Save** to apply the changes.

### 3. Using the Postman Collection

The `FastAPI_Testing_Collection` includes the following requests:

1. **Health Check**
2. **Create User**
3. **User Login**
4. **Create Organization**
5. **Get Organizations**

#### a. Health Check

- **Purpose:** Verify that the API is running.
- **Method:** GET
- **URL:** `{{base_url}}/health`

**Steps:**

1. Select the `Health Check` request.
2. Click **Send**.
3. Expect a `200 OK` response with `{"status": "OK"}`.

#### b. Create User

- **Purpose:** Register a new user.
- **Method:** POST
- **URL:** `{{base_url}}/api/v1/users/`
- **Body:** JSON

**Request Body:**

```json
{
    "email": "test@example.com",
    "password": "testpassword123"
}
```

**Steps:**

1. Select the `Create User` request.
2. Update the request body with desired user details.
3. Click **Send**.
4. Expect a `201 Created` response with user details.

#### c. User Login

- **Purpose:** Authenticate a user and retrieve a JWT token.
- **Method:** POST
- **URL:** `{{base_url}}/api/v1/auth/access-token`
- **Body:** `application/x-www-form-urlencoded`

**Request Body:**

| Key      | Value            |
|----------|------------------|
| username | test@example.com |
| password | testpassword123  |

**Steps:**

1. Select the `User Login` request.
2. Ensure the `username` and `password` fields are correct.
3. Click **Send**.
4. Expect a `200 OK` response with `access_token` and `token_type`.

**Automate Token Storage:**

To automatically store the `access_token` in the environment:

1. Open the `User Login` request.
2. Navigate to the **Tests** tab.
3. Paste the following script:

   ```javascript
   if (pm.response.code === 200) {
       var jsonData = pm.response.json();
       pm.environment.set("access_token", jsonData.access_token);
   }
   ```

4. Click **Save**.

#### d. Create Organization

- **Purpose:** Create a new organization.
- **Method:** POST
- **URL:** `{{base_url}}/api/v1/organizations/`
- **Headers:** `Authorization: Bearer {{access_token}}`
- **Body:** JSON

**Request Body:**

```json
{
    "name": "Test Organization"
}
```

**Steps:**

1. Select the `Create Organization` request.
2. Ensure the `Authorization` header includes `Bearer {{access_token}}`.
3. Update the request body with desired organization details.
4. Click **Send**.
5. Expect a `201 Created` response with organization details.

#### e. Get Organizations

- **Purpose:** Retrieve a list of organizations.
- **Method:** GET
- **URL:** `{{base_url}}/api/v1/organizations/`
- **Headers:** `Authorization: Bearer {{access_token}}`

**Steps:**

1. Select the `Get Organizations` request.
2. Ensure the `Authorization` header includes `Bearer {{access_token}}`.
3. Click **Send**.
4. Expect a `200 OK` response with a list of organizations.

### 4. Postman Collection Structure

The Postman collection is organized into folders for better management.

```
postman/
│
└───FastAPI_Testing_Collection.json
```

- **Health Check:** Ensures the API is operational.
- **User Management:**
  - Create User
  - User Login
- **Organization Management:**
  - Create Organization
  - Get Organizations

### 5. Running the Collection

1. **Select the Collection Runner**

   - Click on the **Runner** button in Postman (usually at the top left).

2. **Choose the Collection and Environment**

   - Select `FastAPI_Testing_Collection`.
   - Choose the `FastAPI Environment`.

3. **Start the Run**

   - Click **Start Run** to execute all requests sequentially.
   - Monitor the results and ensure all tests pass.

## Postman Collection

For best practices, it's recommended to keep your Postman collections organized within a dedicated folder in your repository. Below is an example of how to structure your Postman collections and some sample JSON configurations.

### Directory Structure

```
./
│
├── postman/
│   ├── FastAPI_Testing_Collection.json
│   └── README.md
```

### Sample `FastAPI_Testing_Collection.json`

Here's a simplified example of what your Postman collection JSON might look like. For a complete and detailed collection, you should export it directly from Postman after setting up all your requests.

```json
{
    "info": {
        "name": "FastAPI Testing",
        "_postman_id": "12345678-abcd-efgh-ijkl-1234567890ab",
        "description": "Collection for testing FastAPI endpoints",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Health Check",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/health",
                    "host": ["{{base_url}}"],
                    "path": ["health"]
                }
            },
            "response": []
        },
        {
            "name": "Create User",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"email\": \"test@example.com\",\n    \"password\": \"testpassword123\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/v1/users/",
                    "host": ["{{base_url}}"],
                    "path": ["api", "v1", "users", ""]
                }
            },
            "response": []
        },
        {
            "name": "User Login",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/x-www-form-urlencoded"
                    }
                ],
                "body": {
                    "mode": "urlencoded",
                    "urlencoded": [
                        {
                            "key": "username",
                            "value": "test@example.com"
                        },
                        {
                            "key": "password",
                            "value": "testpassword123"
                        }
                    ]
                },
                "url": {
                    "raw": "{{base_url}}/api/v1/auth/access-token",
                    "host": ["{{base_url}}"],
                    "path": ["api", "v1", "auth", "access-token"]
                }
            },
            "response": []
        },
        {
            "name": "Create Organization",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{access_token}}"
                    },
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"name\": \"Test Organization\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/v1/organizations/",
                    "host": ["{{base_url}}"],
                    "path": ["api", "v1", "organizations", ""]
                }
            },
            "response": []
        },
        {
            "name": "Get Organizations",
            "request": {
                "method": "GET",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{access_token}}"
                    }
                ],
                "url": {
                    "raw": "{{base_url}}/api/v1/organizations/",
                    "host": ["{{base_url}}"],
                    "path": ["api", "v1", "organizations", ""]
                }
            },
            "response": []
        }
    ]
}
```

> **Note:** Replace `{{base_url}}` with your actual base URL (e.g., `http://localhost:8000`). Postman environment variables handle these dynamic values.

## Database Migrations

The project uses Alembic for handling database migrations. Migrations are automatically run during the initialization script.

### Manual Migration Steps

If you need to create new migrations manually, follow these steps:

1. **Create a New Migration**

   ```bash
   docker-compose run api alembic revision --autogenerate -m "Your migration message"
   ```

2. **Apply Migrations**

   ```bash
   docker-compose run api alembic upgrade head
   ```

## Additional Scripts

- **`init_db.py`**: Initializes the database, creates tables, and runs migrations.
- **`verify_installation.py`**: Verifies that all required Python packages are installed.
- **`wait_for_db.py`**: Waits for the PostgreSQL database to be ready before proceeding.
- **`manage_migrations.py`**: Manages database migrations using Alembic.
- **`test_api.py`**: Executes API tests (currently a placeholder).

## Project Structure

The project follows a modular structure with clear separation of concerns:

```
your-repo/
├── app/
│   ├── api/                    # API endpoints and route definitions
│   │   └── v1/
│   │       ├── endpoints/      # API endpoint implementations
│   │       │   ├── auth.py     # Authentication endpoints
│   │       │   ├── organizations.py
│   │       │   ├── roles.py
│   │       │   ├── sites.py
│   │       │   └── users.py
│   │       ├── __init__.py
│   │       └── dependencies.py # Shared API dependencies
│   ├── core/                   # Core functionality and config
│   │   ├── __init__.py
│   │   ├── config.py          # Application configuration
│   │   └── security.py        # Security utilities
│   ├── db/                    # Database related code
│   │   ├── __init__.py
│   │   └── session.py         # Database session management
│   ├── middleware/            # Custom middleware
│   │   ├── __init__.py
│   │   ├── rate_limit.py      # Rate limiting middleware
│   │   └── security.py        # Security middleware
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── organization.py
│   │   ├── role.py
│   │   ├── site.py
│   │   ├── user.py
│   │   ├── user_organization.py
│   │   └── user_role.py
│   ├── schemas/               # Pydantic models/schemas
│   │   ├── __init__.py
│   │   ├── organization.py
│   │   ├── role.py
│   │   ├── site.py
│   │   └── user.py
│   ├── services/             # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── organization.py
│   │   └── user.py
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   └── security.py
│   ├── database.py           # Database configuration
│   └── main.py              # Application entry point
├── alembic/                  # Database migrations
│   ├── versions/
│   └── env.py
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_organizations.py
│   │   └── test_users.py
│   └── test_core/
│       ├── __init__.py
│       └── test_security.py
├── scripts/                  # Utility scripts
│   ├── init_db.py
│   ├── verify_installation.py
│   └── wait_for_db.py
├── postman/                  # Postman collection
│   ├── FastAPI_Testing_Collection.json
│   └── environment.json
├── .env                      # Environment variables
├── .env.example             # Example environment variables
├── .gitignore
├── docker-compose.yml       # Docker compose configuration
├── Dockerfile               # Docker build instructions
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

### Key Components

1. **API Layer (`app/api/`)**: 
   - Contains all API endpoints organized by version
   - Implements REST API logic and request handling

2. **Core (`app/core/`)**: 
   - Contains core application functionality
   - Handles configuration and security

3. **Models (`app/models/`)**: 
   - SQLAlchemy models defining database schema
   - Implements relationships and constraints

4. **Schemas (`app/schemas/`)**: 
   - Pydantic models for request/response validation
   - Defines data shapes for API communication

5. **Services (`app/services/`)**: 
   - Business logic implementation
   - Separates concerns from API layer

6. **Middleware (`app/middleware/`)**: 
   - Custom middleware for rate limiting
   - Security middleware implementation

7. **Tests (`tests/`)**: 
   - Comprehensive test suite
   - API and core functionality tests

## Testing with Postman

### Environment Setup

1. **Import Environment File**

   ```bash
   postman/environment.json
   ```

   Contains environment variables:
   - `base_url`: API base URL
   - `access_token`: JWT token storage
   - `organization_id`: Current organization context
   - `user_id`: Current user context

2. **Configure Variables**

   Development environment example:
   ```json
   {
     "base_url": "http://localhost:8000",
     "access_token": "",
     "organization_id": "",
     "user_id": ""
   }
   ```

### Test Scenarios

The Postman collection includes comprehensive test scenarios:

1. **Authentication Flow**
   - User registration
   - Login and token acquisition
   - Token refresh
   - Password reset flow

2. **User Management**
   - CRUD operations for users
   - Role assignment
   - Organization membership

3. **Organization Operations**
   - Organization creation
   - Member management
   - Role assignments
   - Site management

4. **Site Management**
   - Site creation and configuration
   - Access token management
   - Site statistics and monitoring

### Automated Testing

The collection includes pre-request scripts and tests:

1. **Pre-request Scripts**
   ```javascript
   // Set authentication header
   pm.request.headers.add({
       key: 'Authorization',
       value: 'Bearer ' + pm.environment.get('access_token')
   });
   ```

2. **Test Scripts**
   ```javascript
   // Verify successful response
   pm.test("Status code is 200", function () {
       pm.response.to.have.status(200);
   });

   // Store authentication token
   if (pm.response.code === 200) {
       var jsonData = pm.response.json();
       pm.environment.set("access_token", jsonData.access_token);
   }
   ```

### Running Tests

1. **Individual Endpoints**
   ```bash
   # Using Newman CLI
   newman run postman/FastAPI_Testing_Collection.json -e postman/environment.json
   ```

2. **Complete Flow**
   ```bash
   # Run all tests in sequence
   newman run postman/FastAPI_Testing_Collection.json -e postman/environment.json --folder "Authentication Flow"
   newman run postman/FastAPI_Testing_Collection.json -e postman/environment.json --folder "User Management"
   newman run postman/FastAPI_Testing_Collection.json -e postman/environment.json --folder "Organization Operations"
   ```

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Newman
        run: npm install -g newman
      - name: Run API Tests
        run: |
          newman run postman/FastAPI_Testing_Collection.json \
            -e postman/environment.json \
            --reporters cli,junit \
            --reporter-junit-export results/junit-report.xml
```

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Commit Changes**
   ```bash
   git commit -m "feat: add your feature description"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `test:` for adding tests
   - `refactor:` for code refactoring

4. **Push to Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure tests pass
   - Update documentation

### Development Guidelines

1. **Code Style**
   - Follow PEP 8 for Python code
   - Use type hints
   - Document functions and classes

2. **Testing**
   - Write unit tests for new features
   - Maintain test coverage
   - Run full test suite before submitting PR

3. **Documentation**
   - Update README.md for new features
   - Document API changes
   - Include example usage

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.