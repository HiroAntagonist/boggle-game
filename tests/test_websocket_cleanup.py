# ABOUTME: Tests for WebSocket cleanup functionality
# ABOUTME: Tests that waiting games are deleted when all players disconnect

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.api_server import app, manager
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
    # Clear WebSocket connections
    manager.active_connections.clear()


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


def get_db_session() -> Session:
    """Get a database session for testing."""
    from src.database import SessionLocal
    return SessionLocal()


def test_waiting_game_deleted_when_all_players_disconnect(client: TestClient) -> None:
    """Test that waiting games are deleted when all players disconnect."""
    # Create user and game
    token = create_test_user_and_login(client)
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]

    # Join the game
    join_response = client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={"player_name": "Alice"})
    player_id = join_response.json()["player_id"]

    # Verify game exists in waiting status
    db = next(app.dependency_overrides[get_db]())
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        assert game is not None
        assert game.status == "waiting"

        # Verify player exists
        player = db.query(GamePlayer).filter(GamePlayer.id == player_id).first()
        assert player is not None
    finally:
        db.close()

    # Connect and immediately disconnect via WebSocket
    with client.websocket_connect(f"/ws/{game_id}/{player_id}") as websocket:
        # Connection established
        pass
    # WebSocket disconnects when context exits

    # Verify game and player are deleted from database
    db = next(app.dependency_overrides[get_db]())
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        assert game is None, "Game should be deleted when all players disconnect from waiting game"

        player = db.query(GamePlayer).filter(GamePlayer.id == player_id).first()
        assert player is None, "Player should be deleted when waiting game is deleted"
    finally:
        db.close()


def test_in_progress_game_not_deleted_when_players_disconnect(client: TestClient) -> None:
    """Test that in-progress games are NOT deleted when players disconnect."""
    # Create user and game
    token = create_test_user_and_login(client)
    create_response = client.post("/games", headers=auth_headers(token))
    game_id = create_response.json()["game_id"]

    # Join and start the game
    join_response = client.post(f"/games/{game_id}/players", headers=auth_headers(token), json={"player_name": "Alice"})
    player_id = join_response.json()["player_id"]
    client.post(f"/games/{game_id}/start", headers=auth_headers(token))

    # Verify game is in_progress
    db = next(app.dependency_overrides[get_db]())
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        assert game is not None
        assert game.status == "in_progress"
    finally:
        db.close()

    # Connect and disconnect via WebSocket
    with client.websocket_connect(f"/ws/{game_id}/{player_id}") as websocket:
        pass

    # Verify game still exists (should NOT be deleted)
    db = next(app.dependency_overrides[get_db]())
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        assert game is not None, "In-progress games should not be deleted on disconnect"
        assert game.status == "in_progress"

        player = db.query(GamePlayer).filter(GamePlayer.id == player_id).first()
        assert player is not None, "Players should not be deleted for in-progress games"
    finally:
        db.close()


def test_waiting_game_not_deleted_when_some_players_remain(client: TestClient) -> None:
    """Test that waiting games are NOT deleted when some players remain connected."""
    # Create two users
    token1 = create_test_user_and_login(client, email="alice@example.com")
    token2 = create_test_user_and_login(client, email="bob@example.com")

    # Create game
    create_response = client.post("/games", headers=auth_headers(token1))
    game_id = create_response.json()["game_id"]

    # Both players join
    join_response1 = client.post(f"/games/{game_id}/players", headers=auth_headers(token1), json={"player_name": "Alice"})
    join_response2 = client.post(f"/games/{game_id}/players", headers=auth_headers(token2), json={"player_name": "Bob"})
    player_id1 = join_response1.json()["player_id"]
    player_id2 = join_response2.json()["player_id"]

    # Connect both players
    with client.websocket_connect(f"/ws/{game_id}/{player_id1}") as ws1:
        with client.websocket_connect(f"/ws/{game_id}/{player_id2}") as ws2:
            # Both connected
            pass
        # Player 2 disconnects, Player 1 still connected

        # Verify game still exists (should NOT be deleted while player 1 connected)
        db = next(app.dependency_overrides[get_db]())
        try:
            game = db.query(Game).filter(Game.id == game_id).first()
            assert game is not None, "Game should not be deleted while players remain connected"
            assert game.status == "waiting"
        finally:
            db.close()

    # Now both disconnected - game should be deleted
    db = next(app.dependency_overrides[get_db]())
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        assert game is None, "Game should be deleted when all players disconnect"
    finally:
        db.close()
