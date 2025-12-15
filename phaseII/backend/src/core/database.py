from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from .config import settings

# Determine which database URL to use
DATABASE_URL_TO_USE = (
    settings.TEST_DATABASE_URL if settings.ENVIRONMENT == "testing" else settings.DATABASE_URL
)

# SQLite specific connect arguments
connect_args = {}
if "sqlite" in DATABASE_URL_TO_USE:
    connect_args["check_same_thread"] = False

# PostgreSQL specific connect arguments
if "postgresql" in DATABASE_URL_TO_USE:
    connect_args["server_settings"] = {"timezone": "UTC"}
    # Set pooling parameters for PostgreSQL
    pooling_args = {
        "pool_size": settings.DB_POOL_MIN,
        "max_overflow": settings.DB_POOL_MAX - settings.DB_POOL_MIN,
        "pool_pre_ping": True,
        "pool_recycle": settings.DB_POOL_RECYCLE,
    }
else:
    # For SQLite and other databases
    pooling_args = {}

# Create async engine
engine = create_async_engine(
    DATABASE_URL_TO_USE,
    echo=settings.DEBUG,
    connect_args=connect_args,
    **pooling_args,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncSession:
    """FastAPI dependency that provides a database session."""
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """Initializes the database schema by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)