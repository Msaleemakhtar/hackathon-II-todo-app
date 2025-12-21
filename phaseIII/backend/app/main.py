import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings

# Configure logging explicitly to ensure INFO level for all app modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,  # Override any existing configuration
)
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
    # Import and create database tables
    from app.database import create_db_and_tables
    await create_db_and_tables()
    print("Database tables created/verified")

    # MCP tools are defined in app/mcp/tools.py and run in a separate MCP server service
    print("MCP tools defined (running in separate mcp-server service)")

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
        "adapters": ["chatkit"],
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Phase III AI Chat Service API",
        "docs": "/docs",
        "health": "/health",
    }


# Import ChatKit SDK components
from fastapi.responses import StreamingResponse
from app.chatkit import PostgresStore, TaskChatServer, extract_user_context

# Initialize ChatKit SDK
logger.info("Initializing ChatKit SDK...")
store = PostgresStore()
task_server = TaskChatServer(store=store)
logger.info("ChatKit SDK initialized")


# ChatKit endpoint handler
@app.api_route("/chatkit", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def chatkit_handler(request: Request):
    """
    ChatKit SDK endpoint handler.

    Routes all ChatKit protocol requests to the TaskChatServer.process() method.
    Authenticates user via JWT and passes context to ChatKitServer.
    """
    logger.info(f"📨 ChatKit request: {request.method} {request.url.path}")

    try:
        # Extract user context from JWT
        context = await extract_user_context(request)
        user_id = context.get("user_id")
        logger.info(f"✅ Authenticated user: {user_id}")

        # Get request body
        body = await request.body()
        logger.info(f"📨 Request body length: {len(body)} bytes")
        if body:
            import json
            try:
                body_json = json.loads(body)
                logger.info(f"📨 Request type: {body_json.get('type', 'unknown')}")
                logger.info(f"📨 Request params: {body_json.get('params', {})}")
            except:
                pass

        # Process request via ChatKitServer
        result = await task_server.process(body, context)
        logger.info(f"📤 Result type: {type(result).__name__}")

        # Handle streaming vs non-streaming results
        if hasattr(result, '__aiter__'):
            # Streaming result
            logger.info("🌊 Streaming response detected")
            chunk_count = 0

            async def stream_generator():
                nonlocal chunk_count
                try:
                    async for chunk in result:
                        chunk_count += 1
                        # Debug logging for SSE chunks
                        logger.info(f"📤 SSE Chunk {chunk_count}: type={type(chunk).__name__}, size={len(chunk) if isinstance(chunk, (str, bytes)) else 'N/A'}")
                        if isinstance(chunk, bytes):
                            try:
                                logger.info(f"   Content preview: {chunk[:200].decode('utf-8', errors='ignore')}")
                            except:
                                logger.info(f"   Binary content: {chunk[:100]}")
                        elif isinstance(chunk, str):
                            logger.info(f"   Content preview: {chunk[:200]}")
                        else:
                            logger.info(f"   Object: {str(chunk)[:200]}")
                        yield chunk
                    logger.info(f"✅ Streaming completed: {chunk_count} chunks sent to user {user_id}")
                except Exception as e:
                    logger.error(f"❌ Error in stream generator: {str(e)}", exc_info=True)
                    # Yield error event in SSE format
                    error_msg = f'data: {{"error": "Stream error: {str(e)}"}}\n\n'
                    yield error_msg.encode()

            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # Non-streaming result - ChatKit SDK returns a proper response object
            # Return it directly without wrapping
            logger.info(f"📄 Non-streaming response for user {user_id}")
            return result

    except Exception as e:
        logger.error(f"❌ Error in chatkit_handler: {str(e)}", exc_info=True)
        # Return error response with proper CORS headers
        return Response(
            content=f'{{"error": "{str(e)}"}}',
            status_code=500,
            media_type="application/json",
        )

# MCP Server Architecture Note:
# The MCP server runs as a standalone Docker service (phaseiii-mcp-server)
# on port 8001 to avoid routing conflicts with FastAPI.
#
# Architecture:
# - MCP Server: http://mcp-server:8001 (Docker) or http://localhost:8001 (local)
# - Backend API: http://backend:8000 (Docker) or http://localhost:8000 (local)
# - Communication: Docker network (phaseiii-network)
# - Agent service connects via settings.mcp_server_url
#
# See docker-compose.yml for service configuration.
# See app/mcp/standalone.py for MCP server entry point.
