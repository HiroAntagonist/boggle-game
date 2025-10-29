# ABOUTME: Command-line interface for Boggle game
# ABOUTME: Provides interactive single-player game experience

from src.board import Board
from src.dictionary import Dictionary
from src.scorer import Scorer
from src.game import Game


def display_board(board: Board, rotation: int = 0) -> None:
    """Display the board in a nice format with optional rotation.
    
    Args:
        board: The game board to display
        rotation: Number of 90° clockwise rotations (0, 1, 2, or 3)
    """
    # Get the grid to display based on rotation
    n = board.size
    original_grid = board.grid
    
    # Apply rotation transformation to display coordinates
    if rotation == 0:
        display_grid = original_grid
    elif rotation == 1:  # 90° clockwise
        display_grid = [[original_grid[n-1-c][r] for c in range(n)] for r in range(n)]
    elif rotation == 2:  # 180°
        display_grid = [[original_grid[n-1-r][n-1-c] for c in range(n)] for r in range(n)]
    elif rotation == 3:  # 270° clockwise (90° counter-clockwise)
        display_grid = [[original_grid[c][n-1-r] for c in range(n)] for r in range(n)]
    else:
        display_grid = original_grid
    
    # Display the board
    print("\n" + "=" * 20)
    if rotation > 0:
        print(f"  BOGGLE BOARD (↻{rotation * 90}°)")
    else:
        print("    BOGGLE BOARD")
    print("=" * 20)
    
    for row in display_grid:
        print("  " + "  ".join(row))
    
    print("=" * 20 + "\n")


def display_instructions() -> None:
    """Display game instructions."""
    print("\n🎲 WELCOME TO BOGGLE! 🎲\n")
    print("Instructions:")
    print("- Find words by connecting adjacent letters (including diagonals)")
    print("- Each letter can only be used once per word")
    print("- Minimum word length: 3 letters")
    print("- Type 'quit' to end the game")
    print("- Type 'score' to see your current score")
    print("- Type 'words' to see your submitted words")
    print("- Type 'rotate' to rotate the board view 90° clockwise")
    print()


def display_results(game: Game) -> None:
    """Display final game results.
    
    Args:
        game: The completed game
    """
    words = game.get_submitted_words()
    score = game.get_score()
    
    print("\n" + "=" * 40)
    print("           GAME OVER!")
    print("=" * 40)
    print(f"\nWords found: {len(words)}")
    print(f"Final score: {score} points\n")
    
    if words:
        print("Your words:")
        for word in sorted(words):
            word_score = game.scorer.score_word(word)
            print(f"  {word:12} ({len(word)} letters) - {word_score} points")
    else:
        print("No words found. Better luck next time!")
    
    print("\n" + "=" * 40 + "\n")


def display_multiplayer_results(game: Game) -> None:
    """Display final results for multiplayer game.
    
    Args:
        game: The completed game
    """
    players = game.get_players()
    duplicates = game.get_duplicate_words()
    
    print("\n" + "=" * 60)
    print("                    GAME OVER!")
    print("=" * 60)
    
    # Sort players by score (highest first)
    players_by_score = sorted(
        players,
        key=lambda p: game.get_player_score(p),
        reverse=True
    )
    
    print("\n" + "=" * 60)
    print("FINAL SCORES:")
    print("=" * 60)
    
    for rank, player in enumerate(players_by_score, 1):
        score = game.get_player_score(player)
        valid_words = game.get_player_valid_words(player)
        total_words = len(player.get_words())
        struck_out = total_words - len(valid_words)
        
        print(f"\n{rank}. {player.name}: {score} points")
        print(f"   Words found: {total_words} ({struck_out} struck out)")
    
    # Show each player's words
    print("\n" + "=" * 60)
    print("WORD BREAKDOWN:")
    print("=" * 60)
    
    for player in players_by_score:
        print(f"\n{player.name}'s words:")
        valid_words = game.get_player_valid_words(player)
        
        if valid_words:
            for word in sorted(valid_words):
                word_score = game.scorer.score_word(word)
                print(f"  ✓ {word:12} ({len(word)} letters) - {word_score} points")
        
        # Show struck-out words
        struck_words = [w for w in player.get_words() if w in duplicates]
        if struck_words:
            print(f"\n  Struck out (duplicates):")
            for word in sorted(struck_words):
                print(f"  ✗ {word:12} (0 points)")
        
        if not valid_words and not struck_words:
            print("  No words found")
    
    print("\n" + "=" * 60 + "\n")


