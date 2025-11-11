# ABOUTME: Pydantic models for WebSocket message validation
# ABOUTME: Defines typed messages for real-time game communication

from pydantic import BaseModel, Field
from typing import Literal


# ============================================================================
# CLIENT → SERVER MESSAGES
# ============================================================================

class SubmitWordMessage(BaseModel):
    """Client request to submit a word for validation.

    Example:
        {"type": "submit_word", "word": "CAT"}
    """
    type: Literal["submit_word"]
    word: str = Field(min_length=1, max_length=20, description="Word to validate")


class GetStateMessage(BaseModel):
    """Client request for current game state.

    Example:
        {"type": "get_state"}
    """
    type: Literal["get_state"]


# ============================================================================
# SERVER → CLIENT MESSAGES
# ============================================================================

class WordResultMessage(BaseModel):
    """Server response to word submission.

    Sent to the player who submitted the word.

    Example:
        {
            "type": "word_result",
            "word": "CAT",
            "valid": true,
            "score": 1,
            "message": "Valid! +1 points"
        }
    """
    type: Literal["word_result"]
    word: str = Field(description="The word that was submitted")
    valid: bool = Field(description="Whether the word was valid")
    score: int = Field(ge=0, description="Points awarded (0 if invalid)")
    message: str = Field(description="Human-readable validation message")


class WordSubmittedMessage(BaseModel):
    """Server broadcast when a player submits a valid word.

    Sent to all other players (not the submitter).

    Example:
        {
            "type": "word_submitted",
            "player_name": "alice",
            "word": "CAT",
            "score": 1
        }
    """
    type: Literal["word_submitted"]
    player_name: str = Field(description="Username of player who submitted")
    word: str = Field(description="The word that was submitted")
    score: int = Field(ge=0, description="Points awarded")


class GameStateMessage(BaseModel):
    """Server response with current game state.

    Example:
        {
            "type": "game_state",
            "status": "in_progress",
            "time_remaining": 150,
            "player_count": 2
        }
    """
    type: Literal["game_state"]
    status: str = Field(description="Game status (waiting, in_progress, finished)")
    time_remaining: int | None = Field(description="Seconds remaining, None if no timer")
    player_count: int = Field(ge=0, description="Number of players in game")


class PlayerConnectedMessage(BaseModel):
    """Server broadcast when a player connects.

    Example:
        {
            "type": "player_connected",
            "player_name": "bob"
        }
    """
    type: Literal["player_connected"]
    player_name: str = Field(description="Username of connected player")


class PlayerDisconnectedMessage(BaseModel):
    """Server broadcast when a player disconnects.

    Example:
        {
            "type": "player_disconnected",
            "player_name": "bob"
        }
    """
    type: Literal["player_disconnected"]
    player_name: str = Field(description="Username of disconnected player")


class GameStartedMessage(BaseModel):
    """Server broadcast when a game starts.

    Example:
        {
            "type": "game_started",
            "board": [["A", "B"], ["C", "D"]],
            "started_at": "2025-11-11T12:00:00Z",
            "time_limit": 180
        }
    """
    type: Literal["game_started"]
    board: list[list[str]] = Field(description="Game board grid")
    started_at: str = Field(description="ISO 8601 timestamp when game started")
    time_limit: int | None = Field(description="Time limit in seconds, None if no timer")


class PlayerWordResult(BaseModel):
    """Result for a single word submitted by a player."""
    word: str = Field(description="The word")
    score: int = Field(ge=0, description="Points awarded")
    valid: bool = Field(description="Whether word was valid after duplicate removal")


class PlayerFinalResult(BaseModel):
    """Final results for a single player."""
    player_name: str = Field(description="Username of player")
    words: list[PlayerWordResult] = Field(description="All words submitted by this player")
    total_score: int = Field(ge=0, description="Final score after duplicate removal")


class GameEndedMessage(BaseModel):
    """Server broadcast when a game ends.

    Contains final results for all players, with duplicates removed.

    Example:
        {
            "type": "game_ended",
            "winner": "alice",
            "results": [
                {
                    "player_name": "alice",
                    "words": [{"word": "CAT", "score": 1, "valid": true}],
                    "total_score": 1
                },
                {
                    "player_name": "bob",
                    "words": [{"word": "DOG", "score": 1, "valid": true}],
                    "total_score": 1
                }
            ]
        }
    """
    type: Literal["game_ended"]
    winner: str | None = Field(description="Username of winner, None if tie")
    results: list[PlayerFinalResult] = Field(description="Final results for all players")
