"""FastAPI application entry point for Phase III MCP Server."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import tools to register them
import app.mcp.tools  # noqa: F401
from app.config import settings
from app.mcp.server import mcp_server_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[misc]
    """
    Manage application lifespan events.

    This handles startup and shutdown logic for the MCP server.
    """
    # Startup: Register MCP tools
    # Tools will be registered when their modules are imported
    yield
    # Shutdown: Clean up resources if needed
    pass


# Create FastAPI application
app = FastAPI(
    title="Phase III MCP Server Backend",
    description="AI-powered todo chatbot backend with MCP tool server",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled errors.

    Returns standardized error format: {detail, code, field?}
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "code": "INTERNAL_ERROR"
        }
    )


@app.get("/health")
async def health_check() -> dict[str, str | int]:
    """
    Health check endpoint.

    Returns:
        dict: Status information
    """
    return {
        "status": "ok",
        "service": "todo-mcp-server",
        "version": "0.1.0",
        "mcp_tools_registered": len(mcp_server_manager.get_registered_tools()),
    }


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "message": "Phase III MCP Server Backend",
        "version": "0.1.0",
        "health_check": "/health",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
