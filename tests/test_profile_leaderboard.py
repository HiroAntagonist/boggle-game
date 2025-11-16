# ABOUTME: Tests for profile, stats, leaderboard, and public games features
# ABOUTME: Verifies gamer tags, user stats, leaderboard, and public game discovery

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import json
from datetime import datetime, timezone

from src.api_server import app
from src.database import Base, get_db
from src.models import User, Game as GameModel, GamePlayer


# TEST DATABASE SETUP
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def client():
    """Create a test client with a fresh in-memory database for each test."""
    # Force import of all models FIRST so SQLAlchemy knows about them
    _ = (User, GameModel, GamePlayer)

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
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def create_user(client, email, password="TestPass123!", display_name=None):
    """Helper to create and register a user."""
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "display_name": display_name,
        },
    )
    assert response.status_code == 201
    data = response.json()
    return {
        "user_id": data["user_id"],
        "email": data["email"],
        "token": data["access_token"],
    }


def create_finished_game_with_winner(client, winner_token, loser_token, winner_score=100, loser_score=50):
    """Helper to create a finished game with a winner."""
    # Create game as winner
    response = client.post(
        "/games",
        json={"board_size": 4, "time_limit_seconds": 180, "max_players": 2},
        headers={"Authorization": f"Bearer {winner_token}"},
    )
    assert response.status_code == 201
    game_data = response.json()
    game_id = game_data["game_id"]

    # Creator joins their own game
    response = client.post(
        f"/games/{game_id}/players",
        json={"player_name": "Winner"},
        headers={"Authorization": f"Bearer {winner_token}"},
    )
    assert response.status_code == 201

    # Join game as loser
    response = client.post(
        f"/games/{game_id}/players",
        json={"player_name": "Loser"},
        headers={"Authorization": f"Bearer {loser_token}"},
    )
    assert response.status_code == 201

    # Simulate game completion by directly updating database
    # Use the overridden test database dependency
    from src.api_server import app
    db_gen = app.dependency_overrides[get_db]
    db = next(db_gen())
    try:
        game = db.query(GameModel).filter(GameModel.id == game_id).first()
        game.status = "finished"
        game.ended_at = datetime.now(timezone.utc)

        # Get players and set scores
        players = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()
        # First player joined is winner (creator)
        winner_player = players[0]
        loser_player = players[1]

        winner_player.score = winner_score
        loser_player.score = loser_score

        # Set winner_id
        game.winner_id = winner_player.user_id

        db.commit()
    finally:
        pass  # Don't close - generator manages this

    return game_id


# ============================================================================
# PROFILE TESTS (PATCH /auth/profile)
# ============================================================================


