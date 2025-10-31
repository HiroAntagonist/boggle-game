# ABOUTME: Database setup and configuration
# ABOUTME: Creates database engine and session management

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

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
def get_db():
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
