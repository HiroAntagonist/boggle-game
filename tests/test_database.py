# ABOUTME: Tests for database models and operations
# ABOUTME: Verifies User model CRUD operations work correctly

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import uuid
import json

from src.database import Base
from src.models import User, Game, GamePlayer


# TEST DATABASE SETUP
# We use a separate test database so we don't mess up real data
# :memory: means create database in RAM (faster, fresh for each test)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """Create a fresh database session for each test.

    This fixture:
    1. Creates a new in-memory database
    2. Enables foreign key constraints (SQLite specific)
    3. Creates all tables
    4. Provides a session to the test
    5. Cleans up after the test finishes
    """
    # Create engine for test database
    engine = create_engine(TEST_DATABASE_URL, echo=False)

    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Provide session to test
    yield session

    # Cleanup after test
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_user(db_session):
    """Test creating a user with UUID."""
    # Create a user
    user = User(
        email="a@example.com",
        password_hash="fake_hash_for_now"  # We'll do real password hashing later
    )

    # Add to database
    db_session.add(user)
    db_session.commit()

    # Verify user was saved
    assert user.id is not None  # UUID was auto-generated
    assert len(user.id) == 36  # UUIDs are exactly 36 characters
    
    assert user.email == "a@example.com"

    # Verify it's a valid UUID format
    try:
        uuid.UUID(user.id)  # This will raise ValueError if not valid UUID
    except ValueError:
        pytest.fail(f"user.id is not a valid UUID: {user.id}")


def test_retrieve_user(db_session):
    """Test retrieving a user from database."""
    # Create and save user
    user = User(
        email="alice@example.com",
        password_hash="fake_hash"
    )
    db_session.add(user)
    db_session.commit()

    # Remember the user ID
    user_id = user.id

    # Retrieve user by ID
    retrieved_user = db_session.get(User, user_id)

    # Verify it's the same user
    assert retrieved_user is not None
    assert retrieved_user.id == user_id
    
    assert retrieved_user.email == "alice@example.com"


def test_unique_username_constraint(db_session):
    """Test that emails must be unique (username constraint is obsolete)."""
    # Create first user
    user1 = User(
        email="bob@example.com",
        password_hash="fake_hash"
    )
    db_session.add(user1)
    db_session.commit()

    # Try to create second user with same email
    user2 = User(
        email="bob@example.com",  # Duplicate!
        password_hash="fake_hash"
    )
    db_session.add(user2)

    # This should fail with an integrity error
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        db_session.commit()


def test_unique_email_constraint(db_session):
    """Test that emails must be unique."""
    # Create first user
    user1 = User(
        email="charlie@example.com",
        password_hash="fake_hash"
    )
    db_session.add(user1)
    db_session.commit()

    # Try to create second user with same email
    user2 = User(
        email="charlie@example.com",  # Duplicate!
        password_hash="fake_hash"
    )
    db_session.add(user2)

    # This should fail
    with pytest.raises(Exception):
        db_session.commit()


def test_uuid_is_not_guessable(db_session):
    """Test that UUIDs are random (not sequential)."""
    # Create multiple users
    users = []
    for i in range(5):
        user = User(
            email=f"user{i}@example.com",
            password_hash="fake_hash"
        )
        db_session.add(user)
        db_session.commit()
        users.append(user)

    # Get all UUIDs
    uuids = [user.id for user in users]

    # Verify they're all different
    assert len(set(uuids)) == 5  # All unique

    # Verify they're not sequential (like 1, 2, 3...)
    # UUIDs should be random strings, not numbers
    for uid in uuids:
        assert not uid.isdigit()  # Should contain letters/dashes, not just numbers


# ============================================================================
# GAME MODEL TESTS
# ============================================================================


def test_create_game(db_session):
    """Test creating a game with a creator."""
    # First create a user (games need a creator)
    user = User(
        email="a@example.com",
        password_hash="fake_hash"
    )
    db_session.add(user)
    db_session.commit()

    # Create a game
    game = Game(
        creator_id=user.id,
        board_size=4,
        time_limit=180
    )
    db_session.add(game)
    db_session.commit()

    # Verify game was created
    assert game.id is not None
    assert len(game.id) == 36  # UUID
    assert game.creator_id == user.id
    assert game.status == "waiting"  # Default status
    assert game.board_size == 4
    assert game.time_limit == 180
    assert game.board_state is None  # Null until game starts
    assert game.created_at is not None


def test_game_creator_relationship(db_session):
    """Test the relationship between Game and User (creator)."""
    # Create user
    user = User(
        email="alice@example.com",
        password_hash="fake_hash"
    )
    db_session.add(user)
    db_session.commit()

    # Create game
    game = Game(creator_id=user.id, board_size=5)
    db_session.add(game)
    db_session.commit()

    # Test relationship: game.creator should give us the User object
    assert game.creator is not None
    
    assert game.creator.id == user.id

    # Test reverse relationship: user.created_games should include this game
    assert len(user.created_games) == 1
    assert user.created_games[0].id == game.id


def test_game_foreign_key_constraint(db_session):
    """Test that we can't create a game with invalid creator_id."""
    # Try to create game with non-existent user ID
    game = Game(
        creator_id="fake-uuid-that-doesnt-exist",
        board_size=4
    )
    db_session.add(game)

    # This should fail with foreign key constraint violation
    with pytest.raises(Exception):
        db_session.commit()


