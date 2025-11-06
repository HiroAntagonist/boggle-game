# ABOUTME: Database setup and configuration
# ABOUTME: Creates database engine and session management

from typing import Any, Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure SQLAlchemy logging to output SQL on single lines
# This prevents multi-line SQL statements from creating fragmented log entries
class SingleLineFormatter(logging.Formatter):
    """Custom formatter that replaces newlines with spaces in log messages."""
    def format(self, record: logging.LogRecord) -> str:
        # Replace newlines and multiple spaces with single space
        record.msg = ' '.join(str(record.msg).split())
        return super().format(record)

# Apply single-line formatter to SQLAlchemy's engine logger
sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
if sqlalchemy_logger.handlers:
    for handler in sqlalchemy_logger.handlers:
        handler.setFormatter(SingleLineFormatter('%(levelname)s:%(name)s:%(message)s'))
else:
    # Create handler if none exists
    handler = logging.StreamHandler()
    handler.setFormatter(SingleLineFormatter('%(levelname)s:%(name)s:%(message)s'))
    sqlalchemy_logger.addHandler(handler)

# DATABASE URL
# Format: sqlite:///path/to/file.db (/// for relative, //// for absolute)
# For PostgreSQL: postgresql://user:password@host:port/database
# Load from environment variable, with fallback to local SQLite for development
# Handle both postgres:// and postgresql:// prefixes
# Heroku and some services use postgres:// but SQLAlchemy needs postgresql://
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./boggle.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ENGINE
# The engine is the connection to the database
# echo=True prints all SQL commands (helpful for learning!)
# In production, set echo=False for better performance and cleaner logs
#
# Connection pool settings for PostgreSQL:
# - pool_pre_ping: Test connections before using them (handle stale connections)
# - pool_size: Number of connections to keep in the pool
# - max_overflow: Additional connections beyond pool_size
# - pool_recycle: Recycle connections after this many seconds (prevents stale connections)
# - connect_args: Database-specific connection arguments
connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL-specific settings
    connect_args = {
        "connect_timeout": 10,  # 10 second connection timeout
        "options": "-c statement_timeout=30000"  # 30 second statement timeout
    }
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # SQL logging disabled for cleaner logs
        pool_pre_ping=True,  # Test connection before using
        pool_size=5,  # Maintain 5 connections
        max_overflow=10,  # Allow 10 additional connections
        pool_recycle=3600,  # Recycle connections after 1 hour
        connect_args=connect_args
    )
else:
    # SQLite doesn't need connection pooling
    engine = create_engine(DATABASE_URL, echo=False)


# ENABLE FOREIGN KEY CONSTRAINTS FOR SQLITE
# SQLite doesn't enforce foreign keys by default, we must enable them
# PostgreSQL enforces foreign keys by default, so we only do this for SQLite
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn: Any, connection_record: Any) -> None:
        """Enable foreign key constraints for SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# SESSION FACTORY
# A session is like a "workspace" for database operations
# You open a session, do work, then close it
# sessionmaker creates sessions for us
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# BASE CLASS
# All our models will inherit from this
# This tells SQLAlchemy which classes are database tables
class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# HELPER FUNCTION
def get_db() -> Generator[Session, None, None]:
    """Get a database session.

    Usage:
        db = get_db()
        try:
            # do database work
            db.commit()
        finally:
            db.close()

    Or use as context manager:
        with get_db() as db:
            # do database work
            db.commit()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
