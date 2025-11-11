# ABOUTME: Tests for WebSocket functionality in hybrid API
# ABOUTME: Verifies real-time game updates work correctly

import pytest
import json
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

    # Disable rate limiting for tests
    app.state.limiter.enabled = False

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
    # Re-enable rate limiting after tests
    app.state.limiter.enabled = True


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


def test_websocket_requires_valid_game(client: TestClient) -> None:
    """Test that WebSocket connection requires valid game ID."""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/invalid-game/player-123"):
            pass  # Should fail to connect


def test_websocket_connection_success(client: TestClient) -> None:
    """Test successful WebSocket connection after game creation."""
    token = create_test_user_and_login(client)

    # Create game via REST
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]

    # Join game via REST
    join_response = client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={"player_name": "Alice"})
    player_id = join_response.json()["player_id"]

    # Start game via REST
    client.post(f"/games/{game_id}/start", headers=auth_headers(token))

    # Connect via WebSocket
    with client.websocket_connect(f"/ws/{game_id}/{player_id}") as websocket:
        # Request game state
        websocket.send_text(json.dumps({"type": "get_state"}))

        # Receive response
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "game_state"
        assert message["status"] == "in_progress"
        assert message["player_count"] == 1


def test_websocket_word_submission(client: TestClient) -> None:
    """Test word submission via WebSocket."""
    token = create_test_user_and_login(client)

    # Create and setup game
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]

    join_response = client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={"player_name": "Alice"})
    player_id = join_response.json()["player_id"]

    client.post(f"/games/{game_id}/start", headers=auth_headers(token))

    # Connect via WebSocket
    with client.websocket_connect(f"/ws/{game_id}/{player_id}") as websocket:
        # Submit a word (may or may not be valid depending on board)
        websocket.send_text(json.dumps({"type": "submit_word", "word": "TEST"}))

        # Receive response
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "word_result"
        assert "word" in message
        assert "valid" in message
        assert "score" in message
        assert "message" in message


def test_websocket_multiplayer_broadcast(client: TestClient) -> None:
    """Test that word submissions are broadcast to other players."""
    # Create two users
    token1 = create_test_user_and_login(client, email="alice@example.com")
    token2 = create_test_user_and_login(client, email="bob@example.com")

    # Create game with 2 players
    create_response = client.post("/games", headers=auth_headers(token1))
    game_id = create_response.json()["game_id"]

    alice_response = client.post(f"/games/{game_id}/players", headers=auth_headers(token1), json={"player_name": "Alice"})
    alice_id = alice_response.json()["player_id"]

    bob_response = client.post(f"/games/{game_id}/players", headers=auth_headers(token2), json={"player_name": "Bob"})
    bob_id = bob_response.json()["player_id"]

    client.post(f"/games/{game_id}/start", headers=auth_headers(token1))

    # Connect both players via WebSocket
    with client.websocket_connect(f"/ws/{game_id}/{alice_id}") as alice_ws:
        with client.websocket_connect(f"/ws/{game_id}/{bob_id}") as bob_ws:
            # Alice sees Bob connected
            data = alice_ws.receive_text()
            message = json.loads(data)
            assert message["type"] == "player_connected"
            assert message["player_name"] == "bob"  # Should show display_name (or email prefix)

            # Alice submits a word
            alice_ws.send_text(json.dumps({"type": "submit_word", "word": "TEST"}))

            # Alice gets her result
            alice_result = json.loads(alice_ws.receive_text())
            assert alice_result["type"] == "word_result"

            # If word was valid, Bob should see broadcast
            if alice_result["valid"]:
                bob_broadcast = json.loads(bob_ws.receive_text())
                assert bob_broadcast["type"] == "word_submitted"
                assert bob_broadcast["player_name"] == "alice"  # Should show display_name (or email prefix)


def test_websocket_invalid_message_format(client: TestClient) -> None:
    """Test that invalid WebSocket messages are rejected with error."""
    token = create_test_user_and_login(client)

    # Create and setup game
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]

    join_response = client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={"player_name": "Alice"})
    player_id = join_response.json()["player_id"]

    client.post(f"/games/{game_id}/start", headers=auth_headers(token))

    # Connect via WebSocket
    with client.websocket_connect(f"/ws/{game_id}/{player_id}") as websocket:
        # Send invalid message (missing required field)
        websocket.send_text(json.dumps({"type": "submit_word"}))  # Missing "word" field

        # Receive error response
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "error"
        assert "Invalid message format" in message["message"]


def test_websocket_invalid_word_length(client: TestClient) -> None:
    """Test that word validation catches length constraints."""
    token = create_test_user_and_login(client)

    # Create and setup game
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]

    join_response = client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={"player_name": "Alice"})
    player_id = join_response.json()["player_id"]

    client.post(f"/games/{game_id}/start", headers=auth_headers(token))

    # Connect via WebSocket
    with client.websocket_connect(f"/ws/{game_id}/{player_id}") as websocket:
        # Send word that's too long (> 20 characters)
        websocket.send_text(json.dumps({"type": "submit_word", "word": "A" * 21}))

        # Receive error response
        data = websocket.receive_text()
        message = json.loads(data)

        assert message["type"] == "error"
        assert "Invalid message format" in message["message"]