def test_retrieve_game_by_id(db_session):
    """Test retrieving a game by its ID."""
    # Create user and game
    user = User(email="bob@example.com", password_hash="fake_hash")
    db_session.add(user)
    db_session.commit()

    game = Game(creator_id=user.id, board_size=4, time_limit=120)
    db_session.add(game)
    db_session.commit()

    game_id = game.id

    # Retrieve game by ID
    retrieved_game = db_session.get(Game, game_id)

    # Verify
    assert retrieved_game is not None
    assert retrieved_game.id == game_id
    assert retrieved_game.creator_id == user.id
    assert retrieved_game.time_limit == 120


def test_update_game_status(db_session):
    """Test updating game status from waiting to in_progress."""
    # Create user and game
    user = User(email="charlie@example.com", password_hash="fake_hash")
    db_session.add(user)
    db_session.commit()

    game = Game(creator_id=user.id)
    db_session.add(game)
    db_session.commit()

    # Verify initial status
    assert game.status == "waiting"

    # Update status
    game.status = "in_progress"
    game.board_state = json.dumps([["A", "B"], ["C", "D"]])
    db_session.commit()

    # Retrieve and verify
    retrieved_game = db_session.get(Game, game.id)
    assert retrieved_game.status == "in_progress"
    assert retrieved_game.board_state is not None


# ============================================================================
# GAMEPLAYER MODEL TESTS (Many-to-Many Join Table)
# ============================================================================


def test_add_player_to_game(db_session):
    """Test adding a player to a game via GamePlayer."""
    # Create user and game
    user = User(email="dave@example.com", password_hash="fake_hash")
    db_session.add(user)
    db_session.commit()

    game = Game(creator_id=user.id)
    db_session.add(game)
    db_session.commit()

    # Add player to game
    game_player = GamePlayer(
        game_id=game.id,
        user_id=user.id,
        score=0
    )
    db_session.add(game_player)
    db_session.commit()

    # Verify
    assert game_player.id is not None
    assert game_player.game_id == game.id
    assert game_player.user_id == user.id
    assert game_player.score == 0
    assert game_player.words_found == "[]"  # Default empty array


def test_multiple_players_in_game(db_session):
    """Test a game with multiple players."""
    # Create 3 users
    alice = User(email="alice@example.com", password_hash="fake_hash")
    bob = User(email="bob@example.com", password_hash="fake_hash")
    charlie = User(email="charlie@example.com", password_hash="fake_hash")

    db_session.add_all([alice, bob, charlie])
    db_session.commit()

    # Create game
    game = Game(creator_id=alice.id, board_size=4)
    db_session.add(game)
    db_session.commit()

    # Add all 3 players to game
    gp1 = GamePlayer(game_id=game.id, user_id=alice.id, score=42)
    gp2 = GamePlayer(game_id=game.id, user_id=bob.id, score=38)
    gp3 = GamePlayer(game_id=game.id, user_id=charlie.id, score=51)

    db_session.add_all([gp1, gp2, gp3])
    db_session.commit()

    # Verify game has 3 players
    assert len(game.players) == 3

    # Verify scores
    scores = [gp.score for gp in game.players]
    assert 42 in scores
    assert 38 in scores
    assert 51 in scores


