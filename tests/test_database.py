# ABOUTME: Tests for database models and operations
# ABOUTME: Verifies User model CRUD operations work correctly

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from src.database import Base
from src.models import User


# TEST DATABASE SETUP
# We use a separate test database so we don't mess up real data
# :memory: means create database in RAM (faster, fresh for each test)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """Create a fresh database session for each test.

    This fixture:
    1. Creates a new in-memory database
    2. Creates all tables
    3. Provides a session to the test
    4. Cleans up after the test finishes
    """
    # Create engine for test database
    engine = create_engine(TEST_DATABASE_URL, echo=False)

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
        username="amritansh",
        email="a@example.com",
        password_hash="fake_hash_for_now"  # We'll do real password hashing later
    )

    # Add to database
    db_session.add(user)
    db_session.commit()

    # Verify user was saved
    assert user.id is not None  # UUID was auto-generated
    assert len(user.id) == 36  # UUIDs are exactly 36 characters
    assert user.username == "amritansh"
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
        username="alice",
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
    assert retrieved_user.username == "alice"
    assert retrieved_user.email == "alice@example.com"


def test_unique_username_constraint(db_session):
    """Test that usernames must be unique."""
    # Create first user
    user1 = User(
        username="bob",
        email="bob1@example.com",
        password_hash="fake_hash"
    )
    db_session.add(user1)
    db_session.commit()

    # Try to create second user with same username
    user2 = User(
        username="bob",  # Duplicate!
        email="bob2@example.com",
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
        username="charlie",
        email="charlie@example.com",
        password_hash="fake_hash"
    )
    db_session.add(user1)
    db_session.commit()

    # Try to create second user with same email
    user2 = User(
        username="charlie2",
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
            username=f"user{i}",
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
