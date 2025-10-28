# ABOUTME: Player class for multiplayer Boggle games
# ABOUTME: Tracks individual player state (name, words, score)

from typing import List


class Player:
    """Represents a player in a multiplayer Boggle game."""
    
    def __init__(self, player_id: str, name: str) -> None:
        """Initialize a player.
        
        Args:
            player_id: Unique identifier for the player
            name: Display name for the player
        """
        self.player_id = player_id
        self.name = name
        self._words: List[str] = []
    
    def add_word(self, word: str) -> bool:
        """Add a word to the player's list.
        
        Args:
            word: The word to add (case-insensitive)
            
        Returns:
            True if word was added, False if it was a duplicate
        """
        word = word.upper()
        
        if word in self._words:
            return False
        
        self._words.append(word)
        return True
    
    def get_words(self) -> List[str]:
        """Get a copy of the player's words.
        
        Returns:
            List of words submitted by this player
        """
        return self._words.copy()
    
    @property
    def words(self) -> List[str]:
        """Property access to player's words."""
        return self._words
    
    def __eq__(self, other: object) -> bool:
        """Players are equal if they have the same ID."""
        if not isinstance(other, Player):
            return False
        return self.player_id == other.player_id
    
    def __hash__(self) -> int:
        """Hash based on player ID."""
        return hash(self.player_id)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Player(id={self.player_id}, name={self.name}, words={len(self._words)})"
