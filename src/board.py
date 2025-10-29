# ABOUTME: Board class for generating and managing the Boggle game board
# ABOUTME: Supports configurable 4x4 or 5x5 grids with random letter dice

import random
from typing import List, Set, Tuple


class Board:
    """Represents a Boggle game board with a grid of letter dice."""
    
    # Standard Boggle 4x4 dice (16 dice)
    DICE_4X4 = [
        "AAEEGN", "ABBJOO", "ACHOPS", "AFFKPS",
        "AOOTTW", "CIMOTU", "DEILRX", "DELRVY",
        "DISTTY", "EEGHNW", "EEINSU", "EHRTVW",
        "EIOSST", "ELRTTY", "HIMNQU", "HLNNRZ"
    ]
    
    # Big Boggle 5x5 dice (25 dice)
    DICE_5X5 = [
        "AAAFRS", "AAEEEE", "AAFIRS", "ADENNN", "AEEEEM",
        "AEEGMU", "AEGMNN", "AFIRSY", "BJKQXZ", "CCENST",
        "CEIILT", "CEILPT", "CEIPST", "DDHNOT", "DHHLOR",
        "DHLNOR", "DHLNOR", "EIIITT", "EMOTTT", "ENSSSU",
        "FIPRSY", "GORRVW", "IPRRRY", "NOOTUW", "OOOTTU"
    ]
    
    def __init__(self, size: int) -> None:
        """Initialize a board with the given size.
        
        Args:
            size: The size of the board (4 for 4x4, 5 for 5x5)
            
        Raises:
            ValueError: If size is not 4 or 5
        """
        if size not in (4, 5):
            raise ValueError(f"Board size must be 4 or 5, got {size}")
        
        self.size = size
        self.grid: List[List[str]] = self._generate_grid()
    
    def _generate_grid(self) -> List[List[str]]:
        """Generate a random board grid using actual Boggle dice.
        
        Returns:
            A 2D list representing the board grid
        """
        # Choose appropriate dice set
        dice = self.DICE_4X4 if self.size == 4 else self.DICE_5X5
        
        # Shuffle the dice and pick one face from each
        shuffled_dice = dice.copy()
        random.shuffle(shuffled_dice)
        letters = [random.choice(die) for die in shuffled_dice]
        
        # Arrange into grid
        grid = []
        for i in range(self.size):
            row = letters[i * self.size:(i + 1) * self.size]
            grid.append(row)
        
        return grid
    
    def has_word_path(self, word: str) -> bool:
        """Check if a word can be formed following a valid path on the board.
        
        A valid path means:
        - Each letter is adjacent to the next (including diagonals)
        - No cell is used more than once
        
        Args:
            word: The word to search for (case-insensitive)
            
        Returns:
            True if the word exists on a valid path, False otherwise
        """
        if not word:
            return False
        
        word = word.upper()
        
        # Try starting from each cell
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == word[0]:
                    # Found first letter, try DFS from here
                    visited: Set[Tuple[int, int]] = set()
                    if self._dfs_word_search(word, 0, row, col, visited):
                        return True
        
        return False
    
    def _dfs_word_search(
        self,
        word: str,
        word_index: int,
        row: int,
        col: int,
        visited: Set[Tuple[int, int]]
    ) -> bool:
        """Depth-first search to find if word can be formed from this position.
        
        Args:
            word: The word we're searching for
            word_index: Current index in the word we're trying to match
            row: Current row position on board
            col: Current column position on board
            visited: Set of (row, col) coordinates already used in this path
            
        Returns:
            True if word can be formed from this position, False otherwise
        """
        # Base case: we've matched the entire word
        if word_index == len(word):
            return True
        
        # Check bounds
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
        
        # Check if already visited
        if (row, col) in visited:
            return False
        
        # Check if current cell matches current letter
        if self.grid[row][col] != word[word_index]:
            return False
        
        # Mark as visited
        visited.add((row, col))
        
        # Try all 8 adjacent directions
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # Top-left, top, top-right
            (0, -1),           (0, 1),    # Left, right
            (1, -1),  (1, 0),  (1, 1)     # Bottom-left, bottom, bottom-right
        ]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self._dfs_word_search(word, word_index + 1, new_row, new_col, visited):
                return True
        
        # Backtrack: remove from visited for other paths to use
        visited.remove((row, col))
        
        return False
