# ABOUTME: Tests for WebSocket functionality in hybrid API
# ABOUTME: Verifies real-time game updates work correctly

import pytest
import json
from fastapi.testclient import TestClient
from src.api_server import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the API."""
    return TestClient(app)


def test_websocket_requires_valid_game(client: TestClient) -> None:
    """Test that WebSocket connection requires valid game ID."""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/invalid-game/player-123"):
            pass  # Should fail to connect


def test_websocket_connection_success(client: TestClient) -> None:
    """Test successful WebSocket connection after game creation."""
    # Create game via REST
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]

    # Join game via REST
    join_response = client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})
    player_id = join_response.json()["player_id"]

    # Start game via REST
    client.post(f"/games/{game_id}/start")

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
    # Create and setup game
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]

    join_response = client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})
    player_id = join_response.json()["player_id"]

    client.post(f"/games/{game_id}/start")

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
    # Create game with 2 players
    create_response = client.post("/games")
    game_id = create_response.json()["game_id"]

    alice_response = client.post(f"/games/{game_id}/players", json={"player_name": "Alice"})
    alice_id = alice_response.json()["player_id"]

    bob_response = client.post(f"/games/{game_id}/players", json={"player_name": "Bob"})
    bob_id = bob_response.json()["player_id"]

    client.post(f"/games/{game_id}/start")

    # Connect both players via WebSocket
    with client.websocket_connect(f"/ws/{game_id}/{alice_id}") as alice_ws:
        with client.websocket_connect(f"/ws/{game_id}/{bob_id}") as bob_ws:
            # Alice sees Bob connected
            data = alice_ws.receive_text()
            message = json.loads(data)
            assert message["type"] == "player_connected"
            assert message["player_name"] == "Bob"

            # Alice submits a word
            alice_ws.send_text(json.dumps({"type": "submit_word", "word": "TEST"}))

            # Alice gets her result
            alice_result = json.loads(alice_ws.receive_text())
            assert alice_result["type"] == "word_result"

            # If word was valid, Bob should see broadcast
            if alice_result["valid"]:
                bob_broadcast = json.loads(bob_ws.receive_text())
                assert bob_broadcast["type"] == "word_submitted"
                assert bob_broadcast["player_name"] == "Alice"
