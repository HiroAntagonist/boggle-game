# ABOUTME: Pydantic models for FastAPI request/response validation
# ABOUTME: Defines data structures for REST API endpoints

from pydantic import BaseModel, Field
from typing import List, Dict


class CreateGameRequest(BaseModel):
    """Request model for creating a new game."""
    board_size: int = Field(default=4, ge=4, le=5, description="Board size (4 or 5)")
    time_limit_seconds: int = Field(default=180, gt=0, le=600, description="Game time limit in seconds (max 10 minutes)")
    max_players: int = Field(default=4, ge=1, le=8, description="Maximum number of players")


class CreateGameResponse(BaseModel):
    """Response model after creating a game."""
    game_id: str = Field(description="Unique game identifier")
    friendly_code: str = Field(description="Human-readable game code (XXXX-XXXX format)")
    board: List[List[str]] = Field(description="Game board grid")
    created_at: str = Field(description="ISO timestamp of game creation")
    status: str = Field(description="Game status (waiting, in_progress, finished)")


class JoinGameRequest(BaseModel):
    """Request model for joining a game."""
    player_name: str = Field(min_length=1, max_length=50, description="Player's display name")


class JoinGameResponse(BaseModel):
    """Response model after joining a game.

    Includes full game state to enable immediate gameplay without additional API calls.
    """
    game_id: str = Field(description="Game identifier")
    player_id: str = Field(description="Unique player identifier")
    player_name: str = Field(description="Player's display name")
    # Full game state
    board: List[List[str]] = Field(description="Game board grid")
    status: str = Field(description="Game status (created, waiting, in_progress, finished)")
    players: List[str] = Field(description="List of all player names in game")
    player_count: int = Field(description="Current number of players in game")
    max_players: int = Field(description="Maximum number of players allowed")
    time_limit: int | None = Field(description="Total time limit in seconds, None if no time limit")
    started_at: str | None = Field(description="ISO timestamp of when game started, None if not started")
    time_remaining: int | None = Field(description="Seconds remaining, None if not started")
    words_by_player: Dict[str, List[str]] = Field(description="Player ID to their submitted words")


class LeaveGameResponse(BaseModel):
    """Response model after leaving a game."""
    game_id: str = Field(description="Game identifier")
    status: str = Field(description="Game status after player left")
    player_count: int = Field(description="Remaining player count")


class GameStateResponse(BaseModel):
    """Response model for getting game state."""
    game_id: str
    board: List[List[str]]
    players: List[str]
    status: str
    player_count: int = Field(description="Current number of players in game")
    max_players: int
    time_limit: int | None = Field(description="Total time limit in seconds, None if no time limit")
    started_at: str | None = Field(description="ISO timestamp of when game started, None if not started")
    time_remaining: int | None = Field(description="Seconds remaining, None if not started")
    words_by_player: Dict[str, List[str]] = Field(description="Player ID to their submitted words")


class StartGameResponse(BaseModel):
    """Response model after starting a game."""
    game_id: str
    status: str
    start_time: str = Field(description="ISO timestamp of game start")


class PlayerResult(BaseModel):
    """Result for a single player."""
    name: str
    score: int
    words: List[str] = Field(description="All words submitted")
    valid_words: List[str] = Field(description="Valid words after strike-out")


class GameResultsResponse(BaseModel):
    """Response model for game results."""
    players: List[PlayerResult]
    duplicates: List[str] = Field(description="Words that were struck out")


# ============================================================================
# AUTHENTICATION MODELS
# ============================================================================


class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: str = Field(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(min_length=8)
    display_name: str | None = Field(default=None, min_length=1, max_length=50, description="Optional display name")


class RegisterResponse(BaseModel):
    """Response model after successful registration."""
    user_id: str
    email: str
    display_name: str | None
    message: str


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Response model after successful login."""
    access_token: str
    token_type: str = "bearer"


class GoogleAuthRequest(BaseModel):
    """Request model for Google OAuth authentication."""
    id_token: str = Field(description="Google ID token from native SDK")


class UserResponse(BaseModel):
    """Response model for user information."""
    user_id: str
    email: str
    display_name: str | None


class DatabaseHealth(BaseModel):
    """Database health metrics."""
    connected: bool
    response_time_ms: int


class WebSocketHealth(BaseModel):
    """WebSocket connection metrics."""
    total_connections: int
    connections_by_game: Dict[str, int]


class TimerMonitorHealth(BaseModel):
    """Background timer monitor status."""
    running: bool
    active_games_count: int


class BackgroundTasksHealth(BaseModel):
    """Background tasks health metrics."""
    timer_monitor: TimerMonitorHealth


class GamesHealth(BaseModel):
    """Game statistics."""
    total: int
    in_progress: int
    waiting: int
    finished: int


class HealthCheckResponse(BaseModel):
    """Overall health check response."""
    status: str = Field(description="Overall status: healthy or degraded")
    timestamp: str = Field(description="ISO timestamp of health check")
    database: DatabaseHealth
    websockets: WebSocketHealth
    background_tasks: BackgroundTasksHealth
    games: GamesHealth
