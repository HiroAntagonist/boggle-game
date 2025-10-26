# ABOUTME: Tests for the Dictionary class
# ABOUTME: Validates words against a word list file

from src.dictionary import Dictionary


def test_dictionary_loads_from_file() -> None:
    """Dictionary should load words from a file."""
    dictionary = Dictionary("data/sowpods.txt")
    
    # SOWPODS has ~267,000 words
    assert len(dictionary) > 260000


def test_valid_word_returns_true() -> None:
    """Dictionary should return True for valid words."""
    dictionary = Dictionary("data/sowpods.txt")
    
    assert dictionary.is_valid_word("CAT") is True
    assert dictionary.is_valid_word("PYTHON") is True
    assert dictionary.is_valid_word("BOGGLE") is True


def test_invalid_word_returns_false() -> None:
    """Dictionary should return False for invalid words."""
    dictionary = Dictionary("data/sowpods.txt")
    
    assert dictionary.is_valid_word("ASDFQWER") is False
    assert dictionary.is_valid_word("ZZZZZ") is False
    assert dictionary.is_valid_word("XQZ") is False


def test_case_insensitive_validation() -> None:
    """Dictionary should handle case-insensitive lookups."""
    dictionary = Dictionary("data/sowpods.txt")
    
    assert dictionary.is_valid_word("cat") is True
    assert dictionary.is_valid_word("CAT") is True
    assert dictionary.is_valid_word("CaT") is True


def test_empty_string_is_invalid() -> None:
    """Empty string should be invalid."""
    dictionary = Dictionary("data/sowpods.txt")
    
    assert dictionary.is_valid_word("") is False


def test_whitespace_is_invalid() -> None:
    """Whitespace should be invalid."""
    dictionary = Dictionary("data/sowpods.txt")
    
    assert dictionary.is_valid_word("   ") is False
    assert dictionary.is_valid_word("\n") is False
