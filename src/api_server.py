# ABOUTME: FastAPI REST API server for Boggle game
# ABOUTME: Manages game state and provides HTTP endpoints for game operations

from fastapi import FastAPI, HTTPException, status
from typing import Dict
import uuid
from datetime import datetime, timezone

from src.api_models import (
    CreateGameRequest,
    CreateGameResponse,
    JoinGameRequest,
    JoinGameResponse,
    GameStateResponse,
    StartGameResponse,
    SubmitWordRequest,
    SubmitWordResponse,
    GameResultsResponse,
    PlayerResult,
)
from src.board import Board
from src.dictionary import Dictionary
from src.scorer import Scorer
from src.game import Game
from src.player import Player
from src.config import GameConfig


app = FastAPI(
    title="Boggle Game API",
    description="REST API for multiplayer Boggle game",
    version="1.0.0"
)

# In-memory storage for games
# In a real application, this would be a database
games: Dict[str, Dict] = {}

# Shared game resources
dictionary = Dictionary("data/sowpods.txt")
scorer = Scorer(min_word_length=3)


@app.post("/games", response_model=CreateGameResponse, status_code=status.HTTP_201_CREATED)
def create_game(request: CreateGameRequest = CreateGameRequest()) -> CreateGameResponse:
    """Create a new game session.

    Args:
        request: Game configuration

    Returns:
        Created game details including game_id and board
    """
    # Generate unique game ID
    game_id = str(uuid.uuid4())[:8]

    # Create game config
    config = GameConfig(
        board_size=request.board_size,
        time_limit_seconds=request.time_limit_seconds,
        max_players=request.max_players,
        min_word_length=3
    )

    # Create board
    board = Board(size=config.board_size)

    # Create game instance
    game = Game(
        board=board,
        dictionary=dictionary,
        scorer=scorer,
        config=config
    )

    # Store game state
    games[game_id] = {
        "game": game,
        "config": config,
        "players": {},  # player_id -> Player object
        "status": "waiting",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Convert board to list of lists
    board_data = [[cell for cell in row] for row in board.grid]

    return CreateGameResponse(
        game_id=game_id,
        board=board_data,
        created_at=games[game_id]["created_at"],
        status="waiting"
    )
