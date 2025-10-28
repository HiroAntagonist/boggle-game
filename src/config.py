# ABOUTME: Game configuration with validation
# ABOUTME: Uses Pydantic for type-safe, validated settings

from pydantic import BaseModel, Field, field_validator


class GameConfig(BaseModel):
    """Configuration settings for a Boggle game.
    
    All fields are validated and the config is immutable after creation.
    """
    
    board_size: int = Field(
        default=4,
        description="Size of the board (4 for 4x4, 5 for 5x5)"
    )
    
    time_limit_seconds: int = Field(
        default=180,
        description="Game duration in seconds"
    )
    
    min_word_length: int = Field(
        default=3,
        description="Minimum length for valid words"
    )
    
    max_players: int = Field(
        default=4,
        description="Maximum number of players"
    )
    
    model_config = {
        "frozen": True,  # Makes the config immutable
        "validate_assignment": True  # Validate even when trying to assign
    }
    
    @field_validator("board_size")
    @classmethod
    def validate_board_size(cls, v: int) -> int:
        """Validate board size is 4 or 5."""
        if v not in (4, 5):
            raise ValueError("board_size must be 4 or 5")
        return v
    
    @field_validator("time_limit_seconds")
    @classmethod
    def validate_time_limit(cls, v: int) -> int:
        """Validate time limit is positive."""
        if v <= 0:
            raise ValueError("time_limit_seconds must be positive")
        return v
    
    @field_validator("min_word_length")
    @classmethod
    def validate_min_word_length(cls, v: int) -> int:
        """Validate minimum word length is positive."""
        if v <= 0:
            raise ValueError("min_word_length must be at least 1")
        return v
    
    @field_validator("max_players")
    @classmethod
    def validate_max_players(cls, v: int) -> int:
        """Validate max players is between 1 and 8."""
        if v < 1 or v > 8:
            raise ValueError("max_players must be between 1 and 8")
        return v
