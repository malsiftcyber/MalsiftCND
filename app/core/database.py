"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# Create async engine for async operations
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create async session factory
from sqlalchemy.ext.asyncio import async_sessionmaker
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for models
Base = declarative_base()


async def init_db():
    """Initialize database tables"""
    from importlib import import_module

    model_modules = [
        "app.models.user",
        "app.models.scan",
        "app.models.device",
        "app.models.integration",
        "app.models.edr_integration",
        "app.models.device_correction",
        "app.models.discovery_agent",
        "app.models.tagging",
        "app.models.accuracy_ranking",
    ]

    for module_path in model_modules:
        try:
            import_module(module_path)
        except Exception as exc:
            # Log and continue so one bad import does not prevent start-up
            import logging
            logging.getLogger("database").warning(
                "Failed to import model module %s: %s", module_path, exc
            )

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        yield session
