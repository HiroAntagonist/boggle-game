# ABOUTME: Tests for the Board class
# ABOUTME: Following TDD - write tests first, then implementation

from src.board import Board


def test_board_generates_4x4_grid() -> None:
    """Board should generate a 4x4 grid when size is 4."""
    board = Board(size=4)
    
    assert board.size == 4
    assert len(board.grid) == 4
    assert all(len(row) == 4 for row in board.grid)


def test_board_generates_5x5_grid() -> None:
    """Board should generate a 5x5 grid when size is 5."""
    board = Board(size=5)
    
    assert board.size == 5
    assert len(board.grid) == 5
    assert all(len(row) == 5 for row in board.grid)


def test_board_grid_contains_letters() -> None:
    """Each cell in the grid should contain a letter."""
    board = Board(size=4)
    
    for row in board.grid:
        for cell in row:
            assert isinstance(cell, str)
            assert len(cell) == 1
            assert cell.isalpha()


def test_word_exists_on_simple_path() -> None:
    """Should find a word that exists on a simple adjacent path."""
    # Create a board with known letters for testing
    board = Board(size=4)
    board.grid = [
        ["C", "A", "T", "S"],
        ["O", "R", "E", "D"],
        ["D", "E", "S", "K"],
        ["M", "O", "P", "S"]
    ]
    
    # CAT exists: C(0,0) → A(0,1) → T(0,2)
    assert board.has_word_path("CAT") is True


def test_word_exists_with_diagonal() -> None:
    """Should find a word using diagonal adjacency."""
    board = Board(size=4)
    board.grid = [
        ["C", "X", "X", "X"],
        ["X", "A", "X", "X"],
        ["X", "X", "T", "X"],
        ["X", "X", "X", "X"]
    ]
    
    # CAT exists diagonally: C(0,0) → A(1,1) → T(2,2)
    assert board.has_word_path("CAT") is True


def test_word_not_on_board() -> None:
    """Should return False for word not on board."""
    board = Board(size=4)
    board.grid = [
        ["C", "A", "T", "S"],
        ["O", "R", "E", "D"],
        ["D", "E", "S", "K"],
        ["M", "O", "P", "S"]
    ]
    
    # ZEBRA - Z doesn't exist on board
    assert board.has_word_path("ZEBRA") is False


def test_word_cannot_reuse_cell() -> None:
    """Should return False if word requires reusing a cell."""
    board = Board(size=4)
    board.grid = [
        ["A", "B", "C", "D"],
        ["E", "F", "G", "H"],
        ["I", "J", "K", "L"],
        ["M", "N", "O", "P"]
    ]
    
    # ABA would require using A twice - not allowed
    assert board.has_word_path("ABA") is False


def test_word_with_non_adjacent_letters() -> None:
    """Should return False if letters exist but aren't adjacent."""
    board = Board(size=4)
    board.grid = [
        ["C", "X", "T", "X"],
        ["X", "X", "X", "X"],
        ["X", "X", "X", "X"],
        ["X", "X", "X", "X"]
    ]
    
    # C and T exist but aren't adjacent
    assert board.has_word_path("CT") is False


def test_word_with_duplicate_start_letters() -> None:
    """Should return True if there is a different starting letter that makes the word"""
    board = Board(size=4)
    board.grid = [
        ["C", "X", "T", "E"],
        ["O", "X", "X", "D"],
        ["D", "X", "X", "O"],
        ["X", "X", "X", "C"]
    ]
    
    # Bottom Right C makes the word, but Top Left doesn't
    assert board.has_word_path("CODE") is True


def test_empty_word() -> None:
    """Should handle empty string."""
    board = Board(size=4)
    board.grid = [
        ["C", "A", "T", "S"],
        ["O", "R", "E", "D"],
        ["D", "E", "S", "K"],
        ["M", "O", "P", "S"]
    ]
    
    assert board.has_word_path("") is False
