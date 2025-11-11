"""Database connection and engine management."""

import os
import logging
from sqlalchemy import create_engine, Engine
from typing import Optional

logger = logging.getLogger(__name__)

# Global engine instance
_db_engine: Optional[Engine] = None


def get_db_engine() -> Engine:
    """
    Get or create the SQLAlchemy database engine.

    Returns:
        SQLAlchemy Engine configured with DATABASE_URL from environment

    Raises:
        ValueError: If DATABASE_URL is not configured
    """
    global _db_engine

    if _db_engine is not None:
        return _db_engine

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        # Try POSTGRES_URL as fallback (for Railway)
        database_url = os.getenv("POSTGRES_URL")

    if not database_url:
        raise ValueError(
            "DATABASE_URL or POSTGRES_URL environment variable not configured. "
            "Cannot establish database connection."
        )

    try:
        # Create engine with connection pooling
        _db_engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL logging
            pool_pre_ping=True,  # Verify connection before using
            pool_recycle=3600,  # Recycle connections every hour
        )

        logger.info("✅ Database engine created successfully")
        return _db_engine

    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {e}")
        raise


def close_db_engine() -> None:
    """Close the database engine and cleanup resources."""
    global _db_engine

    if _db_engine is not None:
        _db_engine.dispose()
        _db_engine = None
        logger.info("Database engine closed")
