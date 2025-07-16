# Project Structure

## Root Level Organization
```
├── app/                    # Backend FastAPI application
├── frontend/              # React frontend application
├── tests/                 # Backend test suite
├── docs/                  # Project documentation
├── scripts/               # Utility scripts (DB init, user creation)
├── postman/               # API testing collections
├── examples/              # Mock data and examples
├── alembic/               # Database migrations
├── .docker/               # Docker configuration files
└── github-issues/         # Project planning and issues
```

## Backend Structure (`app/`)
```
app/
├── __init__.py
├── main.py                # FastAPI application entry point
├── api/                   # API layer
│   ├── deps.py           # Common dependencies
│   └── v1/               # API version 1
│       ├── api.py        # Router aggregation
│       ├── endpoints/    # Individual endpoint modules
│       └── dependencies/ # Route-specific dependencies
├── core/                  # Core configuration and utilities
│   ├── config.py         # Settings and configuration
│   ├── security.py       # Authentication utilities
│   ├── celery_app.py     # Celery configuration
│   └── redis.py          # Redis connection
├── crud/                  # Database operations (Create, Read, Update, Delete)
├── db/                    # Database configuration
│   ├── base_class.py     # Base model class
│   └── session.py        # Database session management
├── models/                # SQLAlchemy database models
├── schemas/               # Pydantic schemas for API serialization
├── services/              # Business logic layer
└── tasks/                 # Celery background tasks
```

## Frontend Structure (`frontend/src/`)
```
src/
├── App.tsx               # Main application component
├── main.tsx              # Application entry point
├── app/                  # Redux store and API configuration
│   ├── store.ts          # Redux store setup
│   ├── api.ts            # API client configuration
│   └── types.ts          # Global TypeScript types
├── components/           # Reusable UI components
│   ├── auth/             # Authentication components
│   ├── common/           # Generic UI components
│   ├── dashboard/        # Dashboard-specific components
│   ├── navigation/       # Navigation components
│   ├── public/           # Public-facing components
│   └── ui/               # Base UI components
├── features/             # Feature-based organization
│   ├── auth/             # Authentication feature
│   ├── modules/          # Module management feature
│   ├── organizations/    # Organization management
│   └── reports/          # Reporting feature
├── hooks/                # Custom React hooks
├── layouts/              # Page layout components
├── pages/                # Page components
├── services/             # API services and utilities
├── styles/               # Global styles
└── utils/                # Utility functions
```

## Testing Structure
```
tests/
├── conftest.py           # Test configuration and fixtures
├── factories/            # Test data factories
├── integration/          # Integration tests
├── test_api/             # API endpoint tests
│   ├── auth/             # Authentication tests
│   ├── modules/          # Module-related tests
│   ├── organizations/    # Organization tests
│   ├── sites/            # Site management tests
│   └── users/            # User management tests
├── test_models/          # Database model tests
└── test_services/        # Business logic tests
```

## Key Architectural Patterns

### Backend Patterns
- **Layered Architecture**: API → Services → CRUD → Models
- **Dependency Injection**: FastAPI's dependency system for database sessions, authentication
- **Repository Pattern**: CRUD modules abstract database operations
- **Schema Separation**: Pydantic schemas separate from SQLAlchemy models
- **Async/Await**: Consistent async patterns throughout the application

### Frontend Patterns
- **Feature-Based Organization**: Group related components, hooks, and services
- **Component Composition**: Reusable components with clear interfaces
- **Custom Hooks**: Extract and reuse stateful logic
- **Type Safety**: Comprehensive TypeScript usage
- **State Management**: Redux for global state, React Query for server state

### Database Patterns
- **Migration-First**: All schema changes through Alembic migrations
- **Soft Deletes**: Use `is_active` flags instead of hard deletes
- **Audit Fields**: `created_at`, `updated_at`, `created_by`, `updated_by` on all entities
- **Relationship Modeling**: Clear foreign key relationships with proper cascading

### API Design Patterns
- **RESTful Endpoints**: Standard HTTP methods and status codes
- **Versioned APIs**: `/api/v1/` prefix for version management
- **Consistent Response Format**: Standardized JSON responses with data/meta/links
- **Pagination**: Standard `skip`/`limit` parameters
- **Error Handling**: Consistent error response format

## File Naming Conventions
- **Backend**: Snake_case for Python files and functions
- **Frontend**: PascalCase for components, camelCase for functions/variables
- **Tests**: `test_` prefix for all test files
- **Migrations**: Timestamped with descriptive names
- **API Endpoints**: Plural nouns for resources (`/users`, `/organizations`)

## Import Organization
- **Backend**: Absolute imports from `app.` root
- **Frontend**: Relative imports within features, absolute for shared utilities
- **Test Files**: Import from the module being tested, fixtures from conftest