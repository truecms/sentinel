Test Debugging and Optimization Rules
=================================

1. Test Setup and Organization
----------------------------
### File Structure
- Keep test files modular and focused
- Use descriptive names: `test_<feature>_<scenario>.py`
- Group related tests in the same file
- Maintain test isolation through proper fixtures

### Example Structure
```python
# tests/test_api/test_auth.py
from typing import AsyncGenerator
import pytest
from sqlalchemy.orm import Session
from app.models.user import User

@pytest.fixture
async def test_user(db_session: Session) -> AsyncGenerator[User, None]:
    """Create a test user for authentication tests."""
    user = User(
        email="test@example.com",
        hashed_password="test_hash",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    yield user
    # Cleanup handled by db_session fixture
```

2. Fixture Best Practices
------------------------
### Database Fixtures
- Use session-scoped fixtures for database setup
- Preserve essential data (e.g., superuser)
- Use unique identifiers for test data
- Implement proper cleanup

### Example Database Fixture
```python
@pytest.fixture(scope="session")
def db_session() -> Generator[Session, None, None]:
    """Create a clean database session for testing."""
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        # Preserve superuser
        superuser_email = settings.SUPERUSER_EMAIL
        superuser = session.query(User).filter(
            User.email == superuser_email
        ).first()
        
        yield session
        
        # Clean up all tables except preserved data
        session.execute(text(
            """
            DELETE FROM user_organizations 
            WHERE user_id != :superuser_id;
            DELETE FROM sites;
            DELETE FROM organizations;
            DELETE FROM users WHERE id != :superuser_id;
            """
        ), {"superuser_id": superuser.id if superuser else 0})
        session.commit()
    finally:
        session.close()
```

3. Debugging Strategies
----------------------
### Test Failure Analysis
1. Check the exact error message and traceback
2. Verify database state before and after the test
3. Use pytest's -vv flag for detailed output
4. Add strategic print statements or logging
5. Check transaction management

### Database State Verification
```python
def verify_db_state(db: Session, table: str) -> None:
    """Print current state of a database table."""
    result = db.execute(text(f"SELECT * FROM {table}"))
    print(f"\nCurrent state of {table}:")
    for row in result:
        print(row)
```

4. Common Issues and Solutions
----------------------------
### Foreign Key Violations
- Ensure parent records exist before creating child records
- Use proper fixture dependencies
- Verify cascade delete settings

### Example Fix
```python
@pytest.fixture
async def test_organization(
    db_session: Session,
    test_superuser: User  # Dependency on superuser fixture
) -> Organization:
    """Create test organization with valid user reference."""
    org = Organization(
        name="Test Org",
        created_by=test_superuser.id,  # Valid user reference
        updated_by=test_superuser.id
    )
    db_session.add(org)
    db_session.commit()
    return org
```

5. Test Coverage Optimization
---------------------------
### Requirements
- Minimum 80% coverage required
- Focus on critical paths
- Identify uncovered code sections
- Add missing test cases

### Coverage Analysis
```bash
# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html
```

6. Performance Optimization
-------------------------
### Async Test Optimization
- Use proper async fixtures
- Avoid unnecessary database operations
- Implement connection pooling
- Use test parallelization when possible

### Example Async Test
```python
@pytest.mark.asyncio
async def test_async_operation():
    async with AsyncClient() as client:
        response = await client.get("/api/resource")
        assert response.status_code == 200
```

7. Debugging Tools Integration
----------------------------
### VSCode Configuration
```json
{
    "python.testing.pytestArgs": [
        "tests",
        "-v",
        "--tb=short"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true
}
```

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

8. Test Data Management
----------------------
### Using Factories
```python
from factory import Factory, Faker

class UserFactory(Factory):
    class Meta:
        model = User
    
    email = Faker('email')
    is_active = True
```

### Cleanup Strategies
- Use pytest fixtures for setup/teardown
- Implement transaction rollback
- Clean up in reverse order of creation

9. Best Practices
----------------
- Keep tests simple and focused
- Use proper assertions
- Handle async operations correctly
- Monitor test coverage
- Document test requirements
- Use meaningful test data
- Implement proper error handling
- Regular test maintenance

10. Continuous Integration
-------------------------
### GitHub Actions Example
```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

6. Async Database Operations
---------------------------
### Key Rules for Async Database Operations
1. Always use `async with` when working with async database sessions
2. Never perform database operations outside of async context
3. Use proper async fixtures and dependencies
4. Handle transaction management correctly
5. Ensure proper cleanup of async resources

### Common Pitfalls and Solutions
```python
# WRONG - Database operation outside async context
def test_wrong_db_operation(db_session):
    result = db_session.execute(query)  # Will fail with MissingGreenlet

# CORRECT - Using async context
async def test_correct_db_operation(db_session):
    async with db_session as session:
        result = await session.execute(query)
```

### Async Session Management
```python
# WRONG - Not using async context manager
async def test_wrong_session_usage(db_session):
    user = await db_session.get(User, user_id)  # May cause MissingGreenlet
    await db_session.commit()

# CORRECT - Using async context manager
async def test_correct_session_usage(db_session):
    async with db_session as session:
        user = await session.get(User, user_id)
        await session.commit()
```

### Database Operations in Tests
```python
# Example of correct async database operations in tests
async def test_database_operations(db_session: AsyncSession):
    async with db_session as session:
        # Create
        new_user = User(email="test@example.com")
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        # Read
        query = select(User).where(User.email == "test@example.com")
        result = await session.execute(query)
        user = result.scalar_one()

        # Update
        user.is_active = False
        await session.commit()
        await session.refresh(user)

        # Delete
        await session.delete(user)
        await session.commit()
```

### Async Fixture Setup
```python
@pytest_asyncio.fixture
async def async_db_fixture(async_session_maker):
    async with async_session_maker() as session:
        try:
            yield session
            await session.rollback()
        finally:
            await session.close()

# Using the fixture
async def test_with_fixture(async_db_fixture):
    async with async_db_fixture as session:
        # Perform database operations
        result = await session.execute(query)
```

### Transaction Management
```python
# WRONG - Missing transaction management
async def test_wrong_transaction():
    user = await session.get(User, 1)
    user.name = "New Name"
    # Missing commit, changes won't persist

# CORRECT - Proper transaction management
async def test_correct_transaction():
    async with session as transaction:
        user = await session.get(User, 1)
        user.name = "New Name"
        await session.commit()
        # Use refresh to get updated data
        await session.refresh(user)
```

### Error Handling
```python
async def test_with_error_handling():
    async with session as transaction:
        try:
            # Database operations
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Best Practices for Async Database Testing
1. Always use `pytest.mark.asyncio` decorator for async tests
2. Properly scope your database fixtures
3. Handle session cleanup in fixtures
4. Use transaction rollback for test isolation
5. Implement proper error handling
6. Avoid mixing sync and async operations
7. Ensure all database operations are awaited
8. Use appropriate assertion patterns for async results

Remember:
- Keep tests simple and focused
- Use proper fixtures
- Handle async operations correctly
- Monitor test coverage
- Regular maintenance and updates 