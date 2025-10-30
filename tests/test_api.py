# ABOUTME: Tests for FastAPI REST endpoints
# ABOUTME: Uses FastAPI TestClient for API testing

import pytest
from fastapi.testclient import TestClient
from src.api_server import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the API."""
    return TestClient(app)


def test_create_game_default_settings(client: TestClient) -> None:
    """Test creating a game with default settings."""
    response = client.post("/games")

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
    response = client.post("/games", json={
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
    response = client.post("/games", json={
        "board_size": 3  # Invalid: must be 4 or 5
    })

    assert response.status_code == 422  # Validation error


def test_join_game_success(client: TestClient) -> None:
    """Test successfully joining a game."""
    # First create a game
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]

    # Join the game
    response = client.post(f"/games/{game_id}/players", json={
        "player_name": "Alice"
    })

    assert response.status_code == 201
    data = response.json()

    assert "player_id" in data
    assert data["player_name"] == "Alice"
    assert data["players"] == ["Alice"]


def test_join_game_multiple_players(client: TestClient) -> None:
    """Test multiple players joining a game."""
    # Create game
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]

    # First player joins
    response1 = client.post(f"/games/{game_id}/players", json={
        "player_name": "Alice"
    })
    assert response1.status_code == 201

    # Second player joins
    response2 = client.post(f"/games/{game_id}/players", json={
        "player_name": "Bob"
    })
    assert response2.status_code == 201
    data2 = response2.json()

    # Both players should be in the list
    assert "Alice" in data2["players"]
    assert "Bob" in data2["players"]
    assert len(data2["players"]) == 2


def test_join_game_room_full(client: TestClient) -> None:
    """Test joining a full game."""
    # Create game with max 2 players
    create_response = client.post("/games", json={"max_players": 2})
    game_id = create_response.json()["game_id"]

    # Add 2 players
    client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})
    client.post(f"/games/{game_id}/players", json={"player_name": "Bob"})

    # Try to add third player
    response = client.post(f"/games/{game_id}/players", json={
        "player_name": "Charlie"
    })

    assert response.status_code == 400  # Bad request
    assert "full" in response.json()["detail"].lower()


def test_join_game_nonexistent(client: TestClient) -> None:
    """Test joining a game that doesn't exist."""
    response = client.post("/games/invalid-id/players", json={
        "player_name": "Alice"
    })

    assert response.status_code == 404  # Not found
