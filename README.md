# 🎲 Boggle - Multiplayer Word Game

A Python implementation of the classic Boggle word game with single-player and multiplayer modes.

## Features

### Core Gameplay
- **4x4 and 5x5 boards** with randomized dice
- **Word path validation** using depth-first search (DFS)
- **267,000+ word dictionary** (SOWPODS)
- **Fibonacci scoring system** (3-letter word = 1pt, 4-letter = 2pts, 5-letter = 3pts, 6-letter = 5pts, etc.)
- **Board rotation** - view the board from different angles

### Multiplayer Features
- **2-4 players** on the same machine
- **Turn-based gameplay** with pass mechanics
- **Word strike-out logic** - duplicate words across players don't count
- **Detailed results** showing valid words and struck-out words
- **Optional 3-minute timer** for classic Boggle pressure

### Technical Features
- **Type-safe** with mypy type checking
- **Comprehensive test coverage** with pytest
- **Configurable game settings** using Pydantic
- **Clean architecture** with separation of concerns

## Installation

### Prerequisites
- Python 3.12 or higher
- uv (recommended) or pip

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd boggle
```

2. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package:
```bash
uv pip install -e .
```

## How to Play

### Quick Start
```bash
boggle
```

Choose between:
1. **Single Player** - Find words on your own
2. **Multiplayer** - Compete with 2-4 players

### Game Rules

#### Finding Words
- Connect adjacent letters (including diagonals)
- Each letter can only be used once per word
- Minimum word length: 3 letters
- Words must exist in the dictionary

#### Scoring (Fibonacci Sequence)
- 3 letters: 1 point
- 4 letters: 2 points
- 5 letters: 3 points
- 6 letters: 5 points
- 7 letters: 8 points
- 8+ letters: continues the sequence

#### Multiplayer Strike-Out Rule
If multiple players find the same word, **none of them score for it**. This is the classic Boggle rule that rewards finding unique words!

Example:
```
Alice finds: CAT, DOG, FISH
Bob finds:   CAT, BIRD, FISH
Charlie finds: MOUSE

Duplicates: CAT and FISH are struck out

Final scores:
- Alice: DOG only (2 points)
- Bob: BIRD only (2 points)  
- Charlie: MOUSE (3 points)
```

### Commands During Play

- Type a word to submit it
- `pass` - End your turn (multiplayer)
- `score` - View current scores
- `words` - See your submitted words
- `rotate` - Rotate the board view 90° clockwise
- `quit` - End the game (single player)

## Project Structure

```
boggle/
├── src/
│   ├── board.py       # Board generation and word path validation
│   ├── dictionary.py  # Dictionary loading and word validation
│   ├── scorer.py      # Fibonacci-based scoring
│   ├── player.py      # Player state management
│   ├── game.py        # Game orchestration and rules
│   ├── config.py      # Game configuration with Pydantic
│   └── cli.py         # Command-line interface
├── tests/
│   ├── test_board.py
│   ├── test_dictionary.py
│   ├── test_scorer.py
│   ├── test_player.py
│   ├── test_game.py
│   └── test_config.py
├── data/
│   └── sowpods.txt    # Word dictionary
└── pyproject.toml     # Project configuration
```

## Development

### Running Tests
```bash
pytest                  # Run all tests
pytest -v              # Verbose output
pytest tests/test_board.py  # Run specific test file
pytest -k "test_name"  # Run tests matching pattern
```

### Type Checking
```bash
mypy src/
```

### Test Coverage
```bash
pytest --cov=src tests/
```

## Game Configuration

Game settings can be customized through the `GameConfig` class:

```python
from src.config import GameConfig

config = GameConfig(
    board_size=5,              # 4 or 5
    time_limit_seconds=240,    # Time limit in seconds
    min_word_length=4,         # Minimum word length
    max_players=3              # Maximum players (1-8)
)
```

## Architecture

### Design Principles
- **Separation of Concerns**: Each class has a single responsibility
- **Dependency Injection**: Components are passed to Game, not created internally
- **Immutable Configuration**: Game settings can't be changed after creation
- **Type Safety**: Full type hints with mypy validation
- **Test-Driven Development**: Tests written before implementation

### Key Components

**Board**: Generates random boards and validates word paths using DFS
**Dictionary**: Loads 267k words into a set for O(1) lookup
**Scorer**: Calculates Fibonacci-based scores
**Player**: Tracks individual player state in multiplayer
**Game**: Orchestrates all components and enforces game rules
**Config**: Validates and stores game settings using Pydantic

## Algorithm Highlights

### Word Path Validation (DFS with Backtracking)
```python
def has_word_path(word: str) -> bool:
    # Try starting from each cell
    for row in range(size):
        for col in range(size):
            if dfs(word, 0, row, col, visited=set()):
                return True
    return False
```

Time Complexity: O(n² × 8^m) where n = board size, m = word length

### Strike-Out Detection
```python
def get_duplicate_words() -> set[str]:
    word_counts = {}
    for player in players:
        for word in player.words:
            word_counts[word] = word_counts.get(word, 0) + 1
    return {word for word, count in word_counts.items() if count > 1}
```

Time Complexity: O(p × w) where p = players, w = words per player

## Learning Objectives

This project demonstrates:
- Python 3.12 features (type unions with `|`, pattern matching)
- Modern tooling (uv, mypy, pytest, Pydantic)
- Test-Driven Development (TDD)
- Graph algorithms (DFS, backtracking)
- Game state management
- CLI design patterns
- Git workflow with feature branches

## Future Enhancements (Week 3+)

Planned features:
- [ ] Network multiplayer (WebSocket-based)
- [ ] Persistent leaderboards
- [ ] Custom board generation
- [ ] Hint system
- [ ] Replay functionality
- [ ] Web interface

## Credits

- Dictionary: [SOWPODS word list](https://en.wikipedia.org/wiki/Collins_Scrabble_Words)
- Game concept: Classic Boggle by Parker Brothers
- Implementation: Learning project by Amritansh

## License

This is a personal learning project.

---

Made with ❤️ and Python