def test_update_display_name(client):
    """Test updating display name via PATCH /auth/profile."""
    user = create_user(client, "test@example.com", display_name="OldName")

    response = client.patch(
        "/auth/profile",
        json={"display_name": "NewName"},
        headers={"Authorization": f"Bearer {user['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "NewName"
    assert data["email"] == "test@example.com"


def test_update_gamer_tag_valid(client):
    """Test setting a valid gamer tag."""
    user = create_user(client, "test@example.com")

    response = client.patch(
        "/auth/profile",
        json={"gamer_tag": "ProGamer123"},
        headers={"Authorization": f"Bearer {user['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["gamer_tag"] == "ProGamer123"


def test_update_gamer_tag_duplicate(client):
    """Test that duplicate gamer tags are rejected."""
    user1 = create_user(client, "user1@example.com")
    user2 = create_user(client, "user2@example.com")

    # User 1 sets gamer tag
    response = client.patch(
        "/auth/profile",
        json={"gamer_tag": "UniqueTag"},
        headers={"Authorization": f"Bearer {user1['token']}"},
    )
    assert response.status_code == 200

    # User 2 tries to use same gamer tag - should fail
    response = client.patch(
        "/auth/profile",
        json={"gamer_tag": "UniqueTag"},
        headers={"Authorization": f"Bearer {user2['token']}"},
    )
    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]


def test_update_gamer_tag_invalid_format(client):
    """Test that invalid gamer tag formats are rejected."""
    user = create_user(client, "test@example.com")

    # Too short (< 3 chars)
    response = client.patch(
        "/auth/profile",
        json={"gamer_tag": "ab"},
        headers={"Authorization": f"Bearer {user['token']}"},
    )
    assert response.status_code == 422  # Pydantic validation error

    # Contains invalid characters
    response = client.patch(
        "/auth/profile",
        json={"gamer_tag": "invalid-tag!"},
        headers={"Authorization": f"Bearer {user['token']}"},
    )
    assert response.status_code == 422


def test_update_both_display_name_and_gamer_tag(client):
    """Test updating both display_name and gamer_tag in one request."""
    user = create_user(client, "test@example.com")

    response = client.patch(
        "/auth/profile",
        json={"display_name": "NewName", "gamer_tag": "NewTag"},
        headers={"Authorization": f"Bearer {user['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "NewName"
    assert data["gamer_tag"] == "NewTag"


def test_update_profile_requires_auth(client):
    """Test that PATCH /auth/profile requires authentication."""
    response = client.patch("/auth/profile", json={"display_name": "Test"})
    assert response.status_code == 403


# ============================================================================
# USER STATS TESTS (GET /users/me/stats)
# ============================================================================


def test_get_stats_no_games(client):
    """Test stats for a user with no games played."""
    user = create_user(client, "test@example.com")

    response = client.get(
        "/users/me/stats",
        headers={"Authorization": f"Bearer {user['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_games"] == 0
    assert data["total_wins"] == 0
    assert data["win_rate"] == 0.0
    assert data["total_points"] == 0
    assert data["average_score"] == 0.0
    assert data["best_score"] == 0


def test_get_stats_with_games(client):
    """Test stats calculation for a user with played games."""
    user1 = create_user(client, "user1@example.com")
    user2 = create_user(client, "user2@example.com")

    # Create 3 finished games: user1 wins 2, loses 1
    create_finished_game_with_winner(client, user1["token"], user2["token"], 100, 50)
    create_finished_game_with_winner(client, user1["token"], user2["token"], 80, 60)
    create_finished_game_with_winner(client, user2["token"], user1["token"], 90, 70)  # user1 loses

    response = client.get(
        "/users/me/stats",
        headers={"Authorization": f"Bearer {user1['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_games"] == 3
    assert data["total_wins"] == 2
    assert data["win_rate"] == pytest.approx(2/3, rel=0.01)
    assert data["total_points"] == 100 + 80 + 70  # All scores
    assert data["average_score"] == pytest.approx(250/3, rel=0.01)
    assert data["best_score"] == 100


def test_get_stats_requires_auth(client):
    """Test that GET /users/me/stats requires authentication."""
    response = client.get("/users/me/stats")
    assert response.status_code == 403


# ============================================================================
# LEADERBOARD TESTS (GET /leaderboard)
# ============================================================================


def test_leaderboard_empty(client):
    """Test leaderboard when no users have wins."""
    response = client.get("/leaderboard")

    assert response.status_code == 200
    data = response.json()
    assert data["leaderboard"] == []
    assert data["user_rank"] is None


def test_leaderboard_ranks_by_wins(client):
    """Test that leaderboard ranks users by total wins."""
    user1 = create_user(client, "user1@example.com", display_name="Player1")
    user2 = create_user(client, "user2@example.com", display_name="Player2")
    user3 = create_user(client, "user3@example.com", display_name="Player3")

    # User1: 3 wins
    create_finished_game_with_winner(client, user1["token"], user2["token"])
    create_finished_game_with_winner(client, user1["token"], user3["token"])
    create_finished_game_with_winner(client, user1["token"], user2["token"])

    # User2: 1 win
    create_finished_game_with_winner(client, user2["token"], user3["token"])

    # User3: 0 wins (should not appear on leaderboard)

    response = client.get("/leaderboard")

    assert response.status_code == 200
    data = response.json()
    leaderboard = data["leaderboard"]

    assert len(leaderboard) == 2  # Only users with wins
    assert leaderboard[0]["rank"] == 1
    assert leaderboard[0]["gamer_tag"] == "Player1"  # Falls back to display_name
    assert leaderboard[0]["total_wins"] == 3

    assert leaderboard[1]["rank"] == 2
    assert leaderboard[1]["gamer_tag"] == "Player2"
    assert leaderboard[1]["total_wins"] == 1


def test_leaderboard_with_gamer_tags(client):
    """Test that leaderboard shows gamer tags when set."""
    user1 = create_user(client, "user1@example.com")
    user2 = create_user(client, "user2@example.com")

    # Set gamer tags
    client.patch(
        "/auth/profile",
        json={"gamer_tag": "ProGamer"},
        headers={"Authorization": f"Bearer {user1['token']}"},
    )

    # User1 wins a game
    create_finished_game_with_winner(client, user1["token"], user2["token"])

    response = client.get("/leaderboard")

    assert response.status_code == 200
    data = response.json()
    assert data["leaderboard"][0]["gamer_tag"] == "ProGamer"


def test_leaderboard_user_rank_authenticated(client):
    """Test that authenticated users see their own rank."""
    user1 = create_user(client, "user1@example.com")
    user2 = create_user(client, "user2@example.com")

    # User1 wins a game
    create_finished_game_with_winner(client, user1["token"], user2["token"])

    response = client.get(
        "/leaderboard",
        headers={"Authorization": f"Bearer {user1['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_rank"] is not None
    assert data["user_rank"]["rank"] == 1
    assert data["user_rank"]["total_wins"] == 1


def test_leaderboard_limit_parameter(client):
    """Test that limit parameter restricts results."""
    users = [create_user(client, f"user{i}@example.com") for i in range(5)]

    # Create 5 winners
    for i, user in enumerate(users):
        opponent = users[(i + 1) % 5]
        create_finished_game_with_winner(client, user["token"], opponent["token"])

    response = client.get("/leaderboard?limit=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data["leaderboard"]) == 3


# ============================================================================
# PUBLIC GAMES TESTS (POST /games with is_public, GET /games/public)
# ============================================================================


def test_create_public_game_with_gamer_tag(client):
    """Test creating a public game when user has gamer tag."""
    user = create_user(client, "test@example.com")

    # Set gamer tag
    client.patch(
        "/auth/profile",
        json={"gamer_tag": "PublicGamer"},
        headers={"Authorization": f"Bearer {user['token']}"},
    )

    # Create public game
    response = client.post(
        "/games",
        json={"board_size": 4, "is_public": True},
        headers={"Authorization": f"Bearer {user['token']}"},
    )

    assert response.status_code == 201


def test_create_public_game_without_gamer_tag_fails(client):
    """Test that creating public game without gamer tag returns 400."""
    user = create_user(client, "test@example.com")

    response = client.post(
        "/games",
        json={"board_size": 4, "is_public": True},
        headers={"Authorization": f"Bearer {user['token']}"},
    )

    assert response.status_code == 400
    assert "gamer tag" in response.json()["detail"]


def test_create_private_game_without_gamer_tag(client):
    """Test creating private game works without gamer tag."""
    user = create_user(client, "test@example.com")

    response = client.post(
        "/games",
        json={"board_size": 4, "is_public": False},
        headers={"Authorization": f"Bearer {user['token']}"},
    )

    assert response.status_code == 201


def test_get_public_games_empty(client):
    """Test GET /games/public when no public games exist."""
    response = client.get("/games/public")

    assert response.status_code == 200
    data = response.json()
    assert data["games"] == []


def test_get_public_games_filters_correctly(client):
    """Test that GET /games/public only returns public waiting/created games."""
    user = create_user(client, "test@example.com")

    # Set gamer tag
    client.patch(
        "/auth/profile",
        json={"gamer_tag": "GameHost"},
        headers={"Authorization": f"Bearer {user['token']}"},
    )

    # Create public game
    response = client.post(
        "/games",
        json={"board_size": 4, "is_public": True},
        headers={"Authorization": f"Bearer {user['token']}"},
    )
    public_game_id = response.json()["game_id"]

    # Create private game (should not appear)
    client.post(
        "/games",
        json={"board_size": 4, "is_public": False},
        headers={"Authorization": f"Bearer {user['token']}"},
    )

    response = client.get("/games/public")

    assert response.status_code == 200
    data = response.json()
    assert len(data["games"]) == 1
    assert data["games"][0]["game_id"] == public_game_id
    assert data["games"][0]["creator_gamer_tag"] == "GameHost"


def test_get_public_games_shows_player_count(client):
    """Test that GET /games/public shows correct current_players count."""
    user1 = create_user(client, "user1@example.com")
    user2 = create_user(client, "user2@example.com")
    user3 = create_user(client, "user3@example.com")

    # Set gamer tag for user1
    client.patch(
        "/auth/profile",
        json={"gamer_tag": "Host"},
        headers={"Authorization": f"Bearer {user1['token']}"},
    )

    # Set gamer tag for user2 (required to join public games)
    client.patch(
        "/auth/profile",
        json={"gamer_tag": "Player2Tag"},
        headers={"Authorization": f"Bearer {user2['token']}"},
    )

    # Create public game
    response = client.post(
        "/games",
        json={"board_size": 4, "is_public": True, "max_players": 4},
        headers={"Authorization": f"Bearer {user1['token']}"},
    )
    game_id = response.json()["game_id"]

    # Creator joins their own game
    client.post(
        f"/games/{game_id}/players",
        json={"player_name": "Creator"},
        headers={"Authorization": f"Bearer {user1['token']}"},
    )

    # Another player joins
    client.post(
        f"/games/{game_id}/players",
        json={"player_name": "Player2"},
        headers={"Authorization": f"Bearer {user2['token']}"},
    )

    response = client.get("/games/public")

    assert response.status_code == 200
    data = response.json()
    assert len(data["games"]) == 1
    assert data["games"][0]["current_players"] == 2
    assert data["games"][0]["max_players"] == 4


def test_get_public_games_limit(client):
    """Test that GET /games/public respects limit parameter."""
    user = create_user(client, "test@example.com")

    # Set gamer tag
    client.patch(
        "/auth/profile",
        json={"gamer_tag": "Host"},
        headers={"Authorization": f"Bearer {user['token']}"},
    )

    # Create 3 public games
    for _ in range(3):
        client.post(
            "/games",
            json={"board_size": 4, "is_public": True},
            headers={"Authorization": f"Bearer {user['token']}"},
        )

    response = client.get("/games/public?limit=2")

    assert response.status_code == 200
    data = response.json()
    assert len(data["games"]) == 2
