# ABOUTME: Database setup and configuration
# ABOUTME: Creates database engine and session management

from typing import Any, Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

# DATABASE URL
# Format: sqlite:///path/to/file.db
# /// means relative path, //// means absolute path
# This creates a file called "game.db" in the project root
DATABASE_URL = "sqlite:///game.db"

# ENGINE
# The engine is the connection to the database
# Think of it as opening a connection to a file
# echo=True prints all SQL commands (helpful for learning!)
engine = create_engine(DATABASE_URL, echo=True)


# ENABLE FOREIGN KEY CONSTRAINTS FOR SQLITE
# SQLite doesn't enforce foreign keys by default, we must enable them
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