def play_game() -> None:
    """Run a single-player Boggle game."""
    # Initialize game components
    print("Loading dictionary...")
    dictionary = Dictionary("data/sowpods.txt")
    
    print("Generating board...")
    board = Board(size=4)
    
    scorer = Scorer(min_word_length=3)
    game = Game(board=board, dictionary=dictionary, scorer=scorer)
    
    # Display instructions and board
    display_instructions()
    display_board(board, game.get_rotation())
    
    # Game loop
    while True:
        word = input("Enter a word (or 'quit'/'score'/'words'/'rotate'): ").strip()
        
        if not word:
            continue
        
        # Handle commands
        if word.lower() == "quit":
            break
        
        if word.lower() == "score":
            print(f"\nCurrent score: {game.get_score()} points")
            print(f"Words found: {len(game.get_submitted_words())}\n")
            continue
        
        if word.lower() == "words":
            words = game.get_submitted_words()
            if words:
                print(f"\nYour words ({len(words)}):")
                for w in sorted(words):
                    print(f"  {w}")
                print()
            else:
                print("\nNo words submitted yet.\n")
            continue
        
        if word.lower() == "rotate":
            game.rotate_view_clockwise()
            display_board(board, game.get_rotation())
            print("Board rotated 90° clockwise. Words validate against original orientation.\n")
            continue
        
        # Try to submit the word
        if game.submit_word(word):
            word_score = game.scorer.score_word(word)
            print(f"✓ {word.upper()} accepted! +{word_score} points (Total: {game.get_score()})\n")
        else:
            # Give helpful feedback on why it was rejected
            word_upper = word.upper()
            
            if word_upper in game.get_submitted_words():
                print(f"✗ {word_upper} already submitted!\n")
            elif len(word) < scorer.min_word_length:
                print(f"✗ {word_upper} is too short (minimum {scorer.min_word_length} letters)\n")
            elif not dictionary.is_valid_word(word):
                print(f"✗ {word_upper} is not in the dictionary\n")
            elif not board.has_word_path(word):
                print(f"✗ {word_upper} cannot be formed on the board\n")
            else:
                print(f"✗ {word_upper} was rejected\n")
    
    # Display final results
    display_results(game)


def play_multiplayer_game() -> None:
    """Run a multiplayer Boggle game."""
    from src.player import Player
    from src.config import GameConfig
    
    print("\n🎲 MULTIPLAYER BOGGLE! 🎲\n")
    
    # Get number of players
    while True:
        try:
            num_players = int(input("How many players? (2-4): ").strip())
            if 2 <= num_players <= 4:
                break
            print("Please enter a number between 2 and 4.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get player names
    players = []
    for i in range(num_players):
        name = input(f"Player {i+1} name: ").strip()
        if not name:
            name = f"Player {i+1}"
        players.append(Player(player_id=f"p{i+1}", name=name))
    
    # Initialize game components
    print("\nLoading dictionary...")
    dictionary = Dictionary("data/sowpods.txt")
    
    print("Generating board...")
    board = Board(size=4)
    
    scorer = Scorer(min_word_length=3)
    config = GameConfig(max_players=num_players)
    game = Game(board=board, dictionary=dictionary, scorer=scorer, config=config)
    
    # Add players to game
    for player in players:
        game.add_player(player)
    
    # Display instructions
    print("\nInstructions:")
    print("- Players take turns submitting words")
    print("- Type a word to submit it")
    print("- Type 'pass' to end your turn")
    print("- Type 'score' to see current scores")
    print("- Type 'words' to see your words")
    print("- Type 'rotate' to rotate the board view")
    print("- Game ends when all players pass consecutively")
    print()
    
    display_board(board, game.get_rotation())
    
    # Game loop
    current_player_idx = 0
    consecutive_passes = 0
    
    while consecutive_passes < len(players):
        current_player = players[current_player_idx]
        
        print(f"\n{'='*40}")
        print(f"{current_player.name}'s turn")
        print(f"{'='*40}")
        
        word = input("Enter word (or 'pass'/'score'/'words'/'rotate'): ").strip()
        
        if not word:
            continue
        
        # Handle commands
        if word.lower() == "pass":
            print(f"{current_player.name} passes.\n")
            consecutive_passes += 1
            current_player_idx = (current_player_idx + 1) % len(players)
            continue
        
        if word.lower() == "score":
            print("\nCurrent scores:")
            for p in players:
                score = game.get_player_score(p)
                word_count = len(p.get_words())
                print(f"  {p.name}: {score} points ({word_count} words)")
            print()
            continue
        
        if word.lower() == "words":
            print(f"\n{current_player.name}'s words:")
            words = current_player.get_words()
            if words:
                for w in sorted(words):
                    print(f"  {w}")
            else:
                print("  None yet")
            print()
            continue
        
        if word.lower() == "rotate":
            game.rotate_view_clockwise()
            display_board(board, game.get_rotation())
            print("Board rotated 90° clockwise.\n")
            continue
        
        # Try to submit the word
        if game.submit_word(word, current_player):
            word_score = game.scorer.score_word(word)
            print(f"✓ {word.upper()} accepted! +{word_score} points\n")
            consecutive_passes = 0  # Reset pass counter
        else:
            # Give helpful feedback
            word_upper = word.upper()
            
            if word_upper in current_player.get_words():
                print(f"✗ You already submitted {word_upper}!\n")
            elif len(word) < scorer.min_word_length:
                print(f"✗ {word_upper} is too short (minimum {scorer.min_word_length} letters)\n")
            elif not dictionary.is_valid_word(word):
                print(f"✗ {word_upper} is not in the dictionary\n")
            elif not board.has_word_path(word):
                print(f"✗ {word_upper} cannot be formed on the board\n")
            else:
                print(f"✗ {word_upper} was rejected\n")
    
    # Display final results
    display_multiplayer_results(game)


def main() -> None:
    """Main entry point for CLI."""
    print("\n🎲 WELCOME TO BOGGLE! 🎲\n")
    print("Choose game mode:")
    print("1. Single Player")
    print("2. Multiplayer (2-4 players)")
    
    while True:
        choice = input("\nEnter 1 or 2: ").strip()
        if choice == "1":
            play_game()
            break
        elif choice == "2":
            play_multiplayer_game()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
