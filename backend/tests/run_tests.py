#!/usr/bin/env python3
"""
Script to run tests with PostgreSQL instead of SQLite to avoid the _sqlite3 module error.
This sets the TEST_DATABASE_URL environment variable before running pytest.
"""
import os
import sys
import subprocess

def run_tests():
    # Set the test database URL to use PostgreSQL instead of SQLite
    os.environ['TEST_DATABASE_URL'] = 'postgresql+asyncpg://todouser:todopass@localhost:5432/todo_test'
    os.environ['ENVIRONMENT'] = 'testing'
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("pytest not found. Installing with pip...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pytest', 'pytest-asyncio', 'httpx'])
        except subprocess.CalledProcessError:
            print("Cannot install pytest. Please install it manually.")
            return 1
    
    # Run pytest with the test directory
    test_dir = './backend/tests/'
    if not os.path.exists(test_dir):
        print(f"Test directory {test_dir} does not exist.")
        return 1
        
    # Run pytest with specific arguments
    sys.exit(pytest.main(['-v', test_dir]))

if __name__ == "__main__":
    run_tests()