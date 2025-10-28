# ABOUTME: Tests for GameConfig configuration class
# ABOUTME: Uses Pydantic for validation of game settings

import pytest
from pydantic import ValidationError
from src.config import GameConfig


def test_config_with_default_values() -> None:
    """GameConfig should have sensible defaults."""
    config = GameConfig()
    
    assert config.board_size == 4
    assert config.time_limit_seconds == 180
    assert config.min_word_length == 3
    assert config.max_players == 4


def test_config_with_custom_values() -> None:
    """GameConfig should accept custom values."""
    config = GameConfig(
        board_size=5,
        time_limit_seconds=240,
        min_word_length=4,
        max_players=2
    )
    
    assert config.board_size == 5
    assert config.time_limit_seconds == 240
    assert config.min_word_length == 4
    assert config.max_players == 2


def test_board_size_must_be_4_or_5() -> None:
    """Board size must be 4 or 5."""
    # Valid sizes
    config = GameConfig(board_size=4)
    assert config.board_size == 4
    
    config = GameConfig(board_size=5)
    assert config.board_size == 5
    
    # Invalid sizes should raise ValidationError
    with pytest.raises(ValidationError):
        GameConfig(board_size=3)
    
    with pytest.raises(ValidationError):
        GameConfig(board_size=6)


def test_time_limit_must_be_positive() -> None:
    """Time limit must be positive."""
    config = GameConfig(time_limit_seconds=60)
    assert config.time_limit_seconds == 60
    
    # Zero or negative should fail
    with pytest.raises(ValidationError):
        GameConfig(time_limit_seconds=0)
    
    with pytest.raises(ValidationError):
        GameConfig(time_limit_seconds=-10)


def test_min_word_length_must_be_positive() -> None:
    """Minimum word length must be at least 1."""
    config = GameConfig(min_word_length=2)
    assert config.min_word_length == 2
    
    # Zero or negative should fail
    with pytest.raises(ValidationError):
        GameConfig(min_word_length=0)
    
    with pytest.raises(ValidationError):
        GameConfig(min_word_length=-1)


def test_max_players_between_1_and_8() -> None:
    """Max players should be between 1 and 8."""
    config = GameConfig(max_players=1)
    assert config.max_players == 1
    
    config = GameConfig(max_players=8)
    assert config.max_players == 8
    
    # Outside range should fail
    with pytest.raises(ValidationError):
        GameConfig(max_players=0)
    
    with pytest.raises(ValidationError):
        GameConfig(max_players=9)


def test_config_is_immutable() -> None:
    """Config should be immutable after creation (frozen)."""
    config = GameConfig()
    
    # Should not be able to modify after creation
    with pytest.raises(ValidationError):
        config.board_size = 5  # type: ignore
