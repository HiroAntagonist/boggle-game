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