def test_gameplayer_relationships(db_session):
    """Test GamePlayer → Game and GamePlayer → User relationships."""
    # Create user and game
    user = User(email="eve@example.com", password_hash="fake_hash")
    db_session.add(user)
    db_session.commit()

    game = Game(creator_id=user.id)
    db_session.add(game)
    db_session.commit()

    # Create GamePlayer
    game_player = GamePlayer(game_id=game.id, user_id=user.id, score=100)
    db_session.add(game_player)
    db_session.commit()

    # Test GamePlayer → Game relationship
    assert game_player.game is not None
    assert game_player.game.id == game.id
    assert game_player.game.creator_id == user.id

    # Test GamePlayer → User relationship
    assert game_player.user is not None
    
    assert game_player.user.id == user.id


def test_user_can_join_multiple_games(db_session):
    """Test that a user can be in multiple games (many-to-many)."""
    # Create 1 user
    user = User(email="frank@example.com", password_hash="fake_hash")
    db_session.add(user)
    db_session.commit()

    # Create 3 different games
    game1 = Game(creator_id=user.id, board_size=4)
    game2 = Game(creator_id=user.id, board_size=5)
    game3 = Game(creator_id=user.id, board_size=4)

    db_session.add_all([game1, game2, game3])
    db_session.commit()

    # User joins all 3 games
    gp1 = GamePlayer(game_id=game1.id, user_id=user.id, score=10)
    gp2 = GamePlayer(game_id=game2.id, user_id=user.id, score=20)
    gp3 = GamePlayer(game_id=game3.id, user_id=user.id, score=30)

    db_session.add_all([gp1, gp2, gp3])
    db_session.commit()

    # Verify each game has the user
    assert len(game1.players) == 1
    assert len(game2.players) == 1
    assert len(game3.players) == 1

    # Verify it's the same user in all games
    assert game1.players[0].user_id == user.id
    assert game2.players[0].user_id == user.id
    assert game3.players[0].user_id == user.id


def test_update_player_score_and_words(db_session):
    """Test updating a player's score and words during gameplay."""
    # Create user and game
    user = User(email="grace@example.com", password_hash="fake_hash")
    db_session.add(user)
    db_session.commit()

    game = Game(creator_id=user.id)
    db_session.add(game)
    db_session.commit()

    # Add player
    game_player = GamePlayer(game_id=game.id, user_id=user.id)
    db_session.add(game_player)
    db_session.commit()

    # Update score and words
    game_player.score = 25
    game_player.words_found = json.dumps(["CAT", "DOG", "HOUSE"])
    db_session.commit()

    # Retrieve and verify
    retrieved_gp = db_session.get(GamePlayer, game_player.id)
    assert retrieved_gp.score == 25

    words = json.loads(retrieved_gp.words_found)
    assert len(words) == 3
    assert "CAT" in words
    assert "DOG" in words
    assert "HOUSE" in words


def test_cascade_delete_game_players(db_session):
    """Test that deleting a game deletes all associated GamePlayer records."""
    # Create user and game
    user = User(email="henry@example.com", password_hash="fake_hash")
    db_session.add(user)
    db_session.commit()

    game = Game(creator_id=user.id)
    db_session.add(game)
    db_session.commit()

    # Add player
    game_player = GamePlayer(game_id=game.id, user_id=user.id)
    db_session.add(game_player)
    db_session.commit()

    game_player_id = game_player.id

    # Delete the game
    db_session.delete(game)
    db_session.commit()

    # GamePlayer should also be deleted (cascade)
    deleted_gp = db_session.get(GamePlayer, game_player_id)
    assert deleted_gp is None
