# ABOUTME: Tests for duplicate friendly code handling
# ABOUTME: Verifies that concurrent game creation with duplicate codes is handled correctly

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from src.api_server import app
from src.database import Base, get_db
from src.models import User, Game, GamePlayer


# TEST DATABASE SETUP
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def client():
    """Create a test client with a fresh in-memory database for each test."""
    # Force import of all models FIRST so SQLAlchemy knows about them
    _ = (User, Game, GamePlayer)

    # Create test database engine with StaticPool
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session maker
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # Override the get_db dependency to use test database
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def create_test_user_and_login(client: TestClient, email: str = "test@example.com", password: str = "testpass123", display_name: str | None = None) -> str:
    """Helper function to create a user and return their auth token."""
    # Register user
    register_data = {"email": email, "password": password}
    if display_name is not None:
        register_data["display_name"] = display_name

    client.post("/auth/register", json=register_data)

    # Login to get token
    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )

    return login_response.json()["access_token"]


def test_duplicate_friendly_code_retries_successfully(client: TestClient) -> None:
    """Test that duplicate friendly codes are handled by retrying with a new code."""
    token = create_test_user_and_login(client)

    # Mock generate_friendly_code to return duplicate on first call, unique on second
    call_count = 0
    def mock_generate_code(db):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return "1234-5678"  # First call returns this code
        else:
            return "8765-4321"  # Second call returns different code

    with patch("src.api_server.generate_friendly_code", side_effect=mock_generate_code):
        # Create first game - should succeed with code "1234-5678"
        response1 = client.post(
            "/games",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response1.status_code == 201
        assert response1.json()["friendly_code"] == "1234-5678"

        # Create second game - first attempt will try "1234-5678" (duplicate),
        # should catch IntegrityError and retry with "8765-4321"
        response2 = client.post(
            "/games",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response2.status_code == 201
        # The second game should have gotten a different code after retry
        assert response2.json()["friendly_code"] == "8765-4321"


def test_duplicate_friendly_code_exhausts_retries(client: TestClient) -> None:
    """Test that after max retry attempts, a 500 error is returned."""
    token = create_test_user_and_login(client)

    # Mock generate_friendly_code to always return the same code
    def mock_generate_same_code(db):
        return "1234-5678"

    with patch("src.api_server.generate_friendly_code", side_effect=mock_generate_same_code):
        # Create first game - should succeed
        response1 = client.post(
            "/games",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response1.status_code == 201

        # Try to create second game - should fail after max retries
        response2 = client.post(
            "/games",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response2.status_code == 500
        assert "Unable to generate unique game code" in response2.json()["detail"]
