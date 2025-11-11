# ABOUTME: Tests for FastAPI REST endpoints
# ABOUTME: Uses FastAPI TestClient for API testing

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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
    # StaticPool ensures all connections share the same in-memory database
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # CRITICAL: Share same in-memory database across connections
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


def auth_headers(token: str) -> dict:
    """Helper function to create Authorization headers."""
    return {"Authorization": f"Bearer {token}"}


def test_create_game_default_settings(client: TestClient) -> None:
    """Test creating a game with default settings."""
    token = create_test_user_and_login(client)
    response = client.post("/games", headers=auth_headers(token))

    assert response.status_code == 201
    data = response.json()

    assert "game_id" in data
    assert "board" in data
    assert "created_at" in data
    assert data["status"] == "waiting"

    # Default board should be 4x4
    assert len(data["board"]) == 4
    assert all(len(row) == 4 for row in data["board"])


def test_create_game_custom_settings(client: TestClient) -> None:
    """Test creating a game with custom settings."""
    token = create_test_user_and_login(client)
    response = client.post("/games", headers=auth_headers(token), json={
        "board_size": 5,
        "time_limit_seconds": 300,
        "max_players": 2
    })

    assert response.status_code == 201
    data = response.json()

    # Should have 5x5 board
    assert len(data["board"]) == 5
    assert all(len(row) == 5 for row in data["board"])


def test_create_game_invalid_board_size(client: TestClient) -> None:
    """Test that invalid board size is rejected."""
    token = create_test_user_and_login(client)
    response = client.post("/games", headers=auth_headers(token), json={
        "board_size": 3  # Invalid: must be 4 or 5
    })

    assert response.status_code == 422  # Validation error


def test_join_game_success(client: TestClient) -> None:
    """Test successfully joining a game."""
    token = create_test_user_and_login(client)

    # First create a game
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]

    # Join the game
    response = client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={
        "player_name": "Alice"
    })

    assert response.status_code == 201
    data = response.json()

    assert "player_id" in data
    assert data["player_name"] == "Alice"
    assert data["players"] == ["test"]  # Should show display_name (or email prefix), not player_name


def test_join_game_multiple_players(client: TestClient) -> None:
    """Test multiple players joining a game."""
    # Create two users
    token1 = create_test_user_and_login(client, email="alice@example.com")
    token2 = create_test_user_and_login(client, email="bob@example.com")

    # First user creates game
    create_response = client.post("/games", headers=auth_headers(token1))
    game_id = create_response.json()["game_id"]

    # First player joins
    response1 = client.post(f"/games/{game_id}/players", headers=auth_headers(token1), json={
        "player_name": "Alice"
    })
    assert response1.status_code == 201

    # Second player joins
    response2 = client.post(f"/games/{game_id}/players", headers=auth_headers(token2), json={
        "player_name": "Bob"
    })
    assert response2.status_code == 201
    data2 = response2.json()

    # Both players should be in the list (by display_name or email prefix)
    assert "alice" in data2["players"]
    assert "bob" in data2["players"]
    assert len(data2["players"]) == 2


def test_join_game_room_full(client: TestClient) -> None:
    """Test joining a full game."""
    # Create three users
    token1 = create_test_user_and_login(client, email="alice@example.com")
    token2 = create_test_user_and_login(client, email="bob@example.com")
    token3 = create_test_user_and_login(client, email="charlie@example.com")

    # Create game with max 2 players
    create_response = client.post("/games", headers=auth_headers(token1), json={"max_players": 2})
    game_id = create_response.json()["game_id"]

    # Add 2 players
    client.post(f"/games/{game_id}/players", headers=auth_headers(token1), json={"player_name": "Alice"})
    client.post(f"/games/{game_id}/players", headers=auth_headers(token2), json={"player_name": "Bob"})

    # Try to add third player
    response = client.post(f"/games/{game_id}/players", headers=auth_headers(token3), json={
        "player_name": "Charlie"
    })

    assert response.status_code == 400  # Bad request
    assert "full" in response.json()["detail"].lower()


def test_join_game_nonexistent(client: TestClient) -> None:
    """Test joining a game that doesn't exist."""
    token = create_test_user_and_login(client)
    response = client.post("/games/invalid-id/players", headers=auth_headers(token), json={
        "player_name": "Alice"
    })

    assert response.status_code == 404  # Not found


def test_get_game_state_success(client: TestClient) -> None:
    """Test getting game state."""
    token = create_test_user_and_login(client)

    # Create game
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]

    # Add a player
    client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={"player_name": "Alice"})

    # Get game state (with auth)
    response = client.get(f"/games/{game_id}", headers=auth_headers(token))

    assert response.status_code == 200
    data = response.json()

    assert data["game_id"] == game_id
    assert "board" in data
    assert data["status"] == "waiting"
    assert len(data["players"]) == 1
    assert data["players"][0] == "test"  # Should show display_name (or email prefix)


