"""FastMCP Server for Phase III conversational task management."""

import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

logger = logging.getLogger(__name__)

# Create FastMCP instance with stateless HTTP transport
# Configure allowed hosts for Docker network + localhost
mcp = FastMCP(
    name="phaseiii-task-manager",
    stateless_http=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "127.0.0.1:*",  # Localhost IPv4
            "localhost:*",  # Localhost hostname
            "[::1]:*",  # Localhost IPv6
            "0.0.0.0:*",  # All interfaces
            "mcp-server:*",  # Docker service name
            "*.phaseiii-network:*",  # Docker network (wildcard)
            "mcp-service.todo-phaseiv.svc.cluster.local:*",  # Kubernetes service DNS
            "*.svc.cluster.local:*",  # Kubernetes cluster services (wildcard)
        ],
        allowed_origins=[
            "http://127.0.0.1:*",
            "http://localhost:*",
            "http://[::1]:*",
            "http://mcp-server:*",
            "http://backend:*",
        ],
    ),
)

logger.info("FastMCP Server initialized: phaseiii-task-manager (stateless HTTP)")
logger.info("Allowed hosts: localhost, mcp-server, Docker network, Kubernetes services")


def get_mcp_app():
    """Get the Starlette MCP app for mounting in FastAPI."""
    return mcp.streamable_http_app()


def get_mcp_instance():
    """Get the FastMCP instance for tool registration."""
    return mcp
