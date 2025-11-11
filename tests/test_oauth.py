# ABOUTME: Tests for Google OAuth authentication endpoint
# ABOUTME: Verifies OAuth login, user creation, and account linking

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch, Mock

from src.api_server import app
from src.database import Base, get_db
from src.models import User, Game, GamePlayer


# TEST DATABASE SETUP
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def client():
    """Create a test client with a fresh in-memory database for each test."""
    _ = (User, Game, GamePlayer)

    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


# ============================================================================
# GOOGLE OAUTH TESTS
# ============================================================================


@patch('src.api_server.id_token.verify_oauth2_token')
def test_google_oauth_new_user(mock_verify, client: TestClient) -> None:
    """Test Google OAuth creates new user if doesn't exist."""
    # Mock Google token verification
    mock_verify.return_value = {
        'email': 'newuser@gmail.com',
        'sub': 'google-id-123',
        'name': 'New User'
    }

    # Login with Google
    response = client.post(
        "/auth/google",
        json={"id_token": "fake-google-token"}
    )

    assert response.status_code == 200
    data = response.json()

    # Should return JWT token
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Token should be valid JWT format
    token = data["access_token"]
    assert token.count(".") == 2


@patch('src.api_server.id_token.verify_oauth2_token')
def test_google_oauth_links_to_existing_email_password_user(mock_verify, client: TestClient) -> None:
    """Test Google OAuth links to existing user with same email."""
    # First, register a user with email/password
    register_response = client.post(
        "/auth/register",
        json={
            "email": "existing@gmail.com",
            "password": "password123"
        }
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["user_id"]

    # Mock Google token verification with same email
    mock_verify.return_value = {
        'email': 'existing@gmail.com',
        'sub': 'google-id-456',
        'name': 'Existing User'
    }

    # Login with Google
    response = client.post(
        "/auth/google",
        json={"id_token": "fake-google-token"}
    )

    assert response.status_code == 200
    data = response.json()

    # Should return JWT token
    assert "access_token" in data

    # Decode token to verify it's the same user
    from src.auth import decode_access_token
    decoded = decode_access_token(data["access_token"])
    assert decoded["user_id"] == user_id
    assert decoded["email"] == "existing@gmail.com"


@patch('src.api_server.id_token.verify_oauth2_token')
def test_google_oauth_existing_oauth_user(mock_verify, client: TestClient) -> None:
    """Test Google OAuth works for user who already used OAuth."""
    # First OAuth login (creates user)
    mock_verify.return_value = {
        'email': 'oauth@gmail.com',
        'sub': 'google-id-789',
        'name': 'OAuth User'
    }

    first_response = client.post(
        "/auth/google",
        json={"id_token": "fake-google-token"}
    )
    assert first_response.status_code == 200
    first_token = first_response.json()["access_token"]

    # Second OAuth login (same user)
    second_response = client.post(
        "/auth/google",
        json={"id_token": "fake-google-token"}
    )
    assert second_response.status_code == 200
    second_token = second_response.json()["access_token"]

    # Both tokens should work and point to same user
    from src.auth import decode_access_token
    first_decoded = decode_access_token(first_token)
    second_decoded = decode_access_token(second_token)

    assert first_decoded["user_id"] == second_decoded["user_id"]
    assert first_decoded["email"] == "oauth@gmail.com"


@patch('src.api_server.id_token.verify_oauth2_token')
def test_google_oauth_invalid_token(mock_verify, client: TestClient) -> None:
    """Test Google OAuth fails with invalid token."""
    # Mock Google token verification failure
    mock_verify.side_effect = ValueError("Invalid token")

    response = client.post(
        "/auth/google",
        json={"id_token": "invalid-token"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower()


@patch('src.api_server.id_token.verify_oauth2_token')
def test_google_oauth_missing_email(mock_verify, client: TestClient) -> None:
    """Test Google OAuth fails if token missing email."""
    # Mock Google token without email
    mock_verify.return_value = {
        'sub': 'google-id-999',
        'name': 'No Email User'
        # Missing 'email' field!
    }

    response = client.post(
        "/auth/google",
        json={"id_token": "fake-token"}
    )

    assert response.status_code == 400
    data = response.json()
    assert "email" in data["detail"].lower()


@patch('src.api_server.id_token.verify_oauth2_token')
def test_google_oauth_user_has_no_password(mock_verify, client: TestClient) -> None:
    """Test that OAuth-created user has no password set."""
    mock_verify.return_value = {
        'email': 'oauth_only@gmail.com',
        'sub': 'google-id-111',
        'name': 'OAuth Only User'
    }

    # Create user via OAuth
    oauth_response = client.post(
        "/auth/google",
        json={"id_token": "fake-token"}
    )
    assert oauth_response.status_code == 200

    # Try to login with password (should fail - no password set)
    login_response = client.post(
        "/auth/login",
        json={
            "email": "oauth_only@gmail.com",
            "password": "anypassword"
        }
    )

    assert login_response.status_code == 401
    # User exists but has no password_hash


@patch('src.api_server.id_token.verify_oauth2_token')
def test_google_oauth_user_can_create_game(mock_verify, client: TestClient) -> None:
    """Test that OAuth-authenticated user can create games."""
    mock_verify.return_value = {
        'email': 'gamer@gmail.com',
        'sub': 'google-id-222',
        'name': 'Gamer'
    }

    # Login with Google
    oauth_response = client.post(
        "/auth/google",
        json={"id_token": "fake-token"}
    )
    assert oauth_response.status_code == 200
    token = oauth_response.json()["access_token"]

    # Create game with OAuth token
    game_response = client.post(
        "/games",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert game_response.status_code == 201
    data = game_response.json()
    assert "game_id" in data
    assert "board" in data


@patch('src.api_server.id_token.verify_oauth2_token')
def test_google_oauth_display_name_from_profile(mock_verify, client: TestClient) -> None:
    """Test that OAuth user gets display_name from Google profile."""
    mock_verify.return_value = {
        'email': 'john@gmail.com',
        'sub': 'google-id-333',
        'name': 'John Doe'
    }

    # Login with Google
    oauth_response = client.post(
        "/auth/google",
        json={"id_token": "fake-token"}
    )
    assert oauth_response.status_code == 200
    token = oauth_response.json()["access_token"]

    # Get user info
    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert me_response.status_code == 200
    data = me_response.json()
    assert data["display_name"] == "John Doe"
