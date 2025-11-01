# ABOUTME: FastAPI REST API server for Boggle game
# ABOUTME: Manages game state and provides HTTP endpoints for game operations

from fastapi import FastAPI, HTTPException, status, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime, timezone, timedelta
import asyncio
import json

from src.api_models import (
    CreateGameRequest,
    CreateGameResponse,
    JoinGameRequest,
    JoinGameResponse,
    GameStateResponse,
    StartGameResponse,
    GameResultsResponse,
    PlayerResult,
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)
from src.board import Board
from src.dictionary import Dictionary
from src.scorer import Scorer
from src.game import Game
from src.player import Player
from src.config import GameConfig
from src.database import get_db
from src.models import User
from src.auth import hash_password, verify_password, create_access_token


app = FastAPI(
    title="Boggle Game API",
    description="REST API for multiplayer Boggle game",
    version="1.0.0"
)

# Connection manager for WebSockets
class ConnectionManager:
    """Manages WebSocket connections for real-time gameplay."""

    def __init__(self) -> None:
        # game_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str) -> None:
        """Accept and track a WebSocket connection."""
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = set()
        self.active_connections[game_id].add(websocket)

    def disconnect(self, websocket: WebSocket, game_id: str) -> None:
        """Remove a WebSocket connection."""
        if game_id in self.active_connections:
            self.active_connections[game_id].discard(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def broadcast(self, message: str, game_id: str, exclude: WebSocket | None = None) -> None:
        """Broadcast a message to all connections in a game."""
        if game_id not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[game_id]:
            if connection == exclude:
                continue
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, game_id)


# In-memory storage for games
# In a real application, this would be a database
games: Dict[str, Dict] = {}

# Shared game resources
dictionary = Dictionary("data/sowpods.txt")
scorer = Scorer(min_word_length=3)

# WebSocket connection manager
manager = ConnectionManager()


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


@app.post("/games/{game_id}/players", response_model=JoinGameResponse, status_code=status.HTTP_201_CREATED)
def join_game(game_id: str, request: JoinGameRequest) -> JoinGameResponse:
    """Join an existing game.

    Args:
        game_id: Unique game identifier
        request: Player information

    Returns:
        Player details and list of all players

    Raises:
        HTTPException: 404 if game not found, 400 if game is full
    """
    # Check if game exists
    if game_id not in games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found"
        )

    game_state = games[game_id]

    # Check if game is full
    if len(game_state["players"]) >= game_state["config"].max_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is full"
        )

    # Generate player ID
    player_id = str(uuid.uuid4())[:8]

    # Create player
    player = Player(player_id=player_id, name=request.player_name)

    # Add player to game
    game_state["players"][player_id] = player

    # Get list of all player names
    player_names = [p.name for p in game_state["players"].values()]

    return JoinGameResponse(
        player_id=player_id,
        player_name=request.player_name,
        players=player_names
    )


@app.get("/games/{game_id}", response_model=GameStateResponse)
def get_game_state(game_id: str) -> GameStateResponse:
    """Get current state of a game.

    Args:
        game_id: Unique game identifier

    Returns:
        Current game state including board, players, and status

    Raises:
        HTTPException: 404 if game not found
    """
    # Check if game exists
    if game_id not in games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found"
        )

    game_state = games[game_id]

    # Convert board to list of lists
    board = game_state["game"].board
    board_data = [[cell for cell in row] for row in board.grid]

    # Get player names
    player_names = [p.name for p in game_state["players"].values()]

    # Get time remaining (None if game not started)
    time_remaining = None
    if game_state["status"] == "in_progress":
        remaining = game_state["game"].get_remaining_time()
        time_remaining = int(remaining) if remaining is not None else None

    # Get words by player
    words_by_player = {}
    for player_id, player in game_state["players"].items():
        words_by_player[player_id] = player.get_words()

    return GameStateResponse(
        game_id=game_id,
        board=board_data,
        status=game_state["status"],
        players=player_names,
        time_remaining=time_remaining,
        words_by_player=words_by_player
    )


@app.post("/games/{game_id}/start", response_model=StartGameResponse)
def start_game(game_id: str) -> StartGameResponse:
    """Start a game.

    Args:
        game_id: Unique game identifier

    Returns:
        Game start confirmation with timestamp

    Raises:
        HTTPException: 404 if game not found, 400 if already started
    """
    # Check if game exists
    if game_id not in games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found"
        )

    game_state = games[game_id]

    # Check if game is already started
    if game_state["status"] == "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game already started"
        )

    # Start the game
    game_state["status"] = "in_progress"
    game_state["game"].start_timer()
    start_time = datetime.now(timezone.utc).isoformat()
    game_state["start_time"] = start_time

    return StartGameResponse(
        game_id=game_id,
        status="in_progress",
        start_time=start_time
    )


