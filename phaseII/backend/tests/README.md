# Test Suite for Todo App Backend

This comprehensive test suite tests the Todo App Backend using PostgreSQL as the test database.

## Test Structure

The test suite includes:

- **Database Models Tests**: Verifies that all SQLModel database models work correctly
- **API Endpoint Tests**: Tests the REST API endpoints for all entities (users, tasks, tags, categories, reminders, analytics, subscriptions)
- **Integration Tests**: Tests the integration between different components
- **Authentication Tests**: Verifies JWT token validation and user authorization
- **Performance Tests**: Tests analytics and web vitals tracking

## Configuration

### Database Configuration
- Uses PostgreSQL as the test database (configured via TEST_DATABASE_URL environment variable)
- For Neon PostgreSQL databases, problematic connection parameters are automatically removed
- All tests use transaction rollback for data isolation
- Uses async fixtures with proper event loop handling

### Test Configuration (`pytest.ini`)
- **Coverage**: Minimum 70% code coverage required
- **Reporting**: HTML test reports, coverage reports (HTML, XML, terminal)
- **Markers**: Custom markers for organizing and filtering tests
- **Parallel Execution**: Supports pytest-xdist for parallel test runs
- **Strict Markers**: Enforces use of registered markers only

## Test Organization

### Core Tests
- `test_models.py` - Database models and relationships
- `test_db_connection.py` - Database connection verification
- `test_fixtures.py` - Test fixture validation
- `test_utils.py` - Testing utility functions

### API Endpoint Tests
- `test_tasks.py` - Task CRUD operations and filtering
- `test_tags.py` - Tag management operations
- `test_categories.py` - Category operations
- `test_task_tag_integration.py` - Task-tag relationships
- `test_user_profile.py` - User profile management
- `test_reminders.py` - Reminder management and notifications
- `test_analytics.py` - Analytics events and web vitals tracking
- `test_subscriptions.py` - Push notification subscriptions

### Configuration Files
- `conftest.py` - Pytest configuration with fixtures for database and HTTP client
- `pytest.ini` - Pytest and coverage configuration

## Running the Tests

### Run All Tests
```bash
uv run pytest
```

### Run Tests with Coverage Report
```bash
uv run pytest --cov=src --cov-report=html
```

### Run Specific Test Markers
```bash
# Run only API tests
uv run pytest -m api

# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Run reminder-related tests
uv run pytest -m reminders

# Run analytics tests
uv run pytest -m analytics

# Run notification/subscription tests
uv run pytest -m notifications

# Run authentication tests
uv run pytest -m auth

# Run smoke tests
uv run pytest -m smoke
```

### Run Tests in Parallel
```bash
uv run pytest -n auto
```

### Run Specific Test File
```bash
uv run pytest tests/test_reminders.py -v
```

### Run Tests with HTML Report
```bash
uv run pytest --html=test-report.html --self-contained-html
```

## Test Markers

Tests are organized using the following markers:

- `unit` - Unit tests for individual functions/classes
- `integration` - Integration tests for multiple components
- `api` - API endpoint tests
- `db` - Database-related tests
- `auth` - Authentication and authorization tests
- `slow` - Tests that take longer to run
- `reminders` - Reminder functionality tests
- `analytics` - Analytics and metrics tests
- `notifications` - Notification/subscription tests
- `smoke` - Critical smoke tests

## Coverage Reports

After running tests with coverage, view the reports:

- **Terminal**: Coverage summary displayed in terminal
- **HTML**: Open `htmlcov/index.html` in your browser
- **XML**: `coverage.xml` for CI/CD integration

## Key Features

1. **Database Isolation**: Each test runs in its own transaction which is rolled back
2. **Environment Handling**: Automatically handles Neon PostgreSQL SSL parameters
3. **Async Support**: Full async/await support for FastAPI testing
4. **JWT Testing**: Utilities for creating valid JWT tokens
5. **Test Markers**: Organize and filter tests by category
6. **Coverage Tracking**: Automated code coverage reporting
7. **HTML Reports**: Beautiful HTML test result reports
8. **Parallel Execution**: Run tests faster with pytest-xdist
9. **Access Control Testing**: Verifies user authorization for all endpoints

## Dependencies

The test suite requires:
- pytest
- pytest-asyncio
- pytest-cov
- pytest-xdist
- pytest-html
- httpx
- All application dependencies

Install with:
```bash
uv sync
```

## Best Practices

1. **Always run tests before committing**: `uv run pytest`
2. **Check coverage**: Aim for >80% coverage on new code
3. **Use appropriate markers**: Tag tests with relevant markers
4. **Write isolated tests**: Each test should be independent
5. **Clean test data**: Use fixtures and transaction rollback
6. **Test both success and failure**: Cover happy path and error cases
7. **Test authorization**: Verify users can only access their own data