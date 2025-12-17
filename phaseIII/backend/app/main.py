import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


# Custom rate limit exception handler with logging (T113)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom rate limit exceeded handler with event logging.

    Logs rate limit events for monitoring and security analysis.
    """
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    logger.warning(
        f"Rate limit exceeded: ip={client_ip}, path={path}, limit={exc.detail}",
        extra={"ip": client_ip, "path": path, "limit": exc.detail},
    )

    return Response(
        content=f"Rate limit exceeded: {exc.detail}",
        status_code=429,
        headers={"Retry-After": "60"},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Starting Phase III Backend...")
    # Note: Database tables will be created via Alembic migrations
    # await create_db_and_tables()  # Uncomment if not using Alembic

    # Import tools to register them with FastMCP
    print("FastMCP tools registered")

    yield

    # Shutdown
    print("Shutting down Phase III Backend...")


# Create FastAPI application
app = FastAPI(
    title="Phase III AI Chat Service",
    description="""
    **Conversational Task Management API**

    An AI-powered chat service that allows users to manage their tasks through natural language conversations.

    ## Features
    - 🤖 Natural language task management using Google Gemini
    - 💬 Persistent conversation history
    - 🔒 Secure authentication with Better Auth
    - ⚡ Rate limiting and input sanitization
    - 📊 Real-time task operations via MCP tools

    ## Authentication
    All endpoints (except `/health`, `/`, and `/docs`) require a valid JWT token in the `Authorization` header:
    ```
    Authorization: Bearer <your-jwt-token>
    ```

    ## Rate Limits
    - Chat endpoint: 10 requests per minute per user
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Phase III Development Team",
        "url": "https://github.com/yourusername/todo-app",
    },
    license_info={
        "name": "MIT",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "phaseiii-backend",
        "version": "0.1.0",
        "environment": settings.environment,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Phase III AI Chat Service API",
        "docs": "/docs",
        "health": "/health",
    }


# Import and include routers
from app.routers import chat

app.include_router(chat.router)

# Mount FastMCP app
from app.mcp.server import get_mcp_app

mcp_app = get_mcp_app()
app.mount("/mcp", mcp_app)
