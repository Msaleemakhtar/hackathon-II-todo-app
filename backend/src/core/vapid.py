"""
VAPID (Voluntary Application Server Identification) key management for web push notifications.

This module provides utilities for generating and managing VAPID keys used for
browser push notifications.
"""

import base64
import logging
import os
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


def generate_vapid_keys() -> Dict[str, str]:
    """
    Generate a new pair of VAPID keys for web push notifications.

    Returns:
        Dictionary with 'public_key' and 'private_key' in base64 format

    Raises:
        ImportError: If py_vapid is not installed
    """
    try:
        from py_vapid import Vapid

        vapid = Vapid()
        vapid.generate_keys()

        # Get keys in the format needed for web push
        private_key = vapid.private_key.private_bytes(
            encoding=base64.urlsafe_b64encode.__self__,
            format=base64.urlsafe_b64encode.__self__,
            encryption_algorithm=base64.urlsafe_b64encode.__self__,
        )
        public_key = vapid.public_key.public_bytes(
            encoding=base64.urlsafe_b64encode.__self__,
            format=base64.urlsafe_b64encode.__self__,
        )

        return {
            "public_key": base64.urlsafe_b64encode(public_key).decode("utf-8").rstrip("="),
            "private_key": base64.urlsafe_b64encode(private_key).decode("utf-8").rstrip("="),
        }

    except ImportError:
        logger.error("py_vapid library not installed. Install with: pip install py-vapid")
        raise


def get_vapid_keys() -> Tuple[str, str]:
    """
    Get VAPID keys from environment variables.

    Returns:
        Tuple of (public_key, private_key)

    Raises:
        ValueError: If VAPID keys are not configured
    """
    public_key = os.getenv("VAPID_PUBLIC_KEY")
    private_key = os.getenv("VAPID_PRIVATE_KEY")

    if not public_key or not private_key:
        raise ValueError(
            "VAPID keys not configured. Set VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY "
            "environment variables, or run generate_vapid_keys() to create new keys."
        )

    return public_key, private_key


def get_vapid_claims() -> Dict[str, str]:
    """
    Get VAPID claims for web push notifications.

    Returns:
        Dictionary with VAPID claims (subject)
    """
    claim_email = os.getenv("VAPID_CLAIM_EMAIL", "admin@example.com")

    return {
        "sub": f"mailto:{claim_email}"
    }


def main():
    """
    Command-line utility to generate VAPID keys.

    Usage:
        python -m backend.src.core.vapid
    """
    print("Generating VAPID keys for web push notifications...")
    print()

    try:
        keys = generate_vapid_keys()

        print("✓ VAPID keys generated successfully!")
        print()
        print("Add these to your .env file:")
        print("-" * 60)
        print(f"VAPID_PUBLIC_KEY={keys['public_key']}")
        print(f"VAPID_PRIVATE_KEY={keys['private_key']}")
        print(f"VAPID_CLAIM_EMAIL=your-email@example.com")
        print("-" * 60)
        print()
        print("The public key should also be used in your frontend service worker.")

    except Exception as e:
        print(f"✗ Error generating VAPID keys: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