@app.get("/games/{game_id}/results", response_model=GameResultsResponse)
def get_game_results(game_id: str) -> GameResultsResponse:
    """Get final game results with scores and strike-outs.

    Args:
        game_id: Unique game identifier

    Returns:
        Results for all players including valid words and duplicates

    Raises:
        HTTPException: 404 if game not found
    """
    # Check if game exists
    if game_id not in games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found"
        )

    game_state = games[game_id]
    game = game_state["game"]

    # Get duplicate words (struck out)
    duplicates = list(game.get_duplicate_words())

    # Build results for each player
    player_results = []
    for player_id, player in game_state["players"].items():
        all_words = player.get_words()
        valid_words = game.get_player_valid_words(player)
        score = game.get_player_score(player)

        player_results.append(PlayerResult(
            name=player.name,
            score=score,
            words=all_words,
            valid_words=valid_words
        ))

    # Sort by score descending
    player_results.sort(key=lambda p: p.score, reverse=True)

    return GameResultsResponse(
        players=player_results,
        duplicates=duplicates
    )


@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str) -> None:
    """WebSocket endpoint for real-time game updates.

    Args:
        websocket: WebSocket connection
        game_id: Game identifier
        player_id: Player identifier

    Handles:
        - Real-time word submissions
        - Game state broadcasts
        - Timer updates
        - Player disconnections
    """
    # Verify game exists
    if game_id not in games:
        await websocket.close(code=1008, reason="Game not found")
        return

    game_state = games[game_id]

    # Verify player is in game
    if player_id not in game_state["players"]:
        await websocket.close(code=1008, reason="Player not in game")
        return

    # Accept connection
    await manager.connect(websocket, game_id)

    # Notify others that player connected
    player = game_state["players"][player_id]
    await manager.broadcast(
        json.dumps({"type": "player_connected", "player_name": player.name}),
        game_id,
        exclude=websocket
    )

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            message_type = message.get("type")

            if message_type == "submit_word":
                # Handle word submission
                word = message.get("word", "").upper()
                game = game_state["game"]

                # Validate and submit word
                is_valid = game.submit_word(word, player)

                # Calculate score
                score = 0
                status_msg = ""
                if is_valid:
                    score = scorer.score_word(word)
                    status_msg = f"Valid! +{score} points"
                else:
                    # Determine why invalid
                    if len(word) < game.config.min_word_length:
                        status_msg = f"Too short (min {game.config.min_word_length})"
                    elif not dictionary.is_valid_word(word):
                        status_msg = "Not in dictionary"
                    elif not game.board.has_word_path(word):
                        status_msg = "Not on board"
                    else:
                        status_msg = "Already submitted"

                # Send response to submitter
                await websocket.send_text(json.dumps({
                    "type": "word_result",
                    "word": word,
                    "valid": is_valid,
                    "score": score,
                    "message": status_msg
                }))

                # Broadcast to others if valid
                if is_valid:
                    await manager.broadcast(
                        json.dumps({
                            "type": "word_submitted",
                            "player_name": player.name,
                            "word": word,
                            "score": score
                        }),
                        game_id,
                        exclude=websocket
                    )

            elif message_type == "get_state":
                # Send current game state
                time_remaining = None
                if game_state["status"] == "in_progress":
                    remaining = game_state["game"].get_remaining_time()
                    time_remaining = int(remaining) if remaining is not None else None

                await websocket.send_text(json.dumps({
                    "type": "game_state",
                    "status": game_state["status"],
                    "time_remaining": time_remaining,
                    "player_count": len(game_state["players"])
                }))

    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
        # Notify others that player disconnected
        await manager.broadcast(
            json.dumps({"type": "player_disconnected", "player_name": player.name}),
            game_id
        )


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================


@app.post("/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    """Register a new user account.

    Creates a new user with hashed password. Username and email must be unique.
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(request.password)

    # Create new user
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=hashed_password
    )

    # Save to database
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    return RegisterResponse(
        user_id=new_user.id,
        username=new_user.username,
        message="User registered successfully"
    )


@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Login and get JWT access token.

    Validates credentials and returns a JWT token that expires in 30 days.
    """
    # Find user by username
    user = db.query(User).filter(User.username == request.username).first()

    # Verify user exists and password is correct
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Create JWT token with user info
    token_data = {
        "user_id": user.id,
        "username": user.username
    }
    access_token = create_access_token(token_data, expires_delta=timedelta(days=30))

    return LoginResponse(
        access_token=access_token,
        token_type="bearer"
    )
