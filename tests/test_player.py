# ABOUTME: Tests for the Player class
# ABOUTME: Represents a player in a multiplayer game

from src.player import Player


def test_player_initialization() -> None:
    """Player should initialize with id and name."""
    player = Player(player_id="p1", name="Alice")
    
    assert player.player_id == "p1"
    assert player.name == "Alice"
    assert player.words == []


def test_player_add_word() -> None:
    """Player should be able to add words."""
    player = Player(player_id="p1", name="Alice")
    
    player.add_word("CAT")
    assert "CAT" in player.words
    assert len(player.words) == 1
    
    player.add_word("DOG")
    assert "DOG" in player.words
    assert len(player.words) == 2


def test_player_cannot_add_duplicate_word() -> None:
    """Player cannot add the same word twice."""
    player = Player(player_id="p1", name="Alice")
    
    result1 = player.add_word("CAT")
    assert result1 is True
    assert len(player.words) == 1
    
    result2 = player.add_word("CAT")
    assert result2 is False
    assert len(player.words) == 1  # Still just one


def test_player_words_are_uppercase() -> None:
    """Words should be stored in uppercase."""
    player = Player(player_id="p1", name="Alice")
    
    player.add_word("cat")
    assert "CAT" in player.words
    assert "cat" not in player.words


def test_player_get_words() -> None:
    """Should return list of player's words."""
    player = Player(player_id="p1", name="Alice")
    
    player.add_word("CAT")
    player.add_word("DOG")
    player.add_word("FISH")
    
    words = player.get_words()
    assert len(words) == 3
    assert "CAT" in words
    assert "DOG" in words
    assert "FISH" in words


def test_player_equality() -> None:
    """Players with same ID should be equal."""
    player1 = Player(player_id="p1", name="Alice")
    player2 = Player(player_id="p1", name="Bob")  # Same ID, different name
    player3 = Player(player_id="p2", name="Alice")  # Different ID, same name
    
    assert player1 == player2  # Same ID
    assert player1 != player3  # Different ID