def test_get_game_state_nonexistent(client: TestClient) -> None:
    """Test getting state of nonexistent game."""
    token = create_test_user_and_login(client)
    response = client.get("/games/invalid-id", headers=auth_headers(token))

    assert response.status_code == 404


def test_start_game_success(client: TestClient) -> None:
    """Test successfully starting a game."""
    token = create_test_user_and_login(client)

    # Create game and add player
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]
    client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={"player_name": "Alice"})

    # Start the game (with auth)
    response = client.post(f"/games/{game_id}/start", headers=auth_headers(token))

    assert response.status_code == 200
    data = response.json()

    assert data["game_id"] == game_id
    assert data["status"] == "in_progress"
    assert "start_time" in data


def test_start_game_already_started(client: TestClient) -> None:
    """Test starting a game that's already in progress."""
    token = create_test_user_and_login(client)

    # Create, join, and start game
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]
    client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={"player_name": "Alice"})
    client.post(f"/games/{game_id}/start", headers=auth_headers(token))

    # Try to start again (with auth)
    response = client.post(f"/games/{game_id}/start", headers=auth_headers(token))

    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


def test_start_game_nonexistent(client: TestClient) -> None:
    """Test starting a nonexistent game."""
    token = create_test_user_and_login(client)
    response = client.post("/games/invalid-id/start", headers=auth_headers(token))

    assert response.status_code == 404


def test_get_results_success(client: TestClient) -> None:
    """Test getting game results."""
    # NOTE: This test will need to be updated once we implement word submission
    # For now, we'll just test that we can get results for a game
    token = create_test_user_and_login(client)

    # Create game
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]

    # Join game
    client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={"player_name": "Alice"})

    # Start game
    client.post(f"/games/{game_id}/start", headers=auth_headers(token))

    # Get results (with auth)
    response = client.get(f"/games/{game_id}/results", headers=auth_headers(token))

    assert response.status_code == 200
    data = response.json()

    assert "players" in data
    assert "duplicates" in data


def test_get_results_game_not_started(client: TestClient) -> None:
    """Test getting results for game that hasn't started."""
    token = create_test_user_and_login(client)

    # Create game but don't start (need to join to be a participant)
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]
    client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={"player_name": "Alice"})

    response = client.get(f"/games/{game_id}/results", headers=auth_headers(token))

    # Should work but have no words
    assert response.status_code == 200


def test_get_results_nonexistent_game(client: TestClient) -> None:
    """Test getting results for nonexistent game."""
    token = create_test_user_and_login(client)
    response = client.get("/games/invalid-id/results", headers=auth_headers(token))

    assert response.status_code == 404


def test_authorization_non_participant_cannot_view_game(client: TestClient) -> None:
    """Test that non-participants cannot view game state."""
    # Create two users
    token1 = create_test_user_and_login(client, email="alice@example.com")
    token2 = create_test_user_and_login(client, email="bob@example.com")

    # Alice creates and joins a game
    create_response = client.post("/games", headers=auth_headers(token1))
    game_id = create_response.json()["game_id"]
    client.post(f"/games/{game_id}/players", headers=auth_headers(token1), json={"player_name": "Alice"})

    # Bob (not a participant) tries to view the game
    response = client.get(f"/games/{game_id}", headers=auth_headers(token2))

    assert response.status_code == 403
    assert "not a participant" in response.json()["detail"].lower()


def test_authorization_non_participant_cannot_start_game(client: TestClient) -> None:
    """Test that non-participants cannot start a game."""
    # Create two users
    token1 = create_test_user_and_login(client, email="alice@example.com")
    token2 = create_test_user_and_login(client, email="bob@example.com")

    # Alice creates and joins a game
    create_response = client.post("/games", headers=auth_headers(token1))
    game_id = create_response.json()["game_id"]
    client.post(f"/games/{game_id}/players", headers=auth_headers(token1), json={"player_name": "Alice"})

    # Bob (not a participant) tries to start the game
    response = client.post(f"/games/{game_id}/start", headers=auth_headers(token2))

    assert response.status_code == 403
    assert "not a participant" in response.json()["detail"].lower()


def test_authorization_non_participant_cannot_view_results(client: TestClient) -> None:
    """Test that non-participants cannot view game results."""
    # Create two users
    token1 = create_test_user_and_login(client, email="alice@example.com")
    token2 = create_test_user_and_login(client, email="bob@example.com")

    # Alice creates, joins, and starts a game
    create_response = client.post("/games", headers=auth_headers(token1))
    game_id = create_response.json()["game_id"]
    client.post(f"/games/{game_id}/players", headers=auth_headers(token1), json={"player_name": "Alice"})
    client.post(f"/games/{game_id}/start", headers=auth_headers(token1))

    # Bob (not a participant) tries to view results
    response = client.get(f"/games/{game_id}/results", headers=auth_headers(token2))

    assert response.status_code == 403
    assert "not a participant" in response.json()["detail"].lower()
