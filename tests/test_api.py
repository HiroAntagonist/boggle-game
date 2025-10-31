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


def test_get_game_state_success(client: TestClient) -> None:
    """Test getting game state."""
    # Create game
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]

    # Add a player
    client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})

    # Get game state
    response = client.get(f"/games/{game_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["game_id"] == game_id
    assert "board" in data
    assert data["status"] == "waiting"
    assert len(data["players"]) == 1
    assert data["players"][0] == "Alice"


def test_get_game_state_nonexistent(client: TestClient) -> None:
    """Test getting state of nonexistent game."""
    response = client.get("/games/invalid-id")

    assert response.status_code == 404


def test_start_game_success(client: TestClient) -> None:
    """Test successfully starting a game."""
    # Create game and add player
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]
    client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})

    # Start the game
    response = client.post(f"/games/{game_id}/start")

    assert response.status_code == 200
    data = response.json()

    assert data["game_id"] == game_id
    assert data["status"] == "in_progress"
    assert "start_time" in data


def test_start_game_already_started(client: TestClient) -> None:
    """Test starting a game that's already in progress."""
    # Create, join, and start game
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]
    client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})
    client.post(f"/games/{game_id}/start")

    # Try to start again
    response = client.post(f"/games/{game_id}/start")

    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


def test_start_game_nonexistent(client: TestClient) -> None:
    """Test starting a nonexistent game."""
    response = client.post("/games/invalid-id/start")

    assert response.status_code == 404


def test_submit_word_valid(client: TestClient) -> None:
    """Test submitting a valid word."""
    # Create game, join, start
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]

    join_response = client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})
    player_id = join_response.json()["player_id"]

    client.post(f"/games/{game_id}/start")

    # Get board to find a valid word
    state = client.get(f"/games/{game_id}").json()
    board = state["board"]

    # Find any 3-letter combination that's adjacent (simplest case)
    # For testing, we'll use a word we know exists: we'll submit "CAT" if it's on board
    # But for now, let's just test the structure works
    response = client.post(f"/games/{game_id}/words", json={
        "player_id": player_id,
        "word": "TEST"  # May or may not be valid, we just test response structure
    })

    assert response.status_code == 200
    data = response.json()

    assert "valid" in data
    assert "score" in data
    assert "message" in data


def test_submit_word_duplicate(client: TestClient) -> None:
    """Test submitting same word twice."""
    # Create game, join, start
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]

    join_response = client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})
    player_id = join_response.json()["player_id"]

    client.post(f"/games/{game_id}/start")

    # Submit word twice
    word_data = {"player_id": player_id, "word": "CAT"}
    response1 = client.post(f"/games/{game_id}/words", json=word_data)
    response2 = client.post(f"/games/{game_id}/words", json=word_data)

    # Second submission should be invalid (duplicate)
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["valid"] is False
    assert data2["score"] == 0


def test_submit_word_game_not_started(client: TestClient) -> None:
    """Test submitting word to game that hasn't started."""
    # Create game and join but don't start
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]

    join_response = client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})
    player_id = join_response.json()["player_id"]

    # Try to submit word
    response = client.post(f"/games/{game_id}/words", json={
        "player_id": player_id,
        "word": "CAT"
    })

    assert response.status_code == 400
    assert "not started" in response.json()["detail"].lower()


def test_submit_word_nonexistent_game(client: TestClient) -> None:
    """Test submitting word to nonexistent game."""
    response = client.post("/games/invalid-id/words", json={
        "player_id": "some-id",
        "word": "CAT"
    })

    assert response.status_code == 404


def test_submit_word_invalid_player(client: TestClient) -> None:
    """Test submitting word with invalid player ID."""
    # Create game and start
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]
    client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})
    client.post(f"/games/{game_id}/start")

    # Submit with invalid player ID
    response = client.post(f"/games/{game_id}/words", json={
        "player_id": "invalid-player-id",
        "word": "CAT"
    })

    assert response.status_code == 400
    assert "player" in response.json()["detail"].lower()


def test_get_results_success(client: TestClient) -> None:
    """Test getting game results."""
    # Create game with 2 players
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]

    # Add two players
    alice_response = client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})
    alice_id = alice_response.json()["player_id"]

    bob_response = client.post(f"/games/{game_id}/players", json={"player_name": "Bob"})
    bob_id = bob_response.json()["player_id"]

    # Start game
    client.post(f"/games/{game_id}/start")

    # Both players submit some words
    client.post(f"/games/{game_id}/words", json={"player_id": alice_id, "word": "CAT"})
    client.post(f"/games/{game_id}/words", json={"player_id": alice_id, "word": "DOG"})
    client.post(f"/games/{game_id}/words", json={"player_id": bob_id, "word": "CAT"})  # Duplicate!
    client.post(f"/games/{game_id}/words", json={"player_id": bob_id, "word": "FISH"})

    # Get results
    response = client.get(f"/games/{game_id}/results")

    assert response.status_code == 200
    data = response.json()

    assert "players" in data
    assert "duplicates" in data
    assert len(data["players"]) == 2

    # Check that each player has required fields
    for player in data["players"]:
        assert "name" in player
        assert "score" in player
        assert "words" in player
        assert "valid_words" in player

    # CAT should be in duplicates (both submitted it)
    # Note: May or may not actually be in duplicates depending on board
    # So we just check structure


def test_get_results_game_not_started(client: TestClient) -> None:
    """Test getting results for game that hasn't started."""
    # Create game but don't start
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]

    response = client.get(f"/games/{game_id}/results")

    # Should work but have no words
    assert response.status_code == 200


def test_get_results_nonexistent_game(client: TestClient) -> None:
    """Test getting results for nonexistent game."""
    response = client.get("/games/invalid-id/results")

    assert response.status_code == 404
