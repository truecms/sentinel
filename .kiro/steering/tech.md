# Technology Stack

## Backend
- **Framework**: FastAPI (Python 3.11+) with async/await support
- **Database**: PostgreSQL with SQLAlchemy 2.0+ (async)
- **Cache/Queue**: Redis for rate limiting and Celery task queue
- **Authentication**: JWT tokens with python-jose, bcrypt for password hashing
- **API**: RESTful with OpenAPI/Swagger documentation
- **Migrations**: Alembic for database schema management

## Frontend
- **Framework**: React 19+ with TypeScript
- **Build Tool**: Vite with hot module replacement
- **Styling**: Tailwind CSS with Headless UI components
- **State Management**: Redux Toolkit + React Query for server state
- **Routing**: React Router v7
- **Forms**: React Hook Form with Zod validation
- **Charts**: Recharts for data visualization
- **Testing**: Vitest + React Testing Library

## Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for local development
- **Database**: PostgreSQL 15+ with asyncpg driver
- **Reverse Proxy**: Nginx (production)
- **Process Management**: Uvicorn ASGI server

## Development Tools
- **Testing**: pytest with asyncio support, 80% coverage requirement
- **Linting**: ESLint for frontend, Python follows PEP 8
- **Formatting**: Prettier for frontend code
- **Git Hooks**: Husky with lint-staged for pre-commit checks
- **API Testing**: Postman collections with Newman for automation

## Common Commands

### Backend Development
```bash
# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Run tests with coverage
docker-compose exec test pytest --cov=app --cov-report=term-missing

# View API logs
docker-compose logs -f api

# Access database
docker-compose exec -u postgres db psql -d application_db
```

### Frontend Development
```bash
# Start frontend development server
docker-compose up -d frontend

# Install new dependencies
docker-compose exec frontend npm install <package>

# Run frontend tests
docker-compose exec frontend npm test

# Build for production
docker-compose build --build-arg target=production frontend

# Lint and format
docker-compose exec frontend npm run lint
```

### Testing
```bash
# Run all backend tests
docker-compose exec test pytest

# Run specific test file
docker-compose exec test pytest tests/test_api/test_auth.py

# Run with coverage report
docker-compose exec test pytest --cov=app --cov-report=html

# Run frontend tests
docker-compose exec frontend npm run test:coverage
```

### Database Management
```bash
# Initialize database
./scripts/init-db.sh

# Create superuser
docker-compose exec api python scripts/create_superuser.py

# Reset database
docker-compose down -v && docker-compose up -d
```

## Environment Configuration
- **Development**: `.env` file with Docker Compose
- **Testing**: Separate test database and environment variables
- **Production**: Environment-specific Docker builds and configurations