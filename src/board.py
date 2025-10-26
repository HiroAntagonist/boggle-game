# ABOUTME: Board class for generating and managing the Boggle game board
# ABOUTME: Supports configurable 4x4 or 5x5 grids with random letter dice

import random
from typing import List


class Board:
    """Represents a Boggle game board with a grid of letter dice."""
    
    # Standard Boggle dice (16 dice for 4x4, we'll expand for 5x5 later)
    DICE_4X4 = [
        "AAEEGN", "ABBJOO", "ACHOPS", "AFFKPS",
        "AOOTTW", "CIMOTU", "DEILRX", "DELRVY",
        "DISTTY", "EEGHNW", "EEINSU", "EHRTVW",
        "EIOSST", "ELRTTY", "HIMNQU", "HLNNRZ"
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
        """Generate a random board grid.
        
        Returns:
            A 2D list representing the board grid
        """
        if self.size == 4:
            # Shuffle the dice and pick one face from each
            dice = self.DICE_4X4.copy()
            random.shuffle(dice)
            letters = [random.choice(die) for die in dice]
            
            # Arrange into 4x4 grid
            grid = []
            for i in range(4):
                row = letters[i * 4:(i + 1) * 4]
                grid.append(row)
            return grid
        else:
            # For 5x5, we'll use random letters for now
            # TODO: Add proper 5x5 Boggle dice in the future
            letters = []
            for _ in range(25):
                letters.append(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
            
            grid = []
            for i in range(5):
                row = letters[i * 5:(i + 1) * 5]
                grid.append(row)
            return grid