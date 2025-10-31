# ABOUTME: Database models (tables) for the application
# ABOUTME: Defines User, Game, and related tables

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import Optional
import uuid

from src.database import Base


class User(Base):
    """User account model.

    This becomes a database table called 'users' with columns:
    - id (UUID primary key, not guessable for security)
    - username (unique, required)
    - email (unique, required)
    - password_hash (required)
    - created_at (timestamp)
    """

    # TABLE NAME
    # By default SQLAlchemy uses class name lowercase + 's'
    # User -> users, Game -> games
    __tablename__ = "users"

    # COLUMNS
    # Mapped[type] tells Python's type checker what type this is
    # mapped_column() tells SQLAlchemy this is a database column

    # Primary Key - UUID for security (not guessable)
    # uuid.uuid4() generates a random UUID like: 550e8400-e29b-41d4-a716-446655440000
    # We store as string because SQLite doesn't have native UUID type
    # str(uuid.uuid4()) converts UUID object to string
    id: Mapped[str] = mapped_column(
        String(36),  # UUIDs are exactly 36 characters
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Username - must be unique and can't be null
    # String(50) means max 50 characters
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Email - must be unique and can't be null
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Password hash - we NEVER store plain passwords!
    # We'll hash passwords before storing (Week 5 Part 2)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Created timestamp - when user registered
    # default=lambda: datetime.now(timezone.utc) sets it automatically
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # String representation - useful for debugging
    # When you print a User object, you'll see: <User(username='amritansh')>
    def __repr__(self) -> str:
        return f"<User(username='{self.username}')>"
