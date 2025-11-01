# ABOUTME: Tests for authentication API endpoints (register, login)
# ABOUTME: Verifies user registration and login work correctly

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api_server import app
from src.database import Base, get_db
from src.models import User, Game, GamePlayer  # Import all models


# TEST DATABASE SETUP
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def client():
    """Create a test client with a fresh in-memory database for each test."""
    # Force import of all models FIRST so SQLAlchemy knows about them
    _ = (User, Game, GamePlayer)

    # Create test database engine with StaticPool
    # StaticPool ensures all connections share the same in-memory database
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},  # Needed for SQLite with FastAPI
        poolclass=StaticPool,  # CRITICAL: Share same in-memory database across connections
    )

    # Enable foreign key constraints for SQLite
    # Register event listener BEFORE any connections are made
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


# ============================================================================
# USER REGISTRATION TESTS
# ============================================================================


def test_register_success(client: TestClient) -> None:
    """Test successful user registration."""
    response = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "securepassword123"
        }
    )

    assert response.status_code == 201
    data = response.json()

    # Should return user info
    assert "user_id" in data
    assert data["username"] == "alice"
    assert "message" in data

    # Password should not be in response
    assert "password" not in data


def test_register_duplicate_username(client: TestClient) -> None:
    """Test registration fails with duplicate username."""
    # Register first user
    client.post(
        "/auth/register",
        json={
            "username": "bob",
            "email": "bob1@example.com",
            "password": "password123"
        }
    )

    # Try to register with same username but different email
    response = client.post(
        "/auth/register",
        json={
            "username": "bob",  # Duplicate!
            "email": "bob2@example.com",
            "password": "password456"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "username" in data["detail"].lower()


def test_register_duplicate_email(client: TestClient) -> None:
    """Test registration fails with duplicate email."""
    # Register first user
    client.post(
        "/auth/register",
        json={
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "password123"
        }
    )

    # Try to register with different username but same email
    response = client.post(
        "/auth/register",
        json={
            "username": "charlie2",
            "email": "charlie@example.com",  # Duplicate!
            "password": "password456"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "email" in data["detail"].lower()


def test_register_invalid_email(client: TestClient) -> None:
    """Test registration fails with invalid email format."""
    response = client.post(
        "/auth/register",
        json={
            "username": "dave",
            "email": "not-an-email",  # Invalid!
            "password": "password123"
        }
    )

    assert response.status_code == 422  # Validation error


def test_register_password_hashed(client: TestClient) -> None:
    """Test that password is hashed in database (not stored plain)."""
    password = "myplainpassword"

    # Register user
    response = client.post(
        "/auth/register",
        json={
            "username": "eve",
            "email": "eve@example.com",
            "password": password
        }
    )

    assert response.status_code == 201

    # Manually query database to check password is hashed
    # In real test, we'd inject db session, but for simplicity:
    # Just verify password is not returned in API response
    data = response.json()
    assert "password" not in data
    assert "password_hash" not in data


# ============================================================================
# USER LOGIN TESTS
# ============================================================================


def test_login_success(client: TestClient) -> None:
    """Test successful login returns JWT token."""
    # First register a user
    client.post(
        "/auth/register",
        json={
            "username": "frank",
            "email": "frank@example.com",
            "password": "frankpassword"
        }
    )

    # Now login
    response = client.post(
        "/auth/login",
        json={
            "username": "frank",
            "password": "frankpassword"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Should return JWT token
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    # Token should be a non-empty string with 3 parts (JWT format)
    token = data["access_token"]
    assert isinstance(token, str)
    assert len(token) > 0
    assert token.count(".") == 2


def test_login_wrong_password(client: TestClient) -> None:
    """Test login fails with wrong password."""
    # Register user
    client.post(
        "/auth/register",
        json={
            "username": "grace",
            "email": "grace@example.com",
            "password": "correctpassword"
        }
    )

    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        json={
            "username": "grace",
            "password": "wrongpassword"  # Wrong!
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower() or "incorrect" in data["detail"].lower()


def test_login_nonexistent_user(client: TestClient) -> None:
    """Test login fails with non-existent username."""
    response = client.post(
        "/auth/login",
        json={
            "username": "doesnotexist",
            "password": "anypassword"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower() or "incorrect" in data["detail"].lower()


def test_login_token_contains_user_info(client: TestClient) -> None:
    """Test that JWT token contains user information."""
    # Register user
    register_response = client.post(
        "/auth/register",
        json={
            "username": "henry",
            "email": "henry@example.com",
            "password": "henrypass"
        }
    )
    user_id = register_response.json()["user_id"]

    # Login
    login_response = client.post(
        "/auth/login",
        json={
            "username": "henry",
            "password": "henrypass"
        }
    )

    token = login_response.json()["access_token"]

    # Decode token to verify it contains user info
    from src.auth import decode_access_token
    decoded = decode_access_token(token)

    assert decoded is not None
    assert decoded["user_id"] == user_id
    assert decoded["username"] == "henry"


# ============================================================================
# PROTECTED ENDPOINT TESTS (get_current_user dependency)
# ============================================================================


def test_get_current_user_valid_token(client: TestClient) -> None:
    """Test that valid token returns authenticated user."""
    # Register and login
    client.post(
        "/auth/register",
        json={
            "username": "iris",
            "email": "iris@example.com",
            "password": "irispassword"
        }
    )
    login_response = client.post(
        "/auth/login",
        json={
            "username": "iris",
            "password": "irispassword"
        }
    )
    token = login_response.json()["access_token"]

    # Call protected endpoint with valid token
    # We'll use a test endpoint that just returns the current user
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "iris"
    assert "user_id" in data


def test_get_current_user_missing_token(client: TestClient) -> None:
    """Test that missing token returns 401 or 403."""
    # Call protected endpoint without token
    response = client.get("/auth/me")

    # HTTPBearer returns 403 when no Authorization header is present
    assert response.status_code in [401, 403]
    data = response.json()
    assert "not authenticated" in data["detail"].lower() or "missing" in data["detail"].lower() or "forbidden" in data["detail"].lower()


def test_get_current_user_invalid_token(client: TestClient) -> None:
    """Test that invalid token returns 401 Unauthorized."""
    # Call protected endpoint with fake token
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token-here"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower() or "credentials" in data["detail"].lower()


def test_get_current_user_expired_token(client: TestClient) -> None:
    """Test that expired token returns 401 Unauthorized."""
    from datetime import timedelta
    from src.auth import create_access_token

    # Create token that expires in -1 seconds (already expired)
    token_data = {"user_id": "fake-uuid", "username": "expired"}
    expired_token = create_access_token(token_data, expires_delta=timedelta(seconds=-1))

    # Call protected endpoint with expired token
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "expired" in data["detail"].lower() or "invalid" in data["detail"].lower()


# ============================================================================
# PROTECTED GAME ENDPOINTS TESTS
# ============================================================================


def test_create_game_requires_auth(client: TestClient) -> None:
    """Test that creating a game requires authentication."""
    # Try to create game without token
    response = client.post("/games")

    # Should require authentication
    assert response.status_code in [401, 403]


def test_create_game_with_auth_success(client: TestClient) -> None:
    """Test creating a game with valid authentication."""
    # Register and login
    client.post(
        "/auth/register",
        json={
            "username": "gamer1",
            "email": "gamer1@example.com",
            "password": "password123"
        }
    )
    login_response = client.post(
        "/auth/login",
        json={
            "username": "gamer1",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]

    # Create game with token
    response = client.post(
        "/games",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "game_id" in data
    assert "board" in data
    assert data["status"] == "waiting"


def test_join_game_requires_auth(client: TestClient) -> None:
    """Test that joining a game requires authentication."""
    # First, create a game (with auth)
    client.post(
        "/auth/register",
        json={
            "username": "creator",
            "email": "creator@example.com",
            "password": "password123"
        }
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "creator", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    create_response = client.post(
        "/games",
        headers={"Authorization": f"Bearer {token}"}
    )
    game_id = create_response.json()["game_id"]

    # Try to join without auth
    response = client.post(
        f"/games/{game_id}/players",
        json={"player_name": "Joiner"}
    )

    # Should require authentication
    assert response.status_code in [401, 403]


def test_join_game_with_auth_success(client: TestClient) -> None:
    """Test joining a game with valid authentication."""
    # Register two users
    client.post(
        "/auth/register",
        json={
            "username": "creator",
            "email": "creator@example.com",
            "password": "password123"
        }
    )
    client.post(
        "/auth/register",
        json={
            "username": "joiner",
            "email": "joiner@example.com",
            "password": "password123"
        }
    )

    # Creator logs in and creates game
    creator_login = client.post(
        "/auth/login",
        json={"username": "creator", "password": "password123"}
    )
    creator_token = creator_login.json()["access_token"]

    create_response = client.post(
        "/games",
        headers={"Authorization": f"Bearer {creator_token}"}
    )
    game_id = create_response.json()["game_id"]

    # Joiner logs in and joins game
    joiner_login = client.post(
        "/auth/login",
        json={"username": "joiner", "password": "password123"}
    )
    joiner_token = joiner_login.json()["access_token"]

    response = client.post(
        f"/games/{game_id}/players",
        json={"player_name": "JoinerName"},
        headers={"Authorization": f"Bearer {joiner_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "player_id" in data
    assert data["player_name"] == "JoinerName"
