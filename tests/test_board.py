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