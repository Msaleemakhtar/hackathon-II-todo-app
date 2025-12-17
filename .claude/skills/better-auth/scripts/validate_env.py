#!/usr/bin/env python3
"""
Better Auth Environment Variable Validation Script

Validates required environment variables for Better Auth integration.
Run this before starting your application to catch configuration errors early.

Usage:
    python scripts/validate_env.py
    python scripts/validate_env.py --frontend
    python scripts/validate_env.py --backend
"""

import os
import sys
import re
from typing import List, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def validate_secret_length(secret: str, min_length: int = 32) -> Tuple[bool, str]:
    """Validate that secret meets minimum length requirement"""
    if len(secret) < min_length:
        return False, f"Secret is {len(secret)} characters (minimum: {min_length})"
    return True, f"Secret length: {len(secret)} characters"


def validate_url_format(url: str) -> Tuple[bool, str]:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if url_pattern.match(url):
        return True, f"Valid URL format"
    return False, "Invalid URL format (must start with http:// or https://)"


def validate_database_url(db_url: str) -> Tuple[bool, str]:
    """Validate database URL format"""
    if not db_url.startswith('postgresql://'):
        return False, "Database URL must start with 'postgresql://'"

    # Check for basic components
    if '@' not in db_url or '/' not in db_url:
        return False, "Invalid database URL format"

    return True, "Valid PostgreSQL URL format"


def check_variable(name: str, required: bool = True, validator=None) -> bool:
    """Check single environment variable"""
    value = os.getenv(name)

    if value is None:
        if required:
            print_error(f"{name}: Missing (required)")
            return False
        else:
            print_warning(f"{name}: Not set (optional)")
            return True

    # Run validator if provided
    if validator:
        is_valid, message = validator(value)
        if is_valid:
            print_success(f"{name}: {message}")
        else:
            print_error(f"{name}: {message}")
        return is_valid

    print_success(f"{name}: Set")
    return True


def validate_frontend_env() -> bool:
    """Validate frontend environment variables"""
    print_header("Frontend Environment Variables")

    checks = [
        ("BETTER_AUTH_SECRET", True, validate_secret_length),
        ("BETTER_AUTH_URL", True, validate_url_format),
        ("NEXT_PUBLIC_BETTER_AUTH_URL", True, validate_url_format),
        ("NEXT_PUBLIC_API_BASE_URL", True, validate_url_format),
        ("DATABASE_URL", True, validate_database_url),
    ]

    results = []
    for name, required, validator in checks:
        result = check_variable(name, required, validator)
        results.append(result)

    return all(results)


def validate_backend_env() -> bool:
    """Validate backend environment variables"""
    print_header("Backend Environment Variables")

    checks = [
        ("BETTER_AUTH_SECRET", True, validate_secret_length),
        ("DATABASE_URL", True, validate_database_url),
        ("ACCESS_TOKEN_EXPIRE_MINUTES", False, None),
    ]

    results = []
    for name, required, validator in checks:
        result = check_variable(name, required, validator)
        results.append(result)

    return all(results)


def validate_secret_consistency():
    """Validate that frontend and backend secrets match"""
    print_header("Secret Consistency Check")

    frontend_secret = os.getenv("BETTER_AUTH_SECRET")
    # In production, backend would be in different env file
    # This is a simplified check for development

    if not frontend_secret:
        print_error("Cannot validate consistency: BETTER_AUTH_SECRET not set")
        return False

    print_success("Frontend BETTER_AUTH_SECRET is set")
    print_warning("Ensure backend uses the same BETTER_AUTH_SECRET value")

    return True


def generate_secret_command():
    """Show command to generate secure secret"""
    print_header("Generate Secure Secret")
    print("Run this command to generate a secure secret:")
    print(f"{Colors.BOLD}openssl rand -base64 32{Colors.END}")
    print("\nThen add to your .env.local:")
    print(f"{Colors.BOLD}BETTER_AUTH_SECRET=<generated-secret>{Colors.END}")


def main():
    """Main validation function"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    # Load .env.local if it exists (for development)
    env_file = '.env.local'
    if os.path.exists(env_file):
        print(f"Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")

    print_header("Better Auth Environment Validation")

    all_valid = True

    if not args or '--frontend' in args:
        frontend_valid = validate_frontend_env()
        all_valid = all_valid and frontend_valid

    if not args or '--backend' in args:
        backend_valid = validate_backend_env()
        all_valid = all_valid and backend_valid

    if not args or '--consistency' in args:
        consistency_valid = validate_secret_consistency()
        all_valid = all_valid and consistency_valid

    # Print summary
    print_header("Validation Summary")

    if all_valid:
        print_success("All environment variables are properly configured!")
        print("")
        return 0
    else:
        print_error("Some environment variables are missing or invalid")
        print("")
        generate_secret_command()
        return 1


if __name__ == "__main__":
    sys.exit(main())
