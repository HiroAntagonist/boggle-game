# ABOUTME: Dictionary class for validating words against a word list
# ABOUTME: Uses a set for O(1) lookup performance

from typing import Set


class Dictionary:
    """Validates words against a dictionary loaded from a file."""
    
    def __init__(self, filepath: str) -> None:
        """Initialize dictionary by loading words from a file.
        
        Args:
            filepath: Path to the dictionary file (one word per line)
        """
        self._words: Set[str] = self._load_words(filepath)
    
    def _load_words(self, filepath: str) -> Set[str]:
        """Load words from file into a set.
        
        Args:
            filepath: Path to the dictionary file
            
        Returns:
            Set of uppercase words
        """
        words: Set[str] = set()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().upper()
                if word:  # Skip empty lines
                    words.add(word)
        
        return words
    
    def is_valid_word(self, word: str) -> bool:
        """Check if a word is in the dictionary.
        
        Args:
            word: The word to validate (case-insensitive)
            
        Returns:
            True if word is valid, False otherwise
        """
        if not word or not word.strip():
            return False
        
        return word.upper() in self._words
    
    def __len__(self) -> int:
        """Return the number of words in the dictionary."""
        return len(self._words)
