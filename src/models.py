# ABOUTME: Database models (tables) for the application
# ABOUTME: Defines User, Game, and related tables

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import Optional, List
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

    # RELATIONSHIPS
    # This doesn't create a column! It tells SQLAlchemy how to JOIN tables
    # When you access user.created_games, SQLAlchemy will fetch all games where creator_id = user.id
    created_games: Mapped[List["Game"]] = relationship(
        "Game",
        back_populates="creator",
        foreign_keys="Game.creator_id"
    )

    # String representation - useful for debugging
    # When you print a User object, you'll see: <User(username='amritansh')>
    def __repr__(self) -> str:
        return f"<User(username='{self.username}')>"


class Game(Base):
    """Game instance model.

    This becomes a database table called 'games' with columns:
    - id (UUID primary key)
    - creator_id (foreign key to users table)
    - status (waiting, in_progress, completed)
    - board_size (4 or 5)
    - time_limit (seconds, nullable)
    - board_state (JSON string of the board)
    - created_at (timestamp)
    - started_at (timestamp, nullable)
    - ended_at (timestamp, nullable)
    """

    __tablename__ = "games"

    # PRIMARY KEY
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # FRIENDLY CODE - Human-readable game code (XXXX-XXXX format)
    # Indexed and unique for fast lookups when joining by code
    friendly_code: Mapped[Optional[str]] = mapped_column(
        String(9),  # Format: XXXX-XXXX (8 digits + 1 dash)
        unique=True,
        nullable=True,
        index=True
    )

    # FOREIGN KEY - References users.id
    # This creates a column that MUST contain a valid user ID
    # ForeignKey("users.id") tells SQLAlchemy this column references the users table
    creator_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False
    )

    # GAME CONFIGURATION
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="waiting"  # waiting, in_progress, finished
    )

    board_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=4
    )

    time_limit: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True  # Optional: can be None (no time limit)
    )

    max_players: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=4  # Default to 4 players max
    )

    min_word_length: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3  # Minimum word length (standard Boggle rule)
    )

    # GAME STATE
    # Text type for longer strings (vs String which has a length limit)
    # We'll store the board as JSON: '[["A","B","C","D"],["E","F","G","H"],...]'
    board_state: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True  # Null until game starts
    )

    # TIMESTAMPS
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True  # Null until game starts
    )

    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True  # Null until game ends
    )

    # RELATIONSHIPS
    # These don't create columns! They tell SQLAlchemy how to navigate between tables

    # ONE-TO-MANY: creator relationship
    # When you access game.creator, SQLAlchemy does: SELECT * FROM users WHERE id = game.creator_id
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_games",
        foreign_keys=[creator_id]
    )

    # MANY-TO-MANY: players relationship (via GamePlayer join table)
    # When you access game.players, SQLAlchemy does complex JOIN through game_players table
    # This will give you a list of GamePlayer objects (not User objects!)
    players: Mapped[List["GamePlayer"]] = relationship(
        "GamePlayer",
        back_populates="game",
        cascade="all, delete-orphan"  # If game is deleted, delete all GamePlayer records
    )

    def __repr__(self) -> str:
        return f"<Game(id='{self.id[:8]}...', status='{self.status}')>"


class GamePlayer(Base):
    """Join table linking users to games with their scores.

    This is the MANY-TO-MANY join table.

    Example: Game #1 has 3 players:
    - GamePlayer(game_id=game1_id, user_id=alice_id, score=42)
    - GamePlayer(game_id=game1_id, user_id=bob_id, score=38)
    - GamePlayer(game_id=game1_id, user_id=charlie_id, score=51)

    This becomes a database table called 'game_players' with columns:
    - id (UUID primary key)
    - game_id (foreign key to games table)
    - user_id (foreign key to users table)
    - score (player's score in this game)
    - words_found (JSON array of words this player found)
    - joined_at (timestamp)
    """

    __tablename__ = "game_players"

    # PRIMARY KEY
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # FOREIGN KEY - References games.id
    # This player is in which game?
    game_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("games.id"),
        nullable=False
    )

    # FOREIGN KEY - References users.id
    # Which user is this player?
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False
    )

    # GAME DATA
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    # Store words as JSON array: '["CAT", "DOG", "HOUSE"]'
    words_found: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default="[]"  # Empty JSON array
    )

    # TIMESTAMP
    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # RELATIONSHIPS
    # These allow us to navigate: GamePlayer → Game and GamePlayer → User

    # MANY-TO-ONE: game relationship
    # When you access game_player.game, SQLAlchemy does: SELECT * FROM games WHERE id = game_player.game_id
    game: Mapped["Game"] = relationship(
        "Game",
        back_populates="players"
    )

    # MANY-TO-ONE: user relationship
    # When you access game_player.user, SQLAlchemy does: SELECT * FROM users WHERE id = game_player.user_id
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<GamePlayer(user_id='{self.user_id[:8]}...', game_id='{self.game_id[:8]}...', score={self.score})>"
