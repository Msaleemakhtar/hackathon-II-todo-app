"""Kafka configuration for Redpanda Cloud integration."""

import os
import ssl
from typing import Dict, List

# Kafka broker configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"  # Default for local development
)

# SASL/SCRAM authentication
KAFKA_SECURITY_PROTOCOL = os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_SSL")
KAFKA_SASL_MECHANISM = os.getenv("KAFKA_SASL_MECHANISM", "SCRAM-SHA-256")
KAFKA_SASL_USERNAME = os.getenv("KAFKA_SASL_USERNAME", "")
KAFKA_SASL_PASSWORD = os.getenv("KAFKA_SASL_PASSWORD", "")

# Topic configuration
KAFKA_TOPICS: Dict[str, Dict[str, int | str]] = {
    "task-events": {
        "num_partitions": 3,
        "replication_factor": 1,
        "retention_ms": "604800000",  # 7 days
    },
    "task-reminders": {
        "num_partitions": 1,
        "replication_factor": 1,
        "retention_ms": "86400000",  # 1 day
    },
    "task-recurrence": {
        "num_partitions": 1,
        "replication_factor": 1,
        "retention_ms": "604800000",  # 7 days
    },
}

# Producer configuration (at-least-once delivery)
KAFKA_PRODUCER_CONFIG = {
    "acks": "all",  # Wait for all replicas (required for idempotence)
    "enable_idempotence": True,  # Prevent duplicates on retry
    "compression_type": "gzip",  # Reduce network bandwidth
    "max_request_size": 1048576,  # 1MB max message size
    "request_timeout_ms": 30000,  # 30 seconds
    "retry_backoff_ms": 100,  # Exponential backoff
}

# Producer initialization timeout (SASL_SSL handshake can be slow)
KAFKA_PRODUCER_INIT_TIMEOUT_SECONDS = int(os.getenv("KAFKA_PRODUCER_INIT_TIMEOUT", "90"))

# Producer retry configuration
KAFKA_PRODUCER_MAX_RETRIES = int(os.getenv("KAFKA_PRODUCER_MAX_RETRIES", "3"))
KAFKA_PRODUCER_RETRY_DELAY_SECONDS = int(os.getenv("KAFKA_PRODUCER_RETRY_DELAY", "5"))

# Consumer configuration
KAFKA_CONSUMER_CONFIG = {
    "auto_offset_reset": "earliest",  # Start from beginning on first run
    "enable_auto_commit": False,  # Manual commit for control
    "max_poll_records": 10,  # Reduced from 100 to 10 (faster batch processing, prevents timeout)
    "max_poll_interval_ms": 300000,  # 5 minutes (time allowed to process batch before eviction)
    "session_timeout_ms": 60000,  # 60 seconds (increased from 30s to allow longer processing)
    "heartbeat_interval_ms": 3000,  # 3 seconds (increased frequency from 10s for faster failure detection)
    "request_timeout_ms": 90000,  # 90 seconds (increased from default 30s for slow SASL handshake)
    "connections_max_idle_ms": 300000,  # 5 minutes (keep connections alive longer)
    "metadata_max_age_ms": 300000,  # 5 minutes (refresh metadata less frequently)
}

# Consumer group IDs
NOTIFICATION_SERVICE_GROUP_ID = "notification-service-group"
RECURRING_TASK_SERVICE_GROUP_ID = "recurring-task-service-group"

# Health check configuration
KAFKA_HEALTH_CHECK_TIMEOUT_MS = 5000  # 5 seconds


def get_kafka_ssl_context() -> ssl.SSLContext | None:
    """
    Create SSL context for Kafka SASL_SSL connections.

    Returns:
        SSLContext configured for Redpanda Cloud, or None if not using SSL
    """
    if KAFKA_SECURITY_PROTOCOL in ("SASL_SSL", "SSL"):
        # Create default SSL context with system CA certificates
        context = ssl.create_default_context()
        # Enable hostname checking for security
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        return context
    return None
