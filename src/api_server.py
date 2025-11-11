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
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

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
    GoogleAuthRequest,
    UserResponse,
    HealthCheckResponse,
    DatabaseHealth,
    WebSocketHealth,
    BackgroundTasksHealth,
    TimerMonitorHealth,
    GamesHealth,
)
from src.board import Board
from src.dictionary import Dictionary
from src.scorer import Scorer
from src.game import Game
from src.player import Player
from src.config import GameConfig
from src.database import get_db
from src.models import User
from src.auth import hash_password, verify_password, create_access_token, get_current_user_from_db
import random


def get_display_name(user: User) -> str:
    """Get the display name for a user.

    Returns display_name if set, otherwise falls back to email prefix.
    For example: john@gmail.com -> "john"

    Args:
        user: User object from database

    Returns:
        Display name string
    """
    if user.display_name:
        return user.display_name
    # Fallback to email prefix (before @)
    return user.email.split('@')[0]


def generate_friendly_code(db: Session) -> str:
    """Generate a unique friendly code in XXXX-XXXX format.

    Uses 8 random digits formatted as XXXX-XXXX for human readability.
    Checks database for uniqueness and retries if collision occurs.

    Args:
        db: Database session for uniqueness checks

    Returns:
        Unique 9-character code string (8 digits + 1 dash)
    """
    from src.models import Game as GameModel

    max_attempts = 10
    for _ in range(max_attempts):
        # Generate 8 random digits
        code_number = random.randint(0, 99999999)
        # Format as XXXX-XXXX
        friendly_code = f"{code_number:08d}"[:4] + "-" + f"{code_number:08d}"[4:]

        # Check if code already exists
        existing = db.query(GameModel).filter(GameModel.friendly_code == friendly_code).first()
        if not existing:
            return friendly_code

    # Fallback to UUID if we can't generate unique code (extremely unlikely)
    raise Exception("Unable to generate unique friendly code after multiple attempts")


app = FastAPI(
    title="Boggle Game API",
    description="REST API for multiplayer Boggle game",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event() -> None:
    """Start background tasks when the application starts."""
    # Check if there are any in-progress games and start monitor if needed
    from src.database import SessionLocal
    from src.models import Game as GameModel

    db = SessionLocal()
    try:
        active_count = db.query(GameModel).filter(
            GameModel.status == "in_progress",
            GameModel.started_at.isnot(None),
            GameModel.time_limit.isnot(None)
        ).count()

        if active_count > 0:
            global monitor_task
            monitor_task = asyncio.create_task(monitor_game_timers())
            print(f"API server started - resuming timer monitor for {active_count} active games")
        else:
            print("API server started - no active games")
    finally:
        db.close()


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

        # Create a copy of the set to avoid RuntimeError when set changes during iteration
        disconnected = set()
        for connection in list(self.active_connections[game_id]):
            if connection == exclude:
                continue
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, game_id)

    def get_connection_count(self, game_id: str) -> int:
        """Get the number of active connections for a game."""
        if game_id not in self.active_connections:
            return 0
        return len(self.active_connections[game_id])


# In-memory storage for games
# In a real application, this would be a database
games: Dict[str, Dict] = {}

# Shared game resources
dictionary = Dictionary("data/sowpods.txt")
scorer = Scorer(min_word_length=3)

# WebSocket connection manager
manager = ConnectionManager()

# Global reference to monitor task (None when not running)
monitor_task: asyncio.Task | None = None


def start_monitor_if_needed(db: Session) -> None:
    """Start the game timer monitor if there are active games and it's not already running."""
    global monitor_task

    # Check if monitor is already running
    if monitor_task is not None and not monitor_task.done():
        return

    # Check if there are any active games
    from src.models import Game as GameModel
    active_count = db.query(GameModel).filter(
        GameModel.status == "in_progress",
        GameModel.started_at.isnot(None),
        GameModel.time_limit.isnot(None)
    ).count()

    if active_count > 0:
        monitor_task = asyncio.create_task(monitor_game_timers())
        print(f"Started game timer monitor (active games: {active_count})")


