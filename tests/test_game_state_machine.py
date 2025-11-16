# ABOUTME: Tests for game state machine (Phase 1: Core State Transitions)
# ABOUTME: Tests CREATED state, WAITING state, and ABANDONED transitions

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone

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

    # Disable rate limiting for tests
    app.state.limiter.enabled = False

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
    # Re-enable rate limiting after tests
    app.state.limiter.enabled = True


@pytest.fixture
def auth_token(client: TestClient) -> str:
    """Register a user and return their auth token."""
    # Register user
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 201

    # Login to get token
    login_response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


# ============================================================================
# PHASE 1 TESTS: CREATED STATE
# ============================================================================


def test_game_created_in_created_state(client: TestClient, auth_token: str):
    """Test that POST /games creates game in CREATED state."""
    response = client.post(
        "/games",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"board_size": 4, "time_limit": 300}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "created"
    assert data["board"] is not None  # Board should be generated
    assert data["friendly_code"] is not None  # Should have friendly code
    assert "game_id" in data


def test_created_game_has_no_players(client: TestClient, auth_token: str):
    """Test that CREATED game has no players yet."""
    response = client.post(
        "/games",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"board_size": 4, "time_limit": 300}
    )

    assert response.status_code == 201
    game_id = response.json()["game_id"]

    # Get game state
    response = client.get(
        f"/games/{game_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert data["player_count"] == 0
    assert data["started_at"] is None


# ============================================================================
# PHASE 1 TESTS: CREATED → WAITING TRANSITION
# ============================================================================


def test_first_player_join_transitions_to_waiting(client: TestClient, auth_token: str):
    """Test that first player joining transitions CREATED → WAITING."""
    # Create game in CREATED state
    response = client.post(
        "/games",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"board_size": 4, "time_limit": 300}
    )
    assert response.status_code == 201
    game_id = response.json()["game_id"]

    # First player joins
    response = client.post(
        f"/games/{game_id}/players",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"player_name": "TestPlayer"}
    )
    assert response.status_code == 201

    # Verify game is now in WAITING state
    response = client.get(
        f"/games/{game_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "waiting"
    assert data["player_count"] == 1


# ============================================================================
# PHASE 1 TESTS: WAITING → ABANDONED TRANSITION
# ============================================================================


def test_all_players_leave_waiting_transitions_to_abandoned(
    client: TestClient,
    auth_token: str
):
    """Test that all players leaving WAITING room deletes the game."""
    # Create game and join (CREATED → WAITING)
    response = client.post(
        "/games",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"board_size": 4, "time_limit": 300}
    )
    game_id = response.json()["game_id"]

    response = client.post(
        f"/games/{game_id}/players",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"player_name": "TestPlayer"}
    )
    player_id = response.json()["player_id"]

    # Verify in WAITING
    response = client.get(
        f"/games/{game_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.json()["status"] == "waiting"

    # Player leaves
    response = client.post(
        f"/games/{game_id}/leave",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"
    assert data["player_count"] == 0

    # Verify game is deleted (should return 404)
    response = client.get(
        f"/games/{game_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_abandoned_game_has_abandoned_at_timestamp(
    client: TestClient,
    auth_token: str
):
    """Test that empty WAITING game is deleted when last player leaves."""
    # Create game, join, then leave
    response = client.post(
        "/games",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"board_size": 4, "time_limit": 300}
    )
    game_id = response.json()["game_id"]

    response = client.post(
        f"/games/{game_id}/players",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"player_name": "TestPlayer"}
    )
    player_id = response.json()["player_id"]

    # Leave
    leave_response = client.post(
        f"/games/{game_id}/leave",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert leave_response.status_code == 200
    assert leave_response.json()["status"] == "deleted"

    # Verify game is deleted (404)
    response = client.get(
        f"/games/{game_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404
