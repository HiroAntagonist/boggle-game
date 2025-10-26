# ABOUTME: Game class orchestrating Boggle game logic
# ABOUTME: Combines Board, Dictionary, and Scorer for complete game flow

from typing import List
from src.board import Board
from src.dictionary import Dictionary
from src.scorer import Scorer


class Game:
    """Orchestrates a Boggle game with word validation and scoring."""
    
    def __init__(
        self,
        board: Board,
        dictionary: Dictionary,
        scorer: Scorer
    ) -> None:
        """Initialize a game with its components.
        
        Args:
            board: The game board
            dictionary: Word validator
            scorer: Scoring calculator
        """
        self.board = board
        self.dictionary = dictionary
        self.scorer = scorer
        self._submitted_words: List[str] = []
        self._rotation = 0  # 0, 1, 2, or 3 (number of 90° clockwise rotations)
    
    def submit_word(self, word: str) -> bool:
        """Submit a word for validation and scoring.
        
        A word is valid if:
        1. It meets minimum length requirement
        2. It exists in the dictionary
        3. It can be formed on the board
        4. It hasn't been submitted already
        
        Args:
            word: The word to submit (case-insensitive)
            
        Returns:
            True if word is valid and accepted, False otherwise
        """
        if not word:
            return False
        
        word = word.upper()
        
        # Check if already submitted
        if word in self._submitted_words:
            return False
        
        # Check minimum length
        if len(word) < self.scorer.min_word_length:
            return False
        
        # Check if in dictionary
        if not self.dictionary.is_valid_word(word):
            return False
        
        # Check if on board
        if not self.board.has_word_path(word):
            return False
        
        # All checks passed - accept the word
        self._submitted_words.append(word)
        return True
    
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