# Background task for monitoring game timers
async def monitor_game_timers() -> None:
    """Background task that checks for expired games and ends them.

    This runs continuously while there are active games, checking every 5 seconds
    for games that have exceeded their time limit. When a game expires:
    1. Calculate final scores with duplicate removal
    2. Update game status to "finished"
    3. Broadcast results to all connected players

    Exits automatically when there are no more active games.
    """
    from src.database import SessionLocal
    from src.models import Game as GameModel, GamePlayer
    from src.ws_models import GameEndedMessage, PlayerFinalResult, PlayerWordResult

    print("Game timer monitor started")

    while True:
        db = None
        try:
            # Check every 5 seconds
            await asyncio.sleep(5)

            # Create a new database session for this check
            db = SessionLocal()

            # Find all games that are in progress with a time limit
            active_games = db.query(GameModel).filter(
                GameModel.status == "in_progress",
                GameModel.started_at.isnot(None),
                GameModel.time_limit.isnot(None)
            ).all()

            # Exit if no active games
            if not active_games:
                print("No active games remaining - stopping timer monitor")
                break

            now = datetime.now(timezone.utc)

            for game in active_games:
                # Skip if missing required data
                if game.started_at is None or game.time_limit is None:
                    continue

                # Ensure started_at is timezone-aware
                started_at = game.started_at
                if started_at.tzinfo is None:
                    started_at = started_at.replace(tzinfo=timezone.utc)

                # Calculate elapsed time
                elapsed = (now - started_at).total_seconds()

                # Check if time limit exceeded
                if elapsed >= game.time_limit:
                    # Game has ended! Calculate final results
                    await end_game(game.id, db)

        except Exception as e:
            print(f"Error in game timer monitor: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Always close session if it was created
            if db:
                db.close()

    print("Game timer monitor stopped")


async def end_game(game_id: str, db: Session) -> None:
    """End a game and broadcast final results to all players.

    Args:
        game_id: The game to end
        db: Database session
    """
    from src.models import Game as GameModel, GamePlayer
    from src.ws_models import GameEndedMessage, PlayerFinalResult, PlayerWordResult

    # Get game from database
    db_game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not db_game or db_game.status == "finished":
        return

    # Get all players in this game
    game_players = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()

    # Collect all words by player
    player_words: Dict[str, list[str]] = {}
    for gp in game_players:
        words = json.loads(gp.words_found) if gp.words_found else [] if gp.words_found else []
        player_words[get_display_name(gp.user)] = words

    # Find duplicate words (words submitted by multiple players)
    word_counts: Dict[str, int] = {}
    for words in player_words.values():
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

    duplicates = {word for word, count in word_counts.items() if count > 1}

    # Calculate final results for each player
    results = []
    for gp in game_players:
        words = json.loads(gp.words_found) if gp.words_found else [] if gp.words_found else []
        word_results = []
        total_score = 0

        for word in words:
            is_duplicate = word in duplicates
            score = 0 if is_duplicate else scorer.score_word(word)
            total_score += score

            word_results.append(PlayerWordResult(
                word=word,
                score=score,
                valid=not is_duplicate
            ))

        results.append(PlayerFinalResult(
            player_name=get_display_name(gp.user),
            words=word_results,
            total_score=total_score
        ))

        # Update player score in database
        gp.score = total_score

    # Find winner (highest score)
    winner = None
    if results:
        max_score = max(r.total_score for r in results)
        winners = [r for r in results if r.total_score == max_score]
        winner = winners[0].player_name if len(winners) == 1 else None  # None if tie

    # Update game status in database
    db_game.status = "finished"
    db_game.ended_at = datetime.now(timezone.utc)
    db.commit()

    # Broadcast results to all connected players
    end_message = GameEndedMessage(
        type="game_ended",
        winner=winner,
        results=results
    )

    await manager.broadcast(end_message.model_dump_json(), game_id)

    print(f"Game {game_id} ended. Winner: {winner}")


# Helper function for authorization
def verify_game_participant(game_id: str, user_id: str, db: Session) -> None:
    """Verify that a user is a participant in a game.

    Args:
        game_id: Game identifier
        user_id: User identifier
        db: Database session

    Raises:
        HTTPException: 403 if user is not a participant in the game
    """
    from src.models import GamePlayer

    participant = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == user_id
    ).first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this game"
        )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)) -> HealthCheckResponse:
    """Health check endpoint for monitoring server status.

    Returns comprehensive health metrics including:
    - Database connectivity and response time
    - WebSocket connection counts
    - Background task status
    - Game statistics

    No authentication required - this is a public monitoring endpoint.
    """
    import time
    from src.models import Game as GameModel

    overall_status = "healthy"

    # Check database health
    from sqlalchemy import text
    db_start = time.time()
    db_connected = False
    try:
        # Simple query to test connection
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception as e:
        print(f"Database health check failed: {e}")
        overall_status = "degraded"
    db_response_time = int((time.time() - db_start) * 1000)  # Convert to milliseconds

    # Count WebSocket connections
    total_ws_connections = sum(len(conns) for conns in manager.active_connections.values())
    ws_by_game = {game_id: len(conns) for game_id, conns in manager.active_connections.items()}

    # Check timer monitor status
    global monitor_task
    monitor_running = monitor_task is not None and not monitor_task.done()

    # Count active games being monitored
    active_timed_games = 0
    if db_connected:
        try:
            active_timed_games = db.query(GameModel).filter(
                GameModel.status == "in_progress",
                GameModel.started_at.isnot(None),
                GameModel.time_limit.isnot(None)
            ).count()
        except Exception as e:
            print(f"Failed to count active games: {e}")
            overall_status = "degraded"

    # Get game statistics
    game_stats = {"total": 0, "in_progress": 0, "waiting": 0, "finished": 0}
    if db_connected:
        try:
            game_stats["total"] = db.query(GameModel).count()
            game_stats["in_progress"] = db.query(GameModel).filter(
                GameModel.status == "in_progress"
            ).count()
            game_stats["waiting"] = db.query(GameModel).filter(
                GameModel.status == "waiting"
            ).count()
            game_stats["finished"] = db.query(GameModel).filter(
                GameModel.status == "finished"
            ).count()
        except Exception as e:
            print(f"Failed to get game statistics: {e}")
            overall_status = "degraded"

    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=DatabaseHealth(
            connected=db_connected,
            response_time_ms=db_response_time
        ),
        websockets=WebSocketHealth(
            total_connections=total_ws_connections,
            connections_by_game=ws_by_game
        ),
        background_tasks=BackgroundTasksHealth(
            timer_monitor=TimerMonitorHealth(
                running=monitor_running,
                active_games_count=active_timed_games
            )
        ),
        games=GamesHealth(
            total=game_stats["total"],
            in_progress=game_stats["in_progress"],
            waiting=game_stats["waiting"],
            finished=game_stats["finished"]
        )
    )


