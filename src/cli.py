# ABOUTME: Command-line interface for Boggle game
# ABOUTME: Provides interactive single-player game experience

from src.board import Board
from src.dictionary import Dictionary
from src.scorer import Scorer
from src.game import Game


def display_board(board: Board) -> None:
    """Display the board in a nice format.
    
    Args:
        board: The game board to display
    """
    print("\n" + "=" * 20)
    print("    BOGGLE BOARD")
    print("=" * 20)
    
    for row in board.grid:
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
    display_board(board)
    
    # Game loop
    while True:
        word = input("Enter a word (or 'quit'/'score'/'words'): ").strip()
        
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


def main() -> None:
    """Main entry point for CLI."""
    play_game()


if __name__ == "__main__":
    main()
