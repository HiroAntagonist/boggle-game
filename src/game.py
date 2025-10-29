# ABOUTME: Game class orchestrating Boggle game logic
# ABOUTME: Combines Board, Dictionary, and Scorer for complete game flow

import time
from typing import List, Dict
from src.board import Board
from src.dictionary import Dictionary
from src.scorer import Scorer
from src.config import GameConfig
from src.player import Player


class Game:
    """Orchestrates a Boggle game with word validation and scoring."""
    
    def __init__(
        self,
        board: Board,
        dictionary: Dictionary,
        scorer: Scorer,
        config: GameConfig | None = None
    ) -> None:
        """Initialize a game with its components.
        
        Args:
            board: The game board
            dictionary: Word validator
            scorer: Scoring calculator
            config: Game configuration (uses defaults if not provided)
        """
        self.board = board
        self.dictionary = dictionary
        self.scorer = scorer
        self.config = config or GameConfig()
        self._submitted_words: List[str] = []  # For backward compatibility (single player)
        self._players: Dict[str, Player] = {}  # player_id -> Player
        self._rotation = 0  # 0, 1, 2, or 3 (number of 90° clockwise rotations)
        self.start_time: float | None = None  # Game start timestamp
    
    def submit_word(self, word: str, player: Player | None = None) -> bool:
        """Submit a word for validation and scoring.
        
        A word is valid if:
        1. It meets minimum length requirement
        2. It exists in the dictionary
        3. It can be formed on the board
        4. Player hasn't submitted it already (if multiplayer)
        
        Args:
            word: The word to submit (case-insensitive)
            player: The player submitting (for multiplayer), None for single-player
            
        Returns:
            True if word is valid and accepted, False otherwise
        """
        if not word:
            return False
        
        word = word.upper()
        
        # Multiplayer mode
        if player is not None:
            # Check if player already submitted this word
            if word in player.get_words():
                return False
            
            # Validate word
            if not self._validate_word(word):
                return False
            
            # Add to player's words
            return player.add_word(word)
        
        # Single-player mode (backward compatibility)
        else:
            # Check if already submitted
            if word in self._submitted_words:
                return False
            
            # Validate word
            if not self._validate_word(word):
                return False
            
            # All checks passed - accept the word
            self._submitted_words.append(word)
            return True
    
    def _validate_word(self, word: str) -> bool:
        """Validate a word against game rules.
        
        Args:
            word: The word to validate (already uppercase)
            
        Returns:
            True if word is valid, False otherwise
        """
        # Check minimum length
        if len(word) < self.scorer.min_word_length:
            return False
        
        # Check if in dictionary
        if not self.dictionary.is_valid_word(word):
            return False
        
        # Check if on board
        if not self.board.has_word_path(word):
            return False
        
        return True
    
    def add_player(self, player: Player) -> bool:
        """Add a player to the game.
        
        Args:
            player: The player to add
            
        Returns:
            True if player was added, False if game is full or player already exists
        """
        if len(self._players) >= self.config.max_players:
            return False
        
        if player.player_id in self._players:
            return False
        
        self._players[player.player_id] = player
        return True
    
    def get_players(self) -> List[Player]:
        """Get list of players in the game.
        
        Returns:
            List of players
        """
        return list(self._players.values())
    
    def get_duplicate_words(self) -> set[str]:
        """Find words that were submitted by multiple players.
        
        Returns:
            Set of words that appear in more than one player's list
        """
        word_counts: Dict[str, int] = {}
        
        # Count how many players have each word
        for player in self._players.values():
            for word in player.get_words():
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Return words that appear more than once
        return {word for word, count in word_counts.items() if count > 1}
    
    def get_player_valid_words(self, player: Player) -> List[str]:
        """Get player's words excluding struck-out duplicates.
        
        Args:
            player: The player
            
        Returns:
            List of valid (non-struck-out) words
        """
        duplicates = self.get_duplicate_words()
        return [word for word in player.get_words() if word not in duplicates]
    
    def get_player_score(self, player: Player) -> int:
        """Calculate player's score excluding struck-out words.
        
        Args:
            player: The player
            
        Returns:
            Player's score (only counting unique words)
        """
        valid_words = self.get_player_valid_words(player)
        return self.scorer.score_words(valid_words)
    
    def get_submitted_words(self) -> List[str]:
        """Get list of successfully submitted words.
        
        Returns:
            List of submitted words
        """
        return self._submitted_words.copy()
    
    def get_score(self) -> int:
        """Calculate total score for all submitted words.
        
        Returns:
            Total score
        """
        return self.scorer.score_words(self._submitted_words)
    
    def rotate_view_clockwise(self) -> None:
        """Rotate the board view 90 degrees clockwise.
        
        This is purely a visual aid - the board data itself is unchanged.
        Word validation always uses the original grid orientation.
        """
        self._rotation = (self._rotation + 1) % 4
    
    def get_rotation(self) -> int:
        """Get the current rotation state.
        
        Returns:
            Rotation value: 0 (no rotation), 1 (90°), 2 (180°), or 3 (270°)
        """
        return self._rotation
    
    def start_timer(self) -> None:
        """Start the game timer."""
        self.start_time = time.time()
    
    def get_elapsed_time(self) -> float | None:
        """Get elapsed time since game started.
        
        Returns:
            Elapsed time in seconds, or None if timer not started
        """
        if self.start_time is None:
            return None
        return time.time() - self.start_time
    
    def get_remaining_time(self) -> float | None:
        """Get remaining time until time limit expires.
        
        Returns:
            Remaining time in seconds, or None if timer not started
        """
        elapsed = self.get_elapsed_time()
        if elapsed is None:
            return None
        return max(0, self.config.time_limit_seconds - elapsed)
    
    def is_time_expired(self) -> bool:
        """Check if the time limit has been exceeded.
        
        Returns:
            True if time limit exceeded, False otherwise (or if no timer)
        """
        remaining = self.get_remaining_time()
        if remaining is None:
            return False
        return remaining <= 0