@app.post("/games", response_model=CreateGameResponse, status_code=status.HTTP_201_CREATED)
def create_game(
    request: CreateGameRequest = CreateGameRequest(),
    current_user: User = Depends(get_current_user_from_db),
    db: Session = Depends(get_db)
) -> CreateGameResponse:
    """Create a new game session.

    Requires authentication. The authenticated user becomes the game creator.

    Args:
        request: Game configuration
        current_user: Authenticated user (injected)
        db: Database session (injected)

    Returns:
        Created game details including game_id and board
    """
    # Create board
    board = Board(size=request.board_size)

    # Convert board to JSON for storage
    board_data = [[cell for cell in row] for row in board.grid]
    board_json = json.dumps(board_data)

    # Create game record in database
    from src.models import Game as GameModel
    from sqlalchemy.exc import IntegrityError

    # Retry loop to handle duplicate friendly codes
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            # Generate unique friendly code
            friendly_code = generate_friendly_code(db)

            db_game = GameModel(
                creator_id=current_user.id,
                status="waiting",
                board_size=request.board_size,
                time_limit=request.time_limit_seconds,
                max_players=request.max_players,
                min_word_length=3,
                board_state=board_json,
                friendly_code=friendly_code
            )

            db.add(db_game)
            db.commit()
            db.refresh(db_game)

            # Log successful game creation
            print(f"✅ GAME CREATED - UUID: {db_game.id} | Friendly Code: {db_game.friendly_code} | Creator: {get_display_name(current_user)}")

            break  # Success - exit retry loop

        except IntegrityError as e:
            # Duplicate friendly code - rollback and retry
            db.rollback()
            print(f"⚠️  DUPLICATE CODE DETECTED - Attempt {attempt + 1}/{max_attempts} | Code: {friendly_code} | Error: {str(e)}")
            if attempt == max_attempts - 1:
                # Last attempt failed - raise error
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Unable to generate unique game code after multiple attempts"
                )

    # Assertion: friendly_code is guaranteed to be set since we just assigned it
    assert db_game.friendly_code is not None

    return CreateGameResponse(
        game_id=db_game.id,
        friendly_code=db_game.friendly_code,
        board=board_data,
        created_at=db_game.created_at.isoformat(),
        status=db_game.status
    )


