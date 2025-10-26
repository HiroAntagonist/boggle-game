# ABOUTME: Scorer class for calculating Boggle word scores
# ABOUTME: Uses Fibonacci sequence based on word length

from typing import List


class Scorer:
    """Calculates scores for Boggle words using Fibonacci sequence."""
    
    def __init__(self, min_word_length: int = 3) -> None:
        """Initialize scorer with minimum word length.
        
        Args:
            min_word_length: Minimum length for a word to score points
        """
        self.min_word_length = min_word_length
        self._fibonacci_cache: List[int] = self._generate_fibonacci(20)
    
    def _generate_fibonacci(self, n: int) -> List[int]:
        """Generate first n Fibonacci numbers.
        
        Args:
            n: How many Fibonacci numbers to generate
            
        Returns:
            List of Fibonacci numbers [1, 2, 3, 5, 8, 13, ...]
        """
        if n == 0:
            return []
        if n == 1:
            return [1]
        
        fib = [1, 2]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        
        return fib
    
    def score_word(self, word: str) -> int:
        """Calculate score for a single word.
        
        Scoring rules:
        - Words below minimum length: 0 points
        - First valid length (min_word_length): 1 point
        - Each additional letter follows Fibonacci: 1, 2, 3, 5, 8, 13, 21...
        
        Args:
            word: The word to score (case-insensitive)
            
        Returns:
            Score for the word
        """
        if not word:
            return 0
        
        word_length = len(word)
        
        if word_length < self.min_word_length:
            return 0
        
        # Calculate index into Fibonacci sequence
        # First valid length gets index 0 (Fib[0] = 1)
        # Second valid length gets index 1 (Fib[1] = 2)
        # etc.
        fib_index = word_length - self.min_word_length
        
        # Ensure we have enough Fibonacci numbers cached
        if fib_index >= len(self._fibonacci_cache):
            # Should be rare for normal Boggle words
            return self._fibonacci_cache[-1]
        
        return self._fibonacci_cache[fib_index]
    
    def score_words(self, words: List[str]) -> int:
        """Calculate total score for a list of words.
        
        Args:
            words: List of words to score
            
        Returns:
            Total score across all words
        """
        return sum(self.score_word(word) for word in words)
