# ABOUTME: Tests for the Game class
# ABOUTME: Orchestrates Board, Dictionary, and Scorer for a complete game

from src.game import Game
from src.board import Board
from src.dictionary import Dictionary
from src.scorer import Scorer
from src.config import GameConfig
from src.player import Player


def test_game_initializes_with_components() -> None:
    """Game should initialize with board, dictionary, and scorer."""
    board = Board(size=4)
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    assert game.board is board
    assert game.dictionary is dictionary
    assert game.scorer is scorer


def test_game_starts_with_no_submitted_words() -> None:
    """Game should start with empty submitted words list."""
    board = Board(size=4)
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    assert game.get_submitted_words() == []
    assert game.get_score() == 0


def test_submit_valid_word() -> None:
    """Should accept a word that is on board and in dictionary."""
    board = Board(size=4)
    board.grid = [
        ["C", "A", "T", "S"],
        ["O", "R", "E", "D"],
        ["D", "E", "S", "K"],
        ["M", "O", "P", "S"]
    ]
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    result = game.submit_word("CAT")
    
    assert result is True
    assert "CAT" in game.get_submitted_words()
    assert game.get_score() == 1  # 3-letter word scores 1


def test_submit_word_not_in_dictionary() -> None:
    """Should reject a word that is on board but not in dictionary."""
    board = Board(size=4)
    board.grid = [
        ["X", "Y", "Z", "Q"],
        ["A", "B", "C", "D"],
        ["E", "F", "G", "H"],
        ["I", "J", "K", "L"]
    ]
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    # XYZ is on the board but not a word
    result = game.submit_word("XYZ")
    
    assert result is False
    assert "XYZ" not in game.get_submitted_words()
    assert game.get_score() == 0


def test_submit_word_not_on_board() -> None:
    """Should reject a word that is in dictionary but not on board."""
    board = Board(size=4)
    board.grid = [
        ["X", "X", "X", "X"],
        ["X", "X", "X", "X"],
        ["X", "X", "X", "X"],
        ["X", "X", "X", "X"]
    ]
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    # CAT is in dictionary but not on board (all X's)
    result = game.submit_word("CAT")
    
    assert result is False
    assert "CAT" not in game.get_submitted_words()
    assert game.get_score() == 0


def test_submit_duplicate_word() -> None:
    """Should reject duplicate word submissions."""
    board = Board(size=4)
    board.grid = [
        ["C", "A", "T", "S"],
        ["O", "R", "E", "D"],
        ["D", "E", "S", "K"],
        ["M", "O", "P", "S"]
    ]
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    # Submit CAT first time - should succeed
    assert game.submit_word("CAT") is True
    assert game.get_score() == 1
    
    # Submit CAT second time - should fail
    assert game.submit_word("CAT") is False
    assert game.get_score() == 1  # Score doesn't change


def test_submit_multiple_valid_words() -> None:
    """Should track multiple valid word submissions."""
    board = Board(size=4)
    board.grid = [
        ["C", "A", "T", "S"],
        ["O", "R", "E", "D"],
        ["D", "E", "S", "K"],
        ["M", "O", "P", "S"]
    ]
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    game.submit_word("CAT")    # 1 point
    game.submit_word("CATS")   # 2 points
    game.submit_word("CORE")   # 2 points
    
    assert len(game.get_submitted_words()) == 3
    assert game.get_score() == 5  # 1 + 2 + 2


def test_word_too_short() -> None:
    """Should reject words below minimum length."""
    board = Board(size=4)
    board.grid = [
        ["C", "A", "T", "S"],
        ["O", "R", "E", "D"],
        ["D", "E", "S", "K"],
        ["M", "O", "P", "S"]
    ]
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    # AT is only 2 letters (min is 3)
    result = game.submit_word("AT")
    
    assert result is False
    assert "AT" not in game.get_submitted_words()
    assert game.get_score() == 0


def test_game_starts_with_no_rotation() -> None:
    """Game should start with rotation = 0."""
    board = Board(size=4)
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    assert game.get_rotation() == 0


def test_rotate_view_clockwise() -> None:
    """Should increment rotation counter (mod 4)."""
    board = Board(size=4)
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    assert game.get_rotation() == 0
    
    game.rotate_view_clockwise()
    assert game.get_rotation() == 1
    
    game.rotate_view_clockwise()
    assert game.get_rotation() == 2
    
    game.rotate_view_clockwise()
    assert game.get_rotation() == 3
    
    game.rotate_view_clockwise()
    assert game.get_rotation() == 0  # Wraps back to 0


def test_rotation_does_not_affect_word_validation() -> None:
    """Word validation should use original grid regardless of rotation."""
    board = Board(size=4)
    board.grid = [
        ["C", "A", "T", "S"],
        ["O", "R", "E", "D"],
        ["D", "E", "S", "K"],
        ["M", "O", "P", "S"]
    ]
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    # CAT exists on original board
    assert game.submit_word("CAT") is True
    
    # Rotate view
    game.rotate_view_clockwise()
    
    # CATS should still be validated against original grid
    # (not the rotated view)
    assert game.submit_word("CATS") is True
    
    # Both words should be in submitted list
    assert len(game.get_submitted_words()) == 2


def test_game_accepts_config() -> None:
    """Game should accept and store GameConfig."""
    board = Board(size=5)
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=4)
    config = GameConfig(
        board_size=5,
        time_limit_seconds=240,
        min_word_length=4,
        max_players=2
    )
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer, config=config)
    
    assert game.config is config
    assert game.config.board_size == 5
    assert game.config.time_limit_seconds == 240
    assert game.config.min_word_length == 4
    assert game.config.max_players == 2


def test_game_uses_default_config_if_not_provided() -> None:
    """Game should use default GameConfig if none provided."""
    board = Board(size=4)
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    assert game.config.board_size == 4
    assert game.config.time_limit_seconds == 180
    assert game.config.min_word_length == 3
    assert game.config.max_players == 4


def test_game_add_player() -> None:
    """Game should allow adding players."""
    board = Board(size=4)
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    player1 = Player(player_id="p1", name="Alice")
    player2 = Player(player_id="p2", name="Bob")
    
    game.add_player(player1)
    game.add_player(player2)
    
    assert len(game.get_players()) == 2
    assert player1 in game.get_players()
    assert player2 in game.get_players()


def test_game_cannot_exceed_max_players() -> None:
    """Game should not allow more than max_players."""
    board = Board(size=4)
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    config = GameConfig(max_players=2)
    game = Game(board=board, dictionary=dictionary, scorer=scorer, config=config)
    
    player1 = Player(player_id="p1", name="Alice")
    player2 = Player(player_id="p2", name="Bob")
    player3 = Player(player_id="p3", name="Charlie")
    
    assert game.add_player(player1) is True
    assert game.add_player(player2) is True
    assert game.add_player(player3) is False  # Exceeds max
    
    assert len(game.get_players()) == 2


def test_game_cannot_add_duplicate_player() -> None:
    """Game should not allow adding the same player twice."""
    board = Board(size=4)
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    player1 = Player(player_id="p1", name="Alice")
    player2 = Player(player_id="p1", name="Bob")  # Same ID, different name
    
    assert game.add_player(player1) is True
    assert game.add_player(player2) is False  # Duplicate ID
    
    assert len(game.get_players()) == 1
    assert game.get_players()[0].name == "Alice"  # First one was kept


def test_multiplayer_word_submission() -> None:
    """Each player should have their own word list."""
    board = Board(size=4)
    board.grid = [
        ["C", "A", "T", "S"],
        ["O", "R", "E", "D"],
        ["D", "E", "S", "K"],
        ["M", "O", "P", "S"]
    ]
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    player1 = Player(player_id="p1", name="Alice")
    player2 = Player(player_id="p2", name="Bob")
    game.add_player(player1)
    game.add_player(player2)
    
    # Player 1 submits CAT
    assert game.submit_word("CAT", player1) is True
    assert "CAT" in player1.get_words()
    assert "CAT" not in player2.get_words()
    
    # Player 2 submits CATS
    assert game.submit_word("CATS", player2) is True
    assert "CATS" in player2.get_words()
    assert "CATS" not in player1.get_words()
    
    # Both players can submit the same word
    assert game.submit_word("CORE", player1) is True
    assert game.submit_word("CORE", player2) is True


def test_player_cannot_submit_same_word_twice() -> None:
    """A player cannot submit the same word twice."""
    board = Board(size=4)
    board.grid = [
        ["C", "A", "T", "S"],
        ["O", "R", "E", "D"],
        ["D", "E", "S", "K"],
        ["M", "O", "P", "S"]
    ]
    dictionary = Dictionary("data/sowpods.txt")
    scorer = Scorer(min_word_length=3)
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    player1 = Player(player_id="p1", name="Alice")
    game.add_player(player1)
    
    assert game.submit_word("CAT", player1) is True
    assert game.submit_word("CAT", player1) is False  # Duplicate