@app.post("/games/{game_id}/players", response_model=JoinGameResponse, status_code=status.HTTP_201_CREATED)
async def join_game(
    game_id: str,
    request: JoinGameRequest,
    current_user: User = Depends(get_current_user_from_db),
    db: Session = Depends(get_db)
) -> JoinGameResponse:
    """Join an existing game.

    Requires authentication. The authenticated user joins the game.

    Args:
        game_id: Unique game identifier
        request: Player information
        current_user: Authenticated user (injected)
        db: Database session (injected)

    Returns:
        Player details and list of all players

    Raises:
        HTTPException: 404 if game not found, 400 if game is full
    """
    from src.models import Game as GameModel, GamePlayer

    # Check if game exists
    db_game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not db_game:
        print(f"❌ JOIN FAILED - Game not found | UUID: {game_id} | User: {get_display_name(current_user)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found"
        )

    # Check if game is full
    current_player_count = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).count()
    print(f"🔍 JOIN REQUEST - UUID: {db_game.id} | Friendly Code: {db_game.friendly_code} | User: {get_display_name(current_user)} | Current Players: {current_player_count}/{db_game.max_players}")
    if current_player_count >= db_game.max_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is full"
        )

    # Check if user already joined this game
    existing_player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == current_user.id
    ).first()
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already joined this game"
        )

    # Create GamePlayer record
    game_player = GamePlayer(
        game_id=game_id,
        user_id=current_user.id,
        score=0,
        words_found="[]"
    )

    db.add(game_player)
    db.commit()
    db.refresh(game_player)

    # Get all players in the game
    all_players = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()
    player_names = []
    for gp in all_players:
        user = db.query(User).filter(User.id == gp.user_id).first()
        if user:
            player_names.append(get_display_name(user))

    print(f"✅ PLAYER JOINED - UUID: {game_id} | Friendly Code: {db_game.friendly_code} | Player: {get_display_name(current_user)} | Player ID: {game_player.id} | Total Players: {len(player_names)}/{db_game.max_players}")

    # Broadcast player_joined to all connected players
    await manager.broadcast(
        json.dumps({
            "type": "player_joined",
            "player_name": get_display_name(current_user),
            "player_count": len(player_names),
            "max_players": db_game.max_players,
            "players": player_names
        }),
        game_id
    )

    # Auto-start game if room is now full
    if len(player_names) >= db_game.max_players and db_game.status == "waiting":
        print(f"🚀 AUTO-STARTING GAME - Room is full ({len(player_names)}/{db_game.max_players})")
        db_game.status = "in_progress"
        db_game.started_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_game)

        # Start timer monitor if this is a timed game
        if db_game.time_limit is not None:
            start_monitor_if_needed(db)

        # Broadcast game_started to all connected players
        assert db_game.board_state is not None, "Board state must exist for started game"
        board_data = json.loads(db_game.board_state)
        await manager.broadcast(
            json.dumps({
                "type": "game_started",
                "board": board_data,
                "started_at": db_game.started_at.isoformat(),
                "time_limit": db_game.time_limit
            }),
            game_id
        )

    return JoinGameResponse(
        game_id=game_id,
        player_id=game_player.id,
        player_name=request.player_name,
        players=player_names
    )


@app.post("/games/code/{friendly_code}/join", response_model=JoinGameResponse, status_code=status.HTTP_201_CREATED)
async def join_game_by_code(
    friendly_code: str,
    request: JoinGameRequest,
    current_user: User = Depends(get_current_user_from_db),
    db: Session = Depends(get_db)
) -> JoinGameResponse:
    """Join a game using its friendly code (XXXX-XXXX format).

    This is a convenience endpoint that allows users to join games using
    human-readable codes instead of UUIDs.

    Requires authentication. The authenticated user joins the game.

    Args:
        friendly_code: Human-readable game code (XXXX-XXXX format)
        request: Player information
        current_user: Authenticated user (injected)
        db: Database session (injected)

    Returns:
        Player details and list of all players

    Raises:
        HTTPException: 404 if game not found, 400 if game is full or user already joined
    """
    from src.models import Game as GameModel, GamePlayer

    # Look up game by friendly code
    print(f"🔍 JOIN BY CODE REQUEST - Friendly Code: {friendly_code} | User: {get_display_name(current_user)}")
    db_game = db.query(GameModel).filter(GameModel.friendly_code == friendly_code).first()
    if not db_game:
        print(f"❌ JOIN BY CODE FAILED - Game not found | Friendly Code: {friendly_code} | User: {get_display_name(current_user)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with code {friendly_code} not found"
        )

    print(f"✅ GAME FOUND BY CODE - UUID: {db_game.id} | Friendly Code: {friendly_code}")

    # Check if game is full
    current_player_count = db.query(GamePlayer).filter(GamePlayer.game_id == db_game.id).count()
    if current_player_count >= db_game.max_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is full"
        )

    # Check if user already joined this game
    existing_player = db.query(GamePlayer).filter(
        GamePlayer.game_id == db_game.id,
        GamePlayer.user_id == current_user.id
    ).first()
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already joined this game"
        )

    # Create GamePlayer record
    game_player = GamePlayer(
        game_id=db_game.id,
        user_id=current_user.id,
        score=0,
        words_found="[]"
    )

    db.add(game_player)
    db.commit()
    db.refresh(game_player)

    # Get all players in the game
    all_players = db.query(GamePlayer).filter(GamePlayer.game_id == db_game.id).all()
    player_names = []
    for gp in all_players:
        user = db.query(User).filter(User.id == gp.user_id).first()
        if user:
            player_names.append(get_display_name(user))

    print(f"✅ PLAYER JOINED BY CODE - UUID: {db_game.id} | Friendly Code: {friendly_code} | Player: {get_display_name(current_user)} | Player ID: {game_player.id} | Total Players: {len(player_names)}/{db_game.max_players}")

    # Broadcast player_joined to all connected players
    await manager.broadcast(
        json.dumps({
            "type": "player_joined",
            "player_name": get_display_name(current_user),
            "player_count": len(player_names),
            "max_players": db_game.max_players,
            "players": player_names
        }),
        db_game.id
    )

    # Auto-start game if room is now full
    if len(player_names) >= db_game.max_players and db_game.status == "waiting":
        print(f"🚀 AUTO-STARTING GAME - Room is full ({len(player_names)}/{db_game.max_players})")
        db_game.status = "in_progress"
        db_game.started_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_game)

        # Start timer monitor if this is a timed game
        if db_game.time_limit is not None:
            start_monitor_if_needed(db)

        # Broadcast game_started to all connected players
        assert db_game.board_state is not None, "Board state must exist for started game"
        board_data = json.loads(db_game.board_state)
        await manager.broadcast(
            json.dumps({
                "type": "game_started",
                "board": board_data,
                "started_at": db_game.started_at.isoformat(),
                "time_limit": db_game.time_limit
            }),
            db_game.id
        )

    return JoinGameResponse(
        game_id=db_game.id,
        player_id=game_player.id,
        player_name=request.player_name,
        players=player_names
    )


