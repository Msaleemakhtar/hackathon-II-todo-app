# Test Suite for Todo App Backend

This test suite has been created to test the Todo App Backend using PostgreSQL as the test database.

## Test Structure

The test suite includes:

- **Database Models Tests**: Verifies that all SQLModel database models work correctly
- **API Endpoint Tests**: Tests the REST API endpoints for all entities (users, tasks, tags, categories)
- **Integration Tests**: Tests the integration between different components, including task-tag relationships

## Configuration

- Uses PostgreSQL as the test database (configured via TEST_DATABASE_URL environment variable)
- For Neon PostgreSQL databases, problematic connection parameters are automatically removed
- All tests use transaction rollback for data isolation
- Uses async fixtures with proper event loop handling

## Test Organization

- `test_models.py` - Tests for database models and their relationships
- `test_user_profile.py` - Tests for user profile management endpoints
- `test_tasks.py` - Tests for task CRUD operations and filtering
- `test_tags.py` - Tests for tag management operations
- `test_categories.py` - Tests for category operations
- `test_task_tag_integration.py` - Tests for task-tag relationship operations
- `test_db_connection.py` - Basic database connection test
- `test_utils.py` - Utility functions for testing (e.g., JWT token creation)
- `conftest.py` - Pytest configuration with fixtures for database and HTTP client

## Running the Tests

To run all tests:
```bash
uv run python -m pytest tests/ -v
```

To run specific tests:
```bash
uv run python -m pytest tests/test_models.py -v
```

## Key Features

1. **Database Isolation**: Each test runs in its own transaction which is rolled back after the test
2. **Environment Handling**: Automatically handles Neon PostgreSQL SSL parameters
3. **Async Support**: Full async/await support for FastAPI testing
4. **JWT Testing**: Includes utilities for creating valid JWT tokens for testing

## Dependencies

The test suite requires:
- pytest
- pytest-asyncio
- httpx
- All the application dependencies

These are installed when you run `uv sync --dev`.