# ABOUTME: Initialize the database (create all tables)
# ABOUTME: Run this script to set up the database

from src.database import engine, Base
from src.models import User, Game, GamePlayer  # Import models so SQLAlchemy knows about them


def init_db() -> None:
    """Create all database tables.

    This looks at all classes that inherit from Base
    and creates the corresponding tables in the database.

    If tables already exist, this does nothing (safe to run multiple times).
    """
    print("Creating database tables...")

    # Create all tables
    # This translates our Python models into SQL CREATE TABLE statements
    Base.metadata.create_all(bind=engine)

    print("✓ Database tables created successfully!")


if __name__ == "__main__":
    init_db()