@app.get("/games/{game_id}", response_model=GameStateResponse)
def get_game_state(
    game_id: str,
    current_user: User = Depends(get_current_user_from_db),
    db: Session = Depends(get_db)
) -> GameStateResponse:
    """Get current state of a game.

    Requires authentication and game participation.

    Args:
        game_id: Unique game identifier
        current_user: Authenticated user (injected)
        db: Database session (injected)

    Returns:
        Current game state including board, players, and status

    Raises:
        HTTPException: 404 if game not found, 403 if not a participant
    """
    from src.models import Game as GameModel, GamePlayer

    # Check if game exists
    db_game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not db_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found"
        )

    # Verify user is a participant in this game
    verify_game_participant(game_id, current_user.id, db)

    # Get board from database (stored as JSON)
    board_data = json.loads(db_game.board_state) if db_game.board_state else []

    # Get player names from database
    all_players = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()
    player_names = []
    for gp in all_players:
        user = db.query(User).filter(User.id == gp.user_id).first()
        if user:
            player_names.append(get_display_name(user))

    # Calculate time remaining if game is in progress
    time_remaining = None
    if db_game.status == "in_progress" and db_game.started_at and db_game.time_limit:
        # Ensure started_at is timezone-aware
        started_at = db_game.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
        remaining = db_game.time_limit - elapsed
        time_remaining = int(remaining) if remaining > 0 else 0

    # Get words by player from database
    words_by_player = {}
    for gp in all_players:
        words_by_player[gp.id] = json.loads(gp.words_found) if gp.words_found else []

    return GameStateResponse(
        game_id=game_id,
        board=board_data,
        status=db_game.status,
        players=player_names,
        max_players=db_game.max_players,
        time_limit=db_game.time_limit,
        started_at=db_game.started_at.isoformat() if db_game.started_at else None,
        time_remaining=time_remaining,
        words_by_player=words_by_player
    )


@app.post("/games/{game_id}/start", response_model=StartGameResponse)
async def start_game(
    game_id: str,
    current_user: User = Depends(get_current_user_from_db),
    db: Session = Depends(get_db)
) -> StartGameResponse:
    """Start a game.

    Requires authentication and game participation.

    Args:
        game_id: Unique game identifier
        current_user: Authenticated user (injected)
        db: Database session (injected)

    Returns:
        Game start confirmation with timestamp

    Raises:
        HTTPException: 404 if game not found, 403 if not a participant, 400 if already started
    """
    from src.models import Game as GameModel

    # Check if game exists
    db_game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not db_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found"
        )

    # Verify user is a participant in this game
    verify_game_participant(game_id, current_user.id, db)

    # Check if game is already started
    if db_game.status == "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game already started"
        )

    # Start the game
    db_game.status = "in_progress"
    db_game.started_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_game)

    # Start timer monitor if this is a timed game
    if db_game.time_limit is not None:
        start_monitor_if_needed(db)

    return StartGameResponse(
        game_id=db_game.id,
        status=db_game.status,
        start_time=db_game.started_at.isoformat()
    )


@app.get("/games/{game_id}/results", response_model=GameResultsResponse)
def get_game_results(
    game_id: str,
    current_user: User = Depends(get_current_user_from_db),
    db: Session = Depends(get_db)
) -> GameResultsResponse:
    """Get final game results with scores and strike-outs.

    Requires authentication and game participation.

    Args:
        game_id: Unique game identifier
        current_user: Authenticated user (injected)
        db: Database session (injected)

    Returns:
        Results for all players including valid words and duplicates

    Raises:
        HTTPException: 404 if game not found, 403 if not a participant
    """
    from src.models import Game as GameModel, GamePlayer
    from collections import Counter

    # Check if game exists
    db_game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not db_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found"
        )

    # Verify user is a participant in this game
    verify_game_participant(game_id, current_user.id, db)

    # Get all players in the game
    all_players = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()

    # Calculate duplicates (words submitted by multiple players)
    word_counter: Counter[str] = Counter()
    for gp in all_players:
        words = json.loads(gp.words_found) if gp.words_found else []
        for word in words:
            word_counter[word] += 1

    duplicates = [word for word, count in word_counter.items() if count > 1]

    # Build results for each player
    player_results = []
    for gp in all_players:
        user = db.query(User).filter(User.id == gp.user_id).first()
        if not user:
            continue  # Skip if user not found
        all_words = json.loads(gp.words_found) if gp.words_found else []

        # Valid words are those not in duplicates list
        # NOTE: This is a simplified version - we're not validating against dictionary/board
        # In a real implementation, we'd need to validate each word
        valid_words = [w for w in all_words if w not in duplicates]

        player_results.append(PlayerResult(
            name=get_display_name(user),
            score=gp.score,
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
async def websocket_endpoint(
    websocket: WebSocket,
    game_id: str,
    player_id: str,
    db: Session = Depends(get_db)
) -> None:
    """WebSocket endpoint for real-time game updates.

    Args:
        websocket: WebSocket connection
        game_id: Game identifier
        player_id: Player identifier (GamePlayer ID from database)
        db: Database session (injected)

    Handles:
        - Real-time word submissions
        - Game state broadcasts
        - Timer updates
        - Player disconnections
    """
    from src.models import Game as GameModel, GamePlayer

    try:
        # Load game from database
        db_game = db.query(GameModel).filter(GameModel.id == game_id).first()
        if not db_game:
            await websocket.close(code=1008, reason="Game not found")
            return

        # Load player from database
        db_player = db.query(GamePlayer).filter(GamePlayer.id == player_id).first()
        if not db_player or db_player.game_id != game_id:
            await websocket.close(code=1008, reason="Player not in game")
            return

        # Reconstruct Board from database
        board_data = json.loads(db_game.board_state) if db_game.board_state else []
        board = Board(size=db_game.board_size)
        board.grid = board_data

        # Create Game object for validation
        config = GameConfig(
            board_size=db_game.board_size,
            time_limit_seconds=db_game.time_limit if db_game.time_limit else 180,
            min_word_length=db_game.min_word_length
        )
        game = Game(board, dictionary, scorer, config)

        # Get user info and create Player object
        user = db.query(User).filter(User.id == db_player.user_id).first()
        if not user:
            await websocket.close(code=1008, reason="User not found")
            return
        player = Player(player_id=player_id, name=get_display_name(user))

        # Load existing words from database
        existing_words = json.loads(db_player.words_found) if db_player.words_found else []
        for word in existing_words:
            player.add_word(word)

        # Accept connection
        await manager.connect(websocket, game_id)

        # Notify others that player connected
        from src.ws_models import PlayerConnectedMessage
        connect_msg = PlayerConnectedMessage(
            type="player_connected",
            player_name=get_display_name(user)
        )
        await manager.broadcast(
            connect_msg.model_dump_json(),
            game_id,
            exclude=websocket
        )

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            raw_message = json.loads(data)

            message_type = raw_message.get("type")

            if message_type == "submit_word":
                # Validate incoming message
                from src.ws_models import SubmitWordMessage, WordResultMessage, WordSubmittedMessage
                try:
                    submit_msg = SubmitWordMessage(**raw_message)
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Invalid message format: {str(e)}"
                    }))
                    continue

                # Handle word submission
                word = submit_msg.word.upper()

                # Validate and submit word using Game object
                is_valid = game.submit_word(word, player)

                # Calculate score
                score = 0
                status_msg = ""
                if is_valid:
                    score = scorer.score_word(word)
                    status_msg = f"Valid! +{score} points"

                    # PERSIST TO DATABASE
                    words_list = json.loads(db_player.words_found) if db_player.words_found else []
                    words_list.append(word)
                    db_player.words_found = json.dumps(words_list)
                    db_player.score += score
                    db.commit()
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

                # Send response to submitter using validated model
                response = WordResultMessage(
                    type="word_result",
                    word=word,
                    valid=is_valid,
                    score=score,
                    message=status_msg
                )
                await websocket.send_text(response.model_dump_json())

                # Broadcast to others if valid
                if is_valid:
                    broadcast = WordSubmittedMessage(
                        type="word_submitted",
                        player_name=get_display_name(user),
                        word=word,
                        score=score
                    )
                    await manager.broadcast(
                        broadcast.model_dump_json(),
                        game_id,
                        exclude=websocket
                    )

            elif message_type == "get_state":
                # Validate incoming message
                from src.ws_models import GetStateMessage, GameStateMessage
                try:
                    get_state_msg = GetStateMessage(**raw_message)
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Invalid message format: {str(e)}"
                    }))
                    continue

                # Send current game state from database
                time_remaining = None
                if db_game.status == "in_progress" and db_game.started_at and db_game.time_limit:
                    # Ensure both datetimes are timezone-aware
                    now = datetime.now(timezone.utc)
                    started = db_game.started_at
                    if started.tzinfo is None:
                        started = started.replace(tzinfo=timezone.utc)
                    elapsed = (now - started).total_seconds()
                    remaining = db_game.time_limit - elapsed
                    time_remaining = int(remaining) if remaining > 0 else 0

                # Get current player count from database
                player_count = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).count()

                state_response = GameStateMessage(
                    type="game_state",
                    status=db_game.status,
                    time_remaining=time_remaining,
                    player_count=player_count
                )
                await websocket.send_text(state_response.model_dump_json())

    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
        # Notify others that player disconnected
        from src.ws_models import PlayerDisconnectedMessage
        # Get username for disconnect message
        username = get_display_name(user) if 'user' in locals() and user else "Unknown"
        disconnect_msg = PlayerDisconnectedMessage(
            type="player_disconnected",
            player_name=username
        )
        await manager.broadcast(
            disconnect_msg.model_dump_json(),
            game_id
        )

        # Cleanup: Delete waiting games when all players disconnect
        remaining_connections = manager.get_connection_count(game_id)
        if remaining_connections == 0:
            # Check if game is in waiting status
            db_game = db.query(GameModel).filter(GameModel.id == game_id).first()
            if db_game and db_game.status == "waiting":
                # Delete all players first (foreign key constraint)
                db.query(GamePlayer).filter(GamePlayer.game_id == game_id).delete()
                # Delete the game
                db.delete(db_game)
                db.commit()
                print(f"Deleted abandoned waiting game: {game_id}")


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================


