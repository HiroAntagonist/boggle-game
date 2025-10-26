# ABOUTME: Tests for the Scorer class
# ABOUTME: Validates Fibonacci-based scoring for Boggle words

from src.scorer import Scorer


def test_three_letter_word_scores_one() -> None:
    """3-letter words should score 1 point."""
    scorer = Scorer(min_word_length=3)
    
    assert scorer.score_word("CAT") == 1
    assert scorer.score_word("DOG") == 1


def test_four_letter_word_scores_two() -> None:
    """4-letter words should score 2 points."""
    scorer = Scorer(min_word_length=3)
    
    assert scorer.score_word("CATS") == 2
    assert scorer.score_word("DOGS") == 2


def test_fibonacci_progression() -> None:
    """Longer words follow Fibonacci sequence: 1, 2, 3, 5, 8, 13, 21..."""
    scorer = Scorer(min_word_length=3)
    
    assert scorer.score_word("CAT") == 1      # 3 letters
    assert scorer.score_word("CATS") == 2     # 4 letters
    assert scorer.score_word("TIGER") == 3    # 5 letters
    assert scorer.score_word("TIGERS") == 5   # 6 letters
    assert scorer.score_word("PLAYING") == 8  # 7 letters
    assert scorer.score_word("COMPUTER") == 13  # 8 letters


def test_word_below_minimum_length_scores_zero() -> None:
    """Words below minimum length should score 0."""
    scorer = Scorer(min_word_length=3)
    
    assert scorer.score_word("A") == 0
    assert scorer.score_word("AT") == 0


def test_configurable_minimum_length() -> None:
    """Minimum word length should be configurable."""
    scorer = Scorer(min_word_length=4)
    
    # 3-letter words now score 0
    assert scorer.score_word("CAT") == 0
    
    # 4-letter words score 1 (first valid length)
    assert scorer.score_word("CATS") == 1
    
    # 5-letter words score 2 (second valid length)
    assert scorer.score_word("TIGER") == 2


def test_empty_word_scores_zero() -> None:
    """Empty string should score 0."""
    scorer = Scorer(min_word_length=3)
    
    assert scorer.score_word("") == 0


def test_case_insensitive_scoring() -> None:
    """Scoring should be case-insensitive."""
    scorer = Scorer(min_word_length=3)
    
    assert scorer.score_word("cat") == 1
    assert scorer.score_word("CAT") == 1
    assert scorer.score_word("CaT") == 1


def test_score_multiple_words() -> None:
    """Should be able to score a list of words."""
    scorer = Scorer(min_word_length=3)
    
    words = ["CAT", "DOGS", "TIGER"]
    total = scorer.score_words(words)
    
    # CAT=1, DOGS=2, TIGER=3, total=6
    assert total == 6


def test_score_words_with_invalid_lengths() -> None:
    """score_words should skip words below minimum length."""
    scorer = Scorer(min_word_length=3)
    
    words = ["A", "AT", "CAT", "DOGS"]
    total = scorer.score_words(words)
    
    # A=0, AT=0, CAT=1, DOGS=2, total=3
    assert total == 3