@app.post("/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    """Register a new user account.

    Creates a new user with hashed password. Email must be unique.
    """
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
        email=request.email,
        password_hash=hashed_password,
        display_name=request.display_name
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
            detail="Email already registered"
        )

    return RegisterResponse(
        user_id=new_user.id,
        email=new_user.email,
        display_name=new_user.display_name,
        message="User registered successfully"
    )


@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Login and get JWT access token.

    Validates credentials and returns a JWT token that expires in 30 days.
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    # Verify user exists and password is correct
    if not user or not user.password_hash or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT token with user info
    token_data = {
        "user_id": user.id,
        "email": user.email
    }
    access_token = create_access_token(token_data, expires_delta=timedelta(days=30))

    return LoginResponse(
        access_token=access_token,
        token_type="bearer"
    )


@app.post("/auth/google", response_model=LoginResponse)
def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Authenticate with Google OAuth and get JWT access token.

    Verifies Google ID token and creates user if doesn't exist, or links OAuth to existing email.
    Returns JWT token for subsequent API calls.
    """
    try:
        # Verify the Google ID token
        # This will raise ValueError if token is invalid
        idinfo = id_token.verify_oauth2_token(
            request.id_token,
            google_requests.Request(),
            # We'll pass client_id from environment later, for now accept any
            None
        )

        # Extract user info from verified token
        email = idinfo.get('email')
        google_id = idinfo.get('sub')  # Google's unique user ID
        name = idinfo.get('name')  # Full name from Google profile

        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google token: missing email or user ID"
            )

    except ValueError as e:
        # Token verification failed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google ID token: {str(e)}"
        )

    # Check if user with this email already exists
    user = db.query(User).filter(User.email == email).first()

    if user:
        # User exists - link OAuth if not already linked
        if not user.oauth_provider:
            user.oauth_provider = "google"
            user.oauth_id = google_id
            db.commit()
            db.refresh(user)
    else:
        # Create new user with OAuth
        user = User(
            email=email,
            password_hash=None,  # No password for OAuth users
            display_name=name,  # Use Google profile name
            oauth_provider="google",
            oauth_id=google_id
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            # Handle race condition where user was created between check and insert
            db.rollback()
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user account"
                )

    # Create JWT token
    token_data = {
        "user_id": user.id,
        "email": user.email
    }
    access_token = create_access_token(token_data, expires_delta=timedelta(days=30))

    return LoginResponse(
        access_token=access_token,
        token_type="bearer"
    )


@app.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user_from_db)) -> UserResponse:
    """Get current authenticated user information.

    This is a test endpoint to verify JWT authentication works.
    Requires a valid JWT token in the Authorization header.
    """
    return UserResponse(
        user_id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name
    )
