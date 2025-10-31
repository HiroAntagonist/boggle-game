# Claude & Amritansh Learning Journal

## 2025-01-15: Week 1, Day 1 - Project Setup

### What we did
- Set up development environment from scratch
- Authenticated GitHub CLI and created private repo
- Configured Python with uv (modern package manager)
- Installed pytest, pytest-watch, and mypy for testing and type checking
- Set up mypy.ini for type safety (Python 3.12)
- Configured VSCode with Pylance, testing, and Python extensions
- Made 3 commits and pushed to GitHub
- Learned about git email privacy and fixed it

### What I learned
- `gh repo create` can create and connect a repo in one command
- uv is much faster than pip for package management
- Git can diverge when remote and local have different histories
- `git pull --rebase` replays local commits on top of remote
- `git commit --amend --reset-author` can fix commit metadata
- GitHub protects private email addresses automatically
- VSCode can auto-discover pytest tests

### Challenges/Issues
- Hit a git divergence issue when pushing (fixed with rebase)
- GitHub rejected push due to email privacy (fixed with no-reply email)

### Key Commands Learned
```bash
gh auth login                    # Authenticate GitHub CLI
gh repo create --private         # Create private repo and connect it
uv init                         # Initialize Python project
uv venv                         # Create virtual environment  
uv add --dev pytest mypy        # Add development dependencies
git pull --rebase origin main   # Rebase local commits on remote
git commit --amend --reset-author  # Fix commit author
```

### Blockers/Questions
- None - Day 1 complete!

### Next session
- Day 2: First TDD cycle - Board generation
- Write failing test for Board class
- Implement minimal code to pass
- Learn pytest basics and Python type hints

### Time spent
~45 minutes

### Reflection
Setting up the environment took some troubleshooting (git divergence, email privacy), but these were great learning moments. The tools (uv, gh CLI, VSCode) are much more modern than what I used in the early 2000s. Excited to start writing actual code tomorrow!

---

## 2025-01-XX: Week 1, Day 2 - First TDD Cycle

### What we did
- Created project structure (`src/`, `tests/` directories)
- Wrote first failing tests for Board class (RED phase)
- Implemented Board class with type hints (GREEN phase)
- All tests passing with pytest
- Type checking passing with mypy
- Used feature branch workflow
- Merged to main and pushed to GitHub

### What I learned
- TDD red-green-refactor cycle in practice
- Python has no `char` type - everything is `str`
- Type hints: `List[List[str]]` for 2D grid
- pytest discovers and runs tests automatically
- Feature branch workflow: create branch, commit, merge, delete
- Python `random` module for shuffling dice
- Private methods convention: `_generate_grid()`

### Challenges/Issues
- None! Everything worked smoothly

### Key Commands Learned
```bash
git checkout -b feature/branch-name  # Create and switch to new branch
pytest tests/test_board.py -v        # Run specific test file with verbose output
mypy src/                            # Type check source code
git merge feature/branch-name        # Merge feature branch into current branch
git branch -d branch-name            # Delete local branch
```

### Code Concepts
- Type hints for function signatures: `def __init__(self, size: int) -> None:`
- List comprehensions: `[random.choice(die) for die in dice]`
- Raising exceptions: `raise ValueError(f"...")`
- 2D list slicing: `letters[i * 4:(i + 1) * 4]`

### Blockers/Questions
- Understood the difference between C's `char` vs Python's `str`

### Next session
- Day 3: Word Path Validation
- Implement depth-first search (DFS) for finding words on board
- Test adjacency logic (including diagonals)
- Learn about more complex type hints (Tuple, Set)

### Time spent
~45 minutes

### Reflection
First real code! TDD feels different from how I used to code - writing the test first seemed backwards at first, but I can see how it forces you to think about the interface before implementation. The test failure → implementation → test pass cycle is satisfying. Python's type hints are lighter than C's strict typing, but mypy catches issues. The `List[List[str]]` type hint clearly documents the 2D grid structure.

---

## 2025-01-XX: Week 1, Day 3 - Word Path Validation with DFS

### What we did
- Implemented depth-first search (DFS) algorithm for word path validation
- Wrote comprehensive tests including edge cases
- Validated 8-directional adjacency (including diagonals)
- Implemented backtracking to allow cells to be reused by different paths
- Successfully used feature branch workflow (created, committed, merged, cleaned up)
- All tests passing, type checking passing

### What I learned
- **DFS Algorithm**: Recursive search with backtracking
- **Backtracking**: Why we need `visited.remove()` - allows other search paths to use the same cell
- **Complex type hints**: `Set[Tuple[int, int]]` for coordinate tracking
- **Recursion**: Base cases, recursive cases, and when to backtrack
- **Test-driven algorithm development**: Writing tests first helped clarify the requirements
- **Edge cases**: Empty strings, duplicate starting letters, non-adjacent letters, cell reuse
- **Feature branch workflow**: This time we did it correctly!

### Challenges/Issues
- None! The feature branch workflow finally clicked
- DFS algorithm made sense because of C background with recursion

### Key Commands Learned
```bash
git branch                       # Check current branch (do this often!)
git log --oneline -5            # See recent commits
pytest tests/test_board.py::test_name  # Run specific test
```

### Code Concepts
- **Depth-First Search (DFS)**: Explores as far as possible along each branch before backtracking
- **Backtracking**: Undoing choices to explore other possibilities
- **Set operations**: Using `set.add()` and `set.remove()` for visited tracking
- **Tuple as dictionary key**: `(row, col)` tuple can be added to sets
- **Multiple return paths**: Early returns for base cases and validation
- **8-directional adjacency**: List of (dr, dc) tuples for all 8 directions

### Algorithm Walkthrough (for future reference)
```python
has_word_path("CAT"):
  1. Find all 'C' cells on board
  2. For each 'C', start DFS:
     - Mark (row, col) as visited
     - Check all 8 adjacent cells for 'A'
     - For each 'A', recursively search for 'T'
     - If found 'T' adjacent to 'A': return True
     - If not found: backtrack (remove from visited)
  3. Try next 'C' cell
  4. If no path found: return False
```

### Good Test Case I Added
Created test for duplicate starting letters - when one starting position fails but another succeeds. This tests that the algorithm properly tries all possible starting points.

### Blockers/Questions
- None - DFS made sense from C/algorithm background

### Next session
- Day 4: Dictionary Validation
- Load word list file
- Implement efficient word lookup
- Test case-insensitive validation

### Time spent
~90 minutes

### Reflection
The DFS algorithm was the most algorithmically interesting part so far. Writing the tests first really helped clarify what "adjacent" means and all the edge cases (reusing cells, non-adjacent letters, etc.). The backtracking concept clicked when I realized why we need to remove from visited - other paths need to be able to use that cell. The feature branch workflow finally worked correctly this time by checking `git branch` before every commit. Python's `Set[Tuple[int, int]]` type hint clearly documents what visited contains.

---

## 2025-01-XX: Week 1, Day 4 - Dictionary Validation

### What we did
- Downloaded SOWPODS dictionary (~267k words)
- Implemented Dictionary class with efficient set-based lookup
- Loaded words from file into memory
- Case-insensitive word validation
- All tests passing, type checking passing
- Git workflow continues to improve - checking branch before every commit

### What I learned
- **Set vs List performance**: Set gives O(1) lookup vs List's O(n)
- **Context managers**: `with open()` automatically closes files
- **Magic methods**: `__len__()` allows `len(dictionary)`
- **File I/O in Python**: Much simpler than C's fopen/fclose
- **Git habit**: Always check `git branch` and `git status` before committing
- **Data directory convention**: Keep data files separate from code

### Challenges/Issues
- None - straightforward implementation

### Key Commands Learned
```bash
curl <url> -o <filename>         # Download file from URL
wc -l <file>                     # Count lines in file
mkdir -p <dir>                   # Create directory (and parents if needed)
git branch                       # Check current branch (do this constantly!)
git log --oneline -5             # See recent commits with short hashes
```

### Code Concepts
- **Set for O(1) lookup**: Using `Set[str]` instead of `List[str]` for instant word validation
- **File I/O with context manager**: `with open(filepath) as f:` - no need to manually close
- **String methods**: `.strip()` removes whitespace, `.upper()` for normalization
- **Magic methods**: `__len__()` lets class work with `len()` builtin
- **Type hints**: `Set[str]` is more specific than just `set`

### Performance Note
Loading 267k words into a set takes ~0.1 seconds, but lookups are instant (O(1)). In C, this would be a hash table. Python's set is implemented as a hash table under the hood.

### Blockers/Questions
- None

### Next session
- Day 5: Fibonacci Scoring System
- Implement scoring based on word length
- Configurable minimum word length
- Test edge cases

### Time spent
~45 minutes

### Reflection
Dictionary validation was much simpler than DFS - just loading a file and using the right data structure. The key insight is using a set for O(1) lookup instead of a list. Python's context managers (`with open()`) are much nicer than C's manual file handling. Git workflow is becoming more natural - I'm checking `git branch` before every commit now and it's preventing mistakes. The three-stage workflow (working directory → staging → repository) is starting to click.

---

## 2025-01-XX: Week 1, Day 5 - Fibonacci Scoring System

### What we did
- Implemented Fibonacci-based scoring for word lengths
- Configurable minimum word length
- Score individual words and lists of words
- Pre-cached Fibonacci numbers for efficiency
- All tests passing, type checking passing
- Git workflow flowing smoothly

### What I learned
- **Fibonacci sequence**: 1, 2, 3, 5, 8, 13, 21... (each is sum of previous two)
- **Caching for performance**: Pre-generate Fibonacci numbers instead of recalculating
- **Index arithmetic**: Mapping word length to Fibonacci index
- **List comprehension with sum**: `sum(expr for item in list)` - clean Python idiom
- **Generator expressions**: The expression inside `sum()` is actually a generator

### Challenges/Issues
- None - straightforward implementation

### Key Commands Learned
```bash
# (Still practicing the git workflow habits)
git branch                       # Check current branch
git log --oneline -3             # See recent commits
git status                       # Check for uncommitted changes
```

### Code Concepts
- **Pre-computation/Caching**: Generate Fibonacci sequence once, reuse many times
- **Index calculation**: `fib_index = word_length - min_word_length`
- **Generator expression**: `sum(self.score_word(word) for word in words)`
- **Private methods**: `_generate_fibonacci()` is internal implementation detail
- **List comprehension inside sum**: Pythonic way to sum computed values

### Algorithm: Fibonacci Generation
```python
def _generate_fibonacci(n):
    if n == 0: return []
    if n == 1: return [1]
    
    fib = [1, 2]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])  # Each = sum of previous two
    
    return fib
```

### Scoring Examples
```
min_length = 3:
- 3 letters: index 0 → Fib[0] = 1
- 4 letters: index 1 → Fib[1] = 2
- 5 letters: index 2 → Fib[2] = 3
- 6 letters: index 3 → Fib[3] = 5
- 7 letters: index 4 → Fib[4] = 8
```

### Blockers/Questions
- None

### Next session
- Day 6 (Weekend - 90 min): CLI Interface & Integration
- Bring everything together: Board, Dictionary, Scorer
- Build interactive CLI game
- Full single-player game working end-to-end

### Time spent
~45 minutes

### Reflection
Scoring was simpler than expected. The key insight was pre-caching Fibonacci numbers - generate once, use many times. The index arithmetic (`word_length - min_word_length`) elegantly maps word lengths to the Fibonacci sequence. Python's `sum()` with a generator expression is much cleaner than a manual loop. Git workflow is now second nature - I'm automatically checking `git branch` and `git status` before every commit. Ready to integrate everything into a playable game!

---

## 2025-01-XX: Week 1, Day 6 - CLI Interface & Full Game Integration

### What we did
- Created Game class to orchestrate Board, Dictionary, and Scorer
- Implemented full validation pipeline (length, dictionary, board path, duplicates)
- Built interactive CLI with board display and game loop
- Added helpful feedback for rejected words
- Configured package with `boggle` command entry point via pyproject.toml
- Played actual Boggle game - IT WORKS! 🎉
- Week 1 complete!

### What I learned
- **Orchestration pattern**: Game class coordinates multiple components without business logic
- **Dependency injection**: Pass Board, Dictionary, Scorer to Game constructor
- **CLI interaction**: `input()`, display functions, game loop pattern
- **Package entry points**: `[project.scripts]` in pyproject.toml creates commands
- **`__name__ == "__main__"`**: How Python distinguishes "run directly" vs "imported"
- **`sys.argv[0]`**: First argument is always the program name
- **`sys.exit()`**: Proper way to exit with status code
- **Cross-platform packaging**: Auto-generated wrapper handles Windows `.exe` and `.pyw`
- **Editable installs**: `uv pip install -e .` for development

### Challenges/Issues
- Module import issue: `from src.board` didn't work with `python src/cli.py`
- Fixed with `python -m src.cli` or by installing package with entry point
- Hatchling build error: needed to tell it where code lives with `packages = ["src"]`

### Key Commands Learned
```bash
python -m src.cli                # Run as module (fixes imports)
uv pip install -e .              # Install package in editable mode
boggle                           # Run installed command!
git merge feature/branch         # Merge feature into current branch
```

### Code Concepts
- **Orchestration class**: Coordinates components without business logic
- **Validation pipeline**: Multiple checks in sequence, early returns
- **CLI game loop**: `while True` with command handling
- **Entry points**: Map command names to Python functions
- **Module execution**: `if __name__ == "__main__"` pattern
- **Helpful error messages**: Give users specific feedback on why word rejected

### Package Structure Learned
```
[project.scripts]
boggle = "src.cli:main"
         ^^^^^^^^^^^^^^
         module:function

Creates wrapper script that:
1. Imports the function
2. Cleans up sys.argv[0] (cross-platform)
3. Calls function with sys.exit()
```

### Game Flow
```
1. Initialize Board, Dictionary, Scorer
2. Create Game with components
3. Display board
4. Loop:
   - Get user input
   - Handle commands (quit/score/words)
   - Validate word:
     * Check minimum length
     * Check dictionary
     * Check board path
     * Check duplicates
   - Update score if valid
5. Display final results
```

### What Makes a Valid Word
```python
✓ Length >= min_word_length
✓ In dictionary (SOWPODS)
✓ Path exists on board (DFS)
✓ Not already submitted
= Valid word! Add to list, update score
```

### Blockers/Questions
- None - everything came together!

### Next Steps (Week 2)
- Add local multiplayer (multiple players on same machine)
- Implement word strike-out logic (duplicates across players)
- Add configurable game options with Pydantic
- Enhance CLI for multi-player experience

### Time spent
~90 minutes

### Reflection
This was the most satisfying day! Everything we built separately (Board, Dictionary, Scorer) came together into an actual playable game. The orchestration pattern is elegant - Game class just coordinates without implementing game logic itself. Setting up the package entry point made the game feel "real" - typing `boggle` to play is much nicer than `python -m src.cli`. 

Understanding `__name__ == "__main__"` and how packaging tools generate wrapper scripts demystified a lot of Python magic. The CLI game loop pattern (input → validate → feedback → repeat) is straightforward and effective.

Week 1 complete! I went from zero to a working single-player Boggle game with tests, type checking, proper packaging, and git workflow. The git workflow is now muscle memory - I naturally check branch status before every commit.

Ready for Week 2: multiplayer, configuration, and more complex game state!

---

## 2025-01-XX: Week 2, Day 1 - Game Configuration with Pydantic

### What we did
- Created GameConfig class using Pydantic for validated configuration
- Added validation for board_size (4 or 5), time_limit (positive), min_word_length (positive), max_players (1-8)
- Made config immutable with `frozen=True`
- Integrated GameConfig into Game class with optional parameter
- Added Pydantic as project dependency with `uv add pydantic`
- All tests passing, type checking passing

### What I learned
- **Pydantic BaseModel**: Powerful data validation library for Python
- **Field validators**: Custom validation logic with `@field_validator`
- **Frozen models**: `frozen=True` makes config immutable after creation
- **Field defaults**: Using `Field(default=...)` with descriptions
- **model_config dict**: Configures model behavior (frozen, validate_assignment)
- **ValidationError**: Pydantic raises this for invalid data
- **Optional with defaults**: `config: GameConfig | None = None` then `config or GameConfig()`

### Challenges/Issues
- Initially forgot to install Pydantic - got ModuleNotFoundError
- Fixed with `uv add pydantic` (not `--dev` since it's a runtime dependency)

### Key Commands Learned
```bash
uv add pydantic              # Add runtime dependency
uv add --dev pytest          # Add dev dependency (for comparison)
```

### Code Concepts
- **Data validation at runtime**: Pydantic validates on object creation
- **Immutability for config**: Prevents accidental changes to game settings
- **Custom validators**: `@field_validator` decorator for complex validation
- **Type hints with constraints**: More than just types - actual validation

### Pydantic Pattern
```python
class GameConfig(BaseModel):
    board_size: int = Field(default=4, description="...")
    
    model_config = {
        "frozen": True,  # Immutable
        "validate_assignment": True
    }
    
    @field_validator("board_size")
    @classmethod
    def validate_board_size(cls, v: int) -> int:
        if v not in (4, 5):
            raise ValueError("board_size must be 4 or 5")
        return v
```

### Blockers/Questions
- None

### Next session
- Day 2: Multi-player game state with Player class

### Time spent
~45 minutes

### Reflection
Pydantic is incredibly powerful for configuration! The validation happens automatically, and the frozen model prevents bugs from accidental config changes. The Field descriptions make the code self-documenting. This is much better than manually validating each field in `__init__`. Integration with Game was smooth - optional parameter with default is a clean pattern.

---

## 2025-01-XX: Week 2, Day 2 - Multi-Player Game State

### What we did
- Created Player class to represent individual players (id, name, words)
- Players can add words to their own list (no duplicates per player)
- Implemented `__eq__` and `__hash__` based on player_id for comparability
- Updated Game to manage multiple players using Dict[str, Player]
- Changed from List to Dict to prevent duplicate player IDs (O(1) lookup)
- Game.submit_word() now accepts optional Player parameter
- Backward compatible - single-player mode still works via _submitted_words
- Max players enforced by GameConfig
- All tests passing, type checking passing

### What I learned
- **`__eq__` and `__hash__`**: Making custom objects comparable and hashable
- **Dict vs List for players**: Dict prevents duplicates and gives O(1) lookup by ID
- **Optional parameters**: `player: Player | None = None` for backward compatibility
- **Property decorator**: `@property` for read-only attribute access
- **Code refactoring**: Extracted `_validate_word()` to avoid duplication
- **Backward compatibility**: Keeping old behavior while adding new features

### Challenges/Issues
- Initially used List for players - could add same player twice
- Fixed by switching to Dict[str, Player] keyed by player_id
- Discovered the bug by asking "what if same player ID added twice?"

### Key Commands Learned
```bash
git diff                     # See changes before committing
git diff src/game.py        # See changes in specific file
```

### Code Concepts
- **`__eq__` for equality**: `player1 == player2` checks player_id
- **`__hash__` for sets/dicts**: Allows Player in set or as dict key
- **Dict for uniqueness**: `dict[player_id] = player` prevents duplicates automatically
- **Optional parameters with None**: `player: Player | None = None`
- **Refactoring for reuse**: Single validation logic used by both modes

### Player Class Design
```python
class Player:
    def __init__(self, player_id: str, name: str):
        self.player_id = player_id
        self.name = name
        self._words: List[str] = []
    
    def __eq__(self, other):
        return self.player_id == other.player_id
    
    def __hash__(self):
        return hash(self.player_id)
```

### Game Multiplayer Pattern
```python
# Single-player (backward compatible)
game.submit_word("CAT")  # Uses _submitted_words

# Multiplayer (new)
game.submit_word("CAT", player1)  # Uses player1._words
```

### Blockers/Questions
- None

### Next session
- Day 3: Word strike-out logic (classic Boggle rule)

### Time spent
~45 minutes

### Reflection
The switch from List to Dict for players was a great design decision - prevents bugs and is more efficient. The `__eq__` and `__hash__` implementation makes Player objects work naturally with Python's built-in data structures. Keeping backward compatibility for single-player was important - didn't break existing tests. The optional Player parameter is a clean way to support both modes without duplicating code.

---

## 2025-01-XX: Week 2, Day 3 - Word Strike-Out Logic

### What we did
- Implemented classic Boggle strike-out rule: duplicate words across players don't score
- Added `get_duplicate_words()` - finds words submitted by multiple players
- Added `get_player_valid_words()` - returns player's words excluding duplicates
- Added `get_player_score()` - calculates score only from unique words
- Comprehensive tests including edge case where all players find same word
- All tests passing, type checking passing

### What I learned
- **Word counting algorithm**: Count occurrences across all players using dict
- **Set comprehension**: `{word for word, count in items if count > 1}`
- **List comprehension with filter**: `[word for word in words if word not in set]`
- **Dict.get() with default**: `word_counts.get(word, 0) + 1` to avoid KeyError
- **Set operations**: Using set for O(1) lookup when filtering duplicates
- **Game logic separation**: Strike-out logic separate from submission logic

### Challenges/Issues
- None - straightforward implementation
- Note: Committed implementation before tests (should be reversed for TDD)

### Key Commands Learned
```bash
# No new commands - continued using existing git workflow
```

### Code Concepts
- **Frequency counting**: Building dict to count word occurrences
- **Set for fast lookup**: `word in duplicates` is O(1) instead of O(n)
- **Filtering with comprehensions**: Concise way to exclude items
- **Separation of concerns**: Duplicate detection separate from scoring

### Strike-Out Algorithm
```python
def get_duplicate_words(self) -> set[str]:
    word_counts: Dict[str, int] = {}
    
    # Count occurrences
    for player in self._players.values():
        for word in player.get_words():
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Return words that appear more than once
    return {word for word, count in word_counts.items() if count > 1}

def get_player_valid_words(self, player: Player) -> List[str]:
    duplicates = self.get_duplicate_words()
    return [word for word in player.get_words() if word not in duplicates]
```

### Time Complexity
- `get_duplicate_words()`: O(n × m) where n = players, m = avg words per player
- `get_player_valid_words()`: O(m) where m = player's word count
- Efficient for typical Boggle games (4 players, 10-20 words each)

### Example Strike-Out
```
Alice: CAT, DOG, FISH
Bob:   CAT, BIRD, FISH
Charlie: MOUSE

Duplicates: {CAT, FISH}
Alice scores: DOG only
Bob scores: BIRD only
Charlie scores: MOUSE
```

### Blockers/Questions
- None

### Next session
- Day 4: Multiplayer CLI (player turns, score display, game flow)

### Time spent
~60 minutes

### Reflection
The strike-out logic is the heart of what makes Boggle competitive! The algorithm is elegant - just count occurrences and filter. Using a set for duplicates gives O(1) lookup when filtering each player's words. The separation between "what words did players submit" and "which words count for scoring" is clean. This is a great example of how simple data structures (dict for counting, set for lookup) solve the problem efficiently. Ready to build the multiplayer CLI so we can actually play with strike-outs!

---

## 2025-01-XX: Week 2, Day 4 - Multiplayer CLI

### What we did
- Built interactive multiplayer CLI with turn-based gameplay
- Added game mode selection (single player vs multiplayer)
- Implemented turn system with pass mechanics
- Game ends when all players pass consecutively
- Created comprehensive multiplayer results display
- Shows final scores sorted by rank
- Displays each player's valid words (✓) and struck-out words (✗)
- All commands work per-player: score, words, rotate, pass

### What I learned
- **Turn-based game loops**: Cycling through players with modulo arithmetic
- **Consecutive pass tracking**: Counter resets on any word submission
- **Lambda functions for sorting**: `key=lambda p: game.get_player_score(p)`
- **enumerate with start parameter**: `enumerate(players, 1)` for ranking
- **Modulo for cycling**: `(current_idx + 1) % len(players)` wraps around
- **List comprehension for filtering**: `[w for w in words if w not in duplicates]`
- **Dict vs List tradeoff**: Using dict prevented duplicate player IDs automatically

### Challenges/Issues
- Initially forgot to reset consecutive pass counter on word submission
- Fixed duplicate player bug by switching from List to Dict for player storage
- Had to think through when game should end (all players pass, not just one round)

### Key Commands Learned
```bash
boggle                          # Run the game with mode selection
# (All existing git commands becoming second nature)
```

### Code Concepts
- **Turn management**: Track current player index, cycle with modulo
- **Pass system**: Count consecutive passes across all players
- **Results display**: Sort players by score, show breakdown per player
- **Conditional formatting**: ✓ for valid words, ✗ for struck-out
- **Game end condition**: `consecutive_passes >= len(players)`

### Game Flow Algorithm
```python
consecutive_passes = 0
current_player_idx = 0

while consecutive_passes < len(players):
    current_player = players[current_player_idx]
    
    word = get_input()
    
    if word == "pass":
        consecutive_passes += 1
        current_player_idx = (current_player_idx + 1) % len(players)
    elif submit_word(word, current_player):
        consecutive_passes = 0  # Reset on successful word
    
    # Move to next player after submission
```

### Multiplayer Results Format
```
FINAL SCORES:
1. Alice: 15 points (8 words, 2 struck out)
2. Bob: 12 points (7 words, 3 struck out)

WORD BREAKDOWN:
Alice's words:
  ✓ CAT (3 letters) - 1 point
  ✓ DOGS (4 letters) - 2 points
  
  Struck out (duplicates):
  ✗ FISH (0 points)
```

### Bug Fix: Duplicate Players
**Problem**: Could add same player twice (same player_id)
**Solution**: Changed `_players: List[Player]` to `_players: Dict[str, Player]`
**Benefit**: O(1) lookup by ID, automatic duplicate prevention

### Design Decisions
- **Pass vs Quit**: "pass" ends turn, all players passing consecutively ends game
- **Turn display**: Clear separator showing whose turn it is
- **Command availability**: All commands (score, words, rotate) work during any turn
- **Results sorting**: Highest score first, natural competitive display

### Blockers/Questions
- None - multiplayer works great!

### Next session
- Day 5: Game timer and time limits
- Add countdown timer during gameplay
- Auto-end game when time expires
- Display remaining time

### Time spent
~60 minutes

### Reflection
Bringing everything together into a multiplayer CLI was incredibly satisfying! The turn-based system with pass mechanics creates a natural game flow. The consecutive pass counter is elegant - it ensures the game ends when everyone is done, not just after one round. Switching to a dict for players fixed the duplicate bug and improved code quality. The results display with strike-outs makes the competitive aspect clear and exciting. 

The modulo arithmetic for player cycling is a classic game programming pattern. Testing with multiple "players" (myself) revealed the importance of the consecutive pass reset - without it, the game ends too early if anyone passes once.

Week 2 progress has been amazing - went from single-player to full multiplayer with strike-outs and turn management. The game is genuinely fun to play now! Ready to add the final piece: a countdown timer for that classic Boggle pressure!

---

## 2025-01-XX: Week 2, Day 5 - Game Timer

### What we did
- Implemented game timer using Python's `time` module
- Added `start_timer()` method to begin tracking
- Implemented `get_elapsed_time()` for time since start
- Implemented `get_remaining_time()` for countdown
- Added `is_time_expired()` to check if time limit exceeded
- Integrated timer into multiplayer CLI
- Made timer optional (can play with or without)
- Display live countdown on each turn
- Auto-end game when timer expires
- Timer shows MM:SS format for readability

### What I learned
- **`time.time()`**: Returns current Unix timestamp (seconds since epoch)
- **Time calculations**: `current - start` for elapsed, `limit - elapsed` for remaining
- **`max(0, value)`**: Prevents negative time display
- **Optional state**: `start_time: float | None` for optional timer
- **None propagation**: If start_time is None, all time methods return None
- **Type narrowing**: mypy understands `if x is None: return None` pattern
- **Format strings**: `f"{mins}:{secs:02d}"` for zero-padded seconds
- **Boolean short-circuit**: `remaining is None` returns False without computing

### Challenges/Issues
- Initially forgot to check for None before doing time calculations
- Had to decide: should timer be always-on or optional? (chose optional)
- Format decision: show seconds as float or int? (chose int for cleaner display)

### Key Commands Learned
```bash
# All git commands are second nature now!
```

### Code Concepts
- **Timestamp tracking**: Store `start_time` as Unix timestamp
- **Delta calculations**: Current time minus start time
- **Countdown math**: Limit minus elapsed
- **None handling**: Return None if timer not started
- **Optional features**: Feature exists but doesn't have to be used

### Timer Implementation
```python
def start_timer(self) -> None:
    self.start_time = time.time()

def get_elapsed_time(self) -> float | None:
    if self.start_time is None:
        return None
    return time.time() - self.start_time

def get_remaining_time(self) -> float | None:
    elapsed = self.get_elapsed_time()
    if elapsed is None:
        return None
    return max(0, self.config.time_limit_seconds - elapsed)
```

### Timer Display Logic
```python
if use_timer:
    remaining = game.get_remaining_time()
    if remaining is not None:
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        print(f"⏱️  Time remaining: {mins}:{secs:02d}")
```

### Time Format Examples
```
⏱️  Time remaining: 2:47
⏱️  Time remaining: 0:15
⏰ TIME'S UP! ⏰
```

### Design Decisions
- **Optional timer**: Player chooses at game start
- **Classic 3-minute default**: Standard Boggle time limit
- **Check on each turn**: Not real-time polling, checks between turns
- **Graceful handling**: Game works perfectly without timer
- **Auto-end on expiry**: No need to manually check, game ends automatically

### Testing Approach
- Used `time.sleep()` in tests to verify timer works
- Short timeouts (0.1s, 1.1s) for fast tests
- Tested None propagation for games without timer
- Verified elapsed and remaining time calculations

### Type Hints
```python
start_time: float | None = None      # Optional timestamp
get_elapsed_time() -> float | None   # Returns None if not started
is_time_expired() -> bool            # Always returns bool (False if no timer)
```

### Blockers/Questions
- None

### Next session
- Day 6: Final polish and documentation
- Add README with game rules
- Clean up any edge cases
- Final testing
- Celebrate completion of Week 2!

### Time spent
~45 minutes

### Reflection
Adding the timer brought that classic Boggle pressure! The time module is straightforward - just store a timestamp and compare. The key design decision was making it optional - not every game needs time pressure. The None propagation pattern is elegant: if there's no start_time, all time methods gracefully return None or False.

The live countdown display adds urgency without being intrusive - it shows at the start of each turn but doesn't interrupt gameplay. Using integer division and modulo for MM:SS format is a classic time formatting pattern.

Testing with `time.sleep()` was interesting - usually you avoid sleeping in tests, but here it's necessary to verify timer behavior. Keeping the sleep times short (0.1s, 1.1s) keeps tests fast.

The optional feature pattern is important: the game works perfectly without a timer, but the timer adds an extra dimension when wanted. This is good software design - features should be additive, not mandatory.

Week 2 is almost complete! From single-player to multiplayer with strike-outs and timer. The game now has all the classic Boggle features. Ready for final polish!

---

## 2025-01-XX: Week 2, Day 6 - Final Polish & Documentation

### What we did
- Created comprehensive README with game rules and architecture
- Documented all features, commands, and scoring rules
- Added project structure overview
- Explained strike-out rule with examples
- Documented algorithms with time complexity
- Listed learning objectives and future enhancements
- Verified .gitignore is complete
- Reviewed all code for edge cases
- Completed Week 2!

### What I learned
- **README structure**: Features → Installation → Usage → Development → Architecture
- **Code examples in docs**: Show actual usage, not just descriptions
- **Architecture documentation**: Explain design principles and key components
- **Algorithm documentation**: Include time complexity analysis
- **Future planning**: Document what's next while fresh in mind
- **Project completeness**: README, tests, types, git history all matter

### Challenges/Issues
- None - smooth wrap-up!

### Key Sections in README
```
Features (what it does)
Installation (how to set up)
How to Play (game rules)
Commands (user reference)
Project Structure (code organization)
Development (for contributors)
Architecture (design decisions)
Algorithm Highlights (technical depth)
```

### Documentation Best Practices
- **Start with features**: Tell users what the project does
- **Quick start section**: Get users playing immediately
- **Examples over descriptions**: Show, don't just tell
- **Technical depth for developers**: Algorithm analysis, architecture
- **Visual formatting**: Use emojis, code blocks, examples
- **Keep it current**: Update as features change

### What Makes Good Documentation
1. **User-focused**: Answers "how do I use this?"
2. **Developer-focused**: Answers "how does this work?"
3. **Examples**: Real code and gameplay scenarios
4. **Structure**: Easy to scan and find information
5. **Complete**: Installation, usage, development, architecture

### Week 2 Feature Summary
**Day 1**: Game configuration with Pydantic validation
**Day 2**: Multiplayer state (Player class, game manages multiple players)
**Day 3**: Word strike-out logic (classic Boggle rule)
**Day 4**: Multiplayer CLI with turn-based gameplay
**Day 5**: Game timer with countdown and auto-end
**Day 6**: Documentation and polish

### Blockers/Questions
- None - Week 2 complete!

### Next Steps
Week 3 will focus on network multiplayer and advanced features:
- WebSocket-based multiplayer
- Game rooms and lobbies
- Persistent game state
- Leaderboards
- Web interface

### Time spent
~60 minutes

### Reflection
Week 2 transformed the game from single-player to full multiplayer with all classic Boggle features. The progression was logical: config → players → strike-outs → CLI → timer → docs. Each day built on the previous one.

Writing the README forced me to think about the project holistically. What would someone need to know to play? To develop? To understand the architecture? Good documentation serves multiple audiences: users, developers, and future maintainers.

The strike-out example in the README makes the rule immediately clear - better than just describing it. The algorithm section with time complexity shows technical depth. The project structure gives an overview of how everything fits together.

Looking back at Week 1 and 2, the learning progression is clear:
- Week 1: Core game mechanics (board, dictionary, scoring, single-player)
- Week 2: Multiplayer features (players, turns, strike-outs, timer)

The git history tells the story: 40+ commits, each with a clear purpose. The test coverage is comprehensive. The type checking catches errors. The code is clean and well-organized.

Week 2 complete! 🎉

---

# Week 2 Summary

## What We Built
- **GameConfig**: Validated configuration with Pydantic
- **Player**: Individual player state management
- **Multiplayer Game**: Support for 2-4 players with turn-based gameplay
- **Strike-Out Logic**: Duplicate words across players don't count
- **Multiplayer CLI**: Interactive turn system with pass mechanics
- **Game Timer**: Optional countdown with live display
- **Comprehensive README**: Full documentation

## Technical Achievements
- **40+ total commits** across 12 days of development
- **20+ test files** with comprehensive coverage
- **Full type safety** with mypy
- **Clean architecture** with separation of concerns
- **Professional documentation**

## Key Algorithms Implemented
1. **DFS with backtracking** for word path validation
2. **Fibonacci scoring** for word length
3. **Strike-out detection** with word counting
4. **Turn management** with modulo cycling
5. **Timer tracking** with elapsed/remaining calculations

## Python Concepts Mastered
- Pydantic validation and frozen models
- Optional types (`float | None`)
- Dict vs List tradeoffs
- Set comprehensions
- Lambda functions
- Time calculations
- Property decorators
- Dunder methods (`__eq__`, `__hash__`)

## Design Patterns Used
- **Dependency injection**: Pass components to Game
- **Orchestration**: Game coordinates without business logic
- **Validation layers**: Multiple checks for word submission
- **Optional features**: Timer can be enabled/disabled
- **Separation of concerns**: Each class has one responsibility

## Lines of Code
- **Source code**: ~800 lines
- **Test code**: ~600 lines
- **Total**: ~1400 lines of type-safe, tested Python

## What's Next (Week 3)
Network multiplayer with:
- WebSocket server
- Game rooms
- Real-time updates
- Web interface
- Persistent state

## Reflection on Week 2
Week 2 was about **multiplayer transformation**. Every feature added depth to the game: players create competition, strike-outs create strategy, turns create structure, timer creates pressure.

The progression from single-player (Week 1) to multiplayer (Week 2) taught important lessons about state management. Single-player is simple: one list of words, one score. Multiplayer requires managing multiple players, tracking who submitted what, detecting duplicates, cycling through turns.

The strike-out rule is what makes multiplayer Boggle strategic. Without it, multiplayer would just be multiple people playing solo on the same board. With strike-outs, players must find unique words - the same core mechanic that makes Scrabble strategic.

Git workflow is now second nature. Feature branches, clear commits, merges, pushes - all automatic. The commit history tells a clear story of development. Type checking catches errors before runtime. Tests verify behavior. The development process is professional.

Most importantly: **the game is fun to play!** That's the ultimate validation. Family and friends can play together, the timer adds pressure, the strike-outs create competition, and the results show who found the most unique words.

Ready for Week 3 - network multiplayer! 🚀

---

# Week 3: Network Multiplayer

## 2025-01-XX: Week 3, Day 1 - WebSocket Basics & Echo Server

### What we did
- Installed `websockets` library for async WebSocket communication
- Built simple echo server that handles multiple clients
- Built echo client for testing
- Tested real-time bidirectional communication
- Learned async/await fundamentals
- Created src/network/ package structure

### What I learned
- **WebSockets vs HTTP**: WebSocket maintains persistent connection, HTTP is request-response
- **`async def`**: Declares asynchronous function that returns a coroutine
- **`await`**: Pauses execution, yields control to event loop
- **`async for`**: Asynchronous iteration - waits for each item to arrive
- **Event loop**: Manages concurrent operations without threads
- **Concurrent connections**: Server handles multiple clients simultaneously
- **`asyncio.run()`**: Starts event loop and runs async main function
- **`websockets.serve()`**: Creates WebSocket server
- **`websockets.connect()`**: Connects to WebSocket server

### Challenges/Issues
- Initially confused about `async for` - realized it's like `await` but for loops
- Accidentally made duplicate commits (no harm done)

### Key Commands Learned
```bash
uv add websockets                    # Add WebSocket library
python src/network/echo_server.py    # Run server
python src/network/echo_client.py    # Run client
# Run in separate terminals to test
```

### Code Concepts
- **Async handler pattern**: `async def handler(websocket)`
- **Message loop**: `async for message in websocket`
- **Send/receive**: `await websocket.send()` and `await websocket.recv()`
- **Context managers**: `async with websockets.serve()` and `async with websockets.connect()`
- **Forever future**: `await asyncio.Future()` keeps server running

### Echo Server Architecture
```
Server (localhost:8765)
    |
    |-- Client 1 (connection 1)
    |-- Client 2 (connection 2)
    |-- Client 3 (connection 3)
    
Each connection handled concurrently!
```

### async/await Explanation
```python
# Regular function (synchronous)
def process():
    result = slow_operation()  # Blocks - nothing else runs
    return result

# Async function (asynchronous)
async def process():
    result = await slow_operation()  # Pauses - other code runs
    return result
```

### async for Explained
```python
# Regular for (synchronous)
for item in list:
    print(item)  # Items already in memory

# async for (asynchronous)
async for message in websocket:
    print(message)  # Wait for each message to arrive over network
```

**Key insight**: `async for` waits for each item to arrive, one at a time, yielding control while waiting.

### WebSocket Message Flow
```
Client                    Server
  |                         |
  |--- "hello" ------------>|
  |                         | (processes)
  |<--- "Echo: hello" ------|
  |                         |
  |--- "world" ------------>|
  |                         | (processes)
  |<--- "Echo: world" ------|
```

### Why Async Matters for Games
- **Multiple clients**: Handle 10+ players simultaneously
- **No blocking**: While waiting for Player 1's message, process Player 2's
- **Real-time**: Instant updates to all clients
- **Scalable**: Can handle many concurrent connections efficiently

### Testing Experience
Ran two clients simultaneously:
- Terminal 1: Server running, showing connections
- Terminal 2: Client 1 sending "hello"
- Terminal 3: Client 2 sending "test"
- Both worked independently - that's the power of async!

### Blockers/Questions
- None - async fundamentals clear!

### Next session
- Day 2: Game server with rooms and player management
- JSON protocol for structured messages
- Broadcasting to all players in a room
- Room creation and joining

### Time spent
~45 minutes

### Reflection
WebSockets are surprisingly straightforward once you understand async/await! The echo server is a perfect learning tool - simple enough to understand quickly, but demonstrates all the key concepts: persistent connections, concurrent handling, bidirectional communication.

The `async for` concept clicked when I realized it's just "await in a loop" - waiting for each item to arrive over the network. The synchronous equivalent would block the entire server, but async lets us handle multiple clients.

Seeing two clients connect simultaneously and both get echoes back independently was the "aha!" moment - that's true concurrency without threads or multiprocessing. Python's asyncio event loop handles it all.

The echo server is throwaway learning code, but the concepts transfer directly to building a real game server. Next step: instead of echoing messages, we'll manage game rooms, validate moves, and broadcast game state to all players.

Week 3 is going to be exciting - transforming from local multiplayer to network multiplayer is a huge leap in complexity, but also in capability. The game becomes truly multiplayer - not just multiple people on one computer, but people across the internet playing together!

---

## 2025-01-XX: Week 3, Day 2 - Game Server with Rooms

### What we did
- Designed JSON message protocol with MessageType enum
- Created protocol.py with encode_message() and decode_message()
- Built GameRoom class for managing individual game sessions
- Built GameServer class that manages multiple rooms
- Implemented player registration and tracking
- Added room creation and joining logic
- Implemented game start with board generation
- Added word submission and validation
- Built turn management system
- Implemented broadcasting to all players in a room
- Added automatic room cleanup when empty
- Fixed WebSocket type issues (str vs bytes, legacy imports)

### What I learned
- **Message protocol design**: Use enums for type safety, JSON for structure
- **Room architecture**: Server manages multiple independent game rooms
- **Player tracking**: Two mappings - `player_id -> Player` and `player_id -> room_id`
- **Broadcasting pattern**: Send to all connections in a room except sender
- **asyncio.gather()**: Send to multiple WebSockets concurrently
- **Type handling**: WebSocket messages can be str or bytes
- **Type ignores**: Sometimes necessary for imperfect library type stubs
- **Cleanup patterns**: Remove empty rooms automatically
- **UUID generation**: `uuid.uuid4()` for unique IDs, `[:8]` for short room codes

### Challenges/Issues
- WebSocket library changed API: `websockets.server` → `websockets.legacy.server`
- Messages can be str or bytes - needed isinstance() checks
- json.loads() returns Any - needed explicit type annotation
- websockets.serve() type stub mismatch - used `# type: ignore[arg-type]`
- Missing Player import in game_server.py

### Key Commands Learned
```bash
python src/network/game_server.py    # Run the game server
# Server loads dictionary and waits for connections
```

### Code Concepts
- **Message protocol**: Structured communication with type safety
- **Room management**: Dictionary of room_id -> GameRoom
- **Player-to-room mapping**: Track which room each player is in
- **Broadcasting**: Send message to multiple recipients
- **Concurrent sends**: asyncio.gather() for parallel operations
- **Connection tracking**: Store WebSocket for each player

### Message Protocol Design
```python
# Define all message types as enum
class MessageType(str, Enum):
    CREATE_ROOM = "create_room"
    ROOM_CREATED = "room_created"
    # ... more types

# Encode with type safety
def encode_message(type: MessageType, data: Dict) -> str:
    return json.dumps({"type": type.value, **data})

# Decode with error handling
def decode_message(msg: str) -> Dict[str, Any]:
    result: Dict[str, Any] = json.loads(msg)
    return result
```

### GameRoom Architecture
```python
class GameRoom:
    players: Dict[str, Player]           # player_id -> Player
    connections: Dict[str, WebSocket]    # player_id -> WebSocket
    game: Game | None                    # Actual game instance
    is_started: bool                     # Game state
    current_turn_index: int              # Whose turn
```

### Server Message Handling
```python
async def handle_client(websocket):
    player_id = uuid.uuid4()
    
    async for message in websocket:
        # Route based on message type
        if type == CREATE_ROOM:
            handle_create_room(...)
        elif type == SUBMIT_WORD:
            handle_submit_word(...)
```

### Broadcasting Pattern
```python
async def broadcast_to_room(room_id, message, exclude=None):
    room = self.rooms[room_id]
    websockets_to_send = [
        ws for pid, ws in room.connections.items()
        if pid != exclude
    ]
    await asyncio.gather(
        *[ws.send(message) for ws in websockets_to_send],
        return_exceptions=True
    )
```

### Type Issues Fixed
1. **Import path**: `websockets.server` → `websockets.legacy.server`
2. **str vs bytes**: Added `isinstance()` checks
3. **json.loads() return type**: Explicit annotation
4. **Missing imports**: Added Player import
5. **Type stub mismatch**: Added `# type: ignore[arg-type]`

### Server Architecture
```
GameServer
    ├── rooms: Dict[room_id, GameRoom]
    ├── player_to_room: Dict[player_id, room_id]
    ├── dictionary: Dictionary (shared)
    └── scorer: Scorer (shared)

Each GameRoom:
    ├── players: Dict[player_id, Player]
    ├── connections: Dict[player_id, WebSocket]
    ├── game: Game (board, validation, scoring)
    └── current_turn_index: int
```

### Message Flow Example
```
Client                    Server
  |                         |
  |-- CREATE_ROOM --------->|
  |                         | (creates room "abc123")
  |<-- ROOM_CREATED --------|
  |                         |
  |-- START_GAME ---------->|
  |                         | (generates board, starts game)
  |<-- GAME_STARTED --------|
  |                         |
  |-- SUBMIT_WORD "CAT" --->|
  |                         | (validates, updates score)
  |<-- WORD_ACCEPTED -------|
```

### Design Decisions
- **Short room IDs**: `uuid.uuid4()[:8]` for easy sharing
- **Automatic cleanup**: Empty rooms deleted immediately
- **Shared resources**: One dictionary/scorer for all rooms (memory efficient)
- **Turn tracking by index**: Cycle through players with modulo
- **Exclude sender**: Broadcast to others but not the sender

### Blockers/Questions
- None - server working well!

### Next session
- Day 3: Network client with CLI
- Connect to server and send/receive messages
- Interactive lobby and game interface
- Handle concurrent receive loop and user input

### Time spent
~90 minutes

### Reflection
Building the game server was complex but incredibly rewarding! The architecture with GameServer managing multiple GameRooms is clean and scalable. Each room is independent - different games can be at different stages simultaneously.

The message protocol with enums is type-safe and extensible. Using JSON makes debugging easy (can see exactly what's being sent). The broadcasting pattern with asyncio.gather() is elegant - send to all clients concurrently without blocking.

The type issues were a good learning experience. Third-party libraries don't always have perfect type stubs. The websockets library changed its API structure, and mypy caught it immediately. Learning when to use `# type: ignore` is important - it's not cheating, it's acknowledging that you know more than the type checker in specific cases.

The player-to-room mapping is crucial for routing messages correctly. When a player submits a word, we need to know which room they're in to validate it and broadcast to the right people.

Room cleanup is important - memory leaks would happen if we kept empty rooms forever. Automatic cleanup on last player disconnect keeps the server clean.

Next step is building the client - that's when everything comes together and we can actually test the full game flow! The server is just infrastructure; the client is the user-facing experience.

---

## 2025-01-XX: Week 3, Day 3 - Network Client with CLI & Timer

### What we did
- Built GameClient class for WebSocket connection
- Created interactive CLI with main menu, lobby, and game loop
- Solved async input problem by switching to aioconsole
- Implemented concurrent word submission (removed turn system)
- Added configurable game timer
- Implemented auto-start when room is full
- Added game ended handling with final scores display
- Fixed race conditions with defense-in-depth state checking
- Removed all debug logging
- Tested full multiplayer game flow

### What I learned
- **The async input problem**: Python's `input()` blocks the event loop completely
- **aioconsole library**: Provides `ainput()` for proper async input
- **Why run_in_executor doesn't work well**: Threading + timeouts = race conditions
- **Defense in depth**: Check state both periodically AND before processing
- **Race condition example**: Game starts between input completion and command processing
- **asyncio.create_task()**: Background tasks for timer monitoring
- **Clean code wins**: Simple aioconsole solution vs complex threading hacks

### Challenges/Issues
- Initially used `run_in_executor` with `input()` - caused blocking issues
- Timeout approach missed input completions
- Race condition: lobby commands processed after game started
- Prompts not displaying after server messages
- Had to understand the fundamental incompatibility of sync input with async code

### Key Commands Learned
```bash
uv add aioconsole                         # Add async console library
python src/network/game_server.py         # Run server
python src/network/network_cli.py         # Run client
```

### Code Concepts
- **Proper async input**: `await aioconsole.ainput("> ")`
- **Background tasks**: `asyncio.create_task(monitor_timer())`
- **State checking**: Verify game state before processing commands
- **Concurrent loops**: receive_messages running while game_loop gets input
- **Task cancellation**: Cancel input task when game state changes

### The Async Input Problem - Explained

#### Problem:
```python
# This BLOCKS everything - event loop can't process server messages
command = input("> ")
```

#### Attempted Fix 1 (run_in_executor):
```python
# Run input in thread pool
loop = asyncio.get_event_loop()
command = await loop.run_in_executor(None, lambda: input("> "))
```
**Issues**: Still complex, timeout logic needed, race conditions

#### Clean Solution (aioconsole):
```python
# Native async input - plays nice with event loop
command = await aioconsole.ainput("> ")
```
**Benefits**: Simple, no threads, no timeouts, just works!

### Game Loop Architecture

```
run_client()
    ├── connect to server
    ├── create_task(receive_messages())  ← Background: listens for server
    └── main_menu()
            ├── create_room_flow()
            │       └── lobby()
            │               └── game_loop()  ← Foreground: gets user input
            └── join_room_flow()
                    └── lobby()
                            └── game_loop()
```

Two concurrent async tasks:
1. **receive_messages()**: Always listening for server messages
2. **game_loop()**: Getting user input and sending commands

### Lobby Loop Pattern

```python
while client.connected and not client.in_game:
    # Create input task
    input_task = asyncio.create_task(aioconsole.ainput("\n> "))
    
    # Wait for input OR game state change
    while not input_task.done() and not client.in_game:
        await asyncio.sleep(0.1)  # Check state every 0.1s
    
    # If game started, cancel input and exit
    if client.in_game:
        input_task.cancel()
        break
    
    # Process command
    command = input_task.result()
    
    # Double-check state before processing (defense in depth!)
    if client.in_game:
        break
```

### Game Loop (Final Clean Version)

```python
while client.connected and client.in_game:
    command = await aioconsole.ainput("\n> ")
    command = command.strip().lower()
    
    if command == "board":
        client.display_board()
    elif command == "quit":
        await client.disconnect()
        break
    else:
        await client.submit_word(command)
```

**So simple!** No threads, no executors, no timeouts, no tasks.

### Timer Implementation

**Server side:**
```python
async def handle_start_game(player_id):
    room.game.start_timer()
    asyncio.create_task(monitor_game_timer(room_id))  # Background task

async def monitor_game_timer(room_id):
    await asyncio.sleep(time_limit)
    # Calculate scores and broadcast GAME_ENDED
```

**Client side:**
```python
def handle_game_ended(message):
    self.in_game = False  # Exits game_loop
    # Display final scores with strike-outs
```

### Features Added
1. **Configurable timer**: User chooses time limit when creating room
2. **Auto-start**: Game starts automatically when room is full
3. **Concurrent submission**: No turns, everyone submits simultaneously
4. **Final results**: Beautiful display with valid and struck-out words
5. **Defense in depth**: Multiple state checks prevent race conditions

### Race Condition Example

```
Timeline without defense:
1. Player in lobby, waiting for input
2. Other player types "start"
3. Server sends GAME_STARTED
4. receive_messages sets in_game = True
5. Player presses Enter on "bot"
6. Lobby processes "bot" as command ❌ WRONG!

Timeline with defense:
1-5. Same as above
6. Before processing, check: if in_game: break ✅ CORRECT!
```

### Design Decisions
- **Removed turns**: Concurrent submission is more fun and natural
- **Auto-start**: Better UX - no waiting when room is full
- **Configurable timer**: Easier testing with short times (30s vs 3min)
- **aioconsole over threading**: Clean code trumps clever hacks
- **Periodic + pre-process checks**: Defense in depth for race conditions

### Blockers/Questions
- None - game works great!

### Next session
- Day 4: Polish and additional features?
- Or start Week 4?

### Time spent
~3 hours (including debugging async input issues)

### Reflection
This was the hardest day yet, but also the most rewarding! The async input problem was a real challenge. We tried threading with `run_in_executor`, timeout-based polling, task management - all complex and buggy. The breakthrough was realizing we needed a library designed for this: `aioconsole`.

The key insight: **don't fight the framework**. Python's `input()` is fundamentally synchronous. Wrapping it in threads and tasks is fighting against its nature. Using a library built for async input (`aioconsole`) works with the framework.

The race condition debugging was excellent learning. The issue where lobby commands were processed after game start seemed mysterious at first, but tracing through the timeline made it clear: we need to check state BOTH periodically (to catch changes while waiting) AND before processing (to catch changes that just happened).

The game is now fully functional over the network! Two people on different computers can play Boggle together in real-time. That's incredible progress from where we started. The WebSocket communication is solid, the game logic works perfectly, and the CLI is responsive.

Removing turns and making submission concurrent was a great decision - it's more fun and removes a lot of complexity. The auto-start feature makes the UX smooth. The configurable timer makes testing much faster.

The final results display with strike-outs is satisfying - you can see exactly which words you found and which got struck out. The game feels complete and polished.

Week 3 Day 3 complete! We have a working network multiplayer Boggle game! 🎉

---

## 2025-10-29: Week 3, Day 4 (Restart) - Introduction to FastAPI and REST APIs

### What we did
- Switched from Claude web chat to Claude Code terminal experience
- Created comprehensive CLAUDE.md documentation for the project
- Recognized we skipped REST APIs and went straight to WebSockets
- Started Week 3 properly: implementing REST API with FastAPI
- Created feature branch `feature/fastapi-rest-api`
- Installed FastAPI, uvicorn, and httpx dependencies
- Designed REST API endpoints (POST /games, POST /games/{id}/players, etc.)
- Created Pydantic models for request/response validation
- Implemented 2 endpoints with TDD:
  - POST /games - Create new game
  - POST /games/{game_id}/players - Join game
- All tests passing, mypy type checking passing

### What I learned

**FastAPI Fundamentals:**
- FastAPI automatically validates requests using Pydantic models
- Auto-generated API documentation at `/docs` (Swagger UI)
- Path parameters: `{game_id}` in URL becomes function parameter automatically
- Status codes: 201 Created, 404 Not Found, 400 Bad Request
- TestClient for testing APIs without running the server

**REST API Design:**
- RESTful resources and HTTP verbs (POST, GET, PUT, DELETE)
- Proper status codes for different scenarios
- Request/response models with Pydantic
- Error handling with HTTPException

**Pydantic Models:**
- Field validation (min/max values, string length, etc.)
- Default values in models
- Type-safe request/response structures
- Automatic JSON serialization/deserialization

**TDD with FastAPI:**
- Write tests first using TestClient
- Tests fail (RED)
- Implement endpoint (GREEN)
- All tests pass
- This cycle ensures we only build what's needed

**Key Code Patterns:**
```python
# Path parameters automatically extracted
@app.post("/games/{game_id}/players")
def join_game(game_id: str, request: JoinGameRequest):
    # game_id comes from URL, request from JSON body
    pass

# Default values allow optional request bodies
def create_game(request: CreateGameRequest = CreateGameRequest()):
    # Can call POST /games with no body (uses defaults)
    # Or POST /games with JSON body (overrides defaults)
    pass

# Proper error handling
if game_id not in games:
    raise HTTPException(status_code=404, detail="Game not found")
```

### Challenges/Issues
- Initially confused about why we were going "backwards" to REST APIs
- Understood that WebSockets were Week 4, and we skipped Week 3
- Learning the difference between path parameters and request body
- Understanding how FastAPI automatically maps URL paths to function parameters

### Key Commands Learned
```bash
uv add fastapi "uvicorn[standard]"  # Install FastAPI
uv add --dev httpx                  # Install HTTP client for testing
pytest tests/test_api.py -v         # Run API tests
mypy src/api_server.py              # Type check API code
git checkout -b feature/name        # Create feature branch
```

### Code Concepts

**Path Parameters:**
- URL: `/games/{game_id}/players`
- FastAPI extracts `game_id` from URL
- Passes it as function argument
- Names must match exactly

**Pydantic Field Validation:**
```python
board_size: int = Field(default=4, ge=4, le=5)
# ge = greater than or equal (min)
# le = less than or equal (max)
```

**In-Memory State:**
```python
games: Dict[str, Dict] = {}  # game_id -> game_state
# In production, this would be a database
```

**HTTP Status Codes:**
- 200 OK - Successful GET
- 201 Created - Successful POST (resource created)
- 400 Bad Request - Client error (e.g., room full)
- 404 Not Found - Resource doesn't exist
- 422 Unprocessable Entity - Validation error

### Blockers/Questions
- None! FastAPI is very intuitive once you understand the patterns

### Next session
- Implement remaining 3 endpoints:
  - GET /games/{game_id} - Get game state
  - POST /games/{game_id}/start - Start game
  - POST /games/{game_id}/words - Submit word
  - GET /games/{game_id}/results - Get final results
- Then we can integrate with our existing game logic
- Finally add WebSockets on top of REST API

### Time spent
~1.5 hours

### Reflection

This was a great learning day! Going back to implement REST APIs properly was the right decision. I now understand:

1. **Why REST APIs matter**: They're the foundation of web services. Even if we add WebSockets later, REST APIs are essential for CRUD operations (Create, Read, Update, Delete).

2. **FastAPI is magical**: The automatic parameter extraction, validation, and documentation generation is amazing. Coming from C and Go, Python's type hints + Pydantic make APIs so much easier to build correctly.

3. **TDD really works**: Writing tests first forced me to think about the API design from the client's perspective. The tests document how the API should behave.

4. **Path parameters are elegant**: The way `{game_id}` in the URL automatically becomes `game_id` in the function is beautiful. No manual parsing needed.

5. **Status codes matter**: Using the right HTTP status code (201 vs 200, 404 vs 400) communicates intent clearly to API clients.

The switch to Claude Code terminal is working well. Being able to ask questions during the session (like "what does line 45 mean?") without triggering code changes is helpful for learning.

Looking forward to completing the REST API tomorrow and then integrating WebSockets on top of this solid foundation. The architecture is becoming clearer: REST for basic operations, WebSockets for real-time updates.

Week 3 Day 4 complete! 🚀

---

## Week 3 Day 5 - Hybrid Architecture & Cleanup

**Date**: 2025-10-30
**Focus**: Complete REST API, add WebSocket integration, architectural cleanup

### What we built

1. **Completed REST API endpoints** (TDD)
   - GET /games/{game_id} - Get current game state
   - POST /games/{game_id}/start - Start game timer
   - POST /games/{game_id}/words - Submit word (later removed)
   - GET /games/{game_id}/results - Get final results with strike-outs
   - Total: 6 REST endpoints, 20 tests passing

2. **Added WebSocket support for real-time gameplay**
   - Created ConnectionManager for WebSocket client management
   - WS /ws/{game_id}/{player_id} endpoint
   - Real-time word submission with instant feedback
   - Broadcast word submissions to all players in game
   - Player connect/disconnect notifications
   - 4 WebSocket tests passing

3. **Architectural simplification** (CRITICAL LEARNING)
   - Identified code duplication: word submission in both REST and WebSocket
   - Decided on clean architecture: REST for CRUD, WebSocket for gameplay
   - Deleted REST word submission endpoint (POST /games/{id}/words)
   - Deleted entire src/network/ directory (old standalone WebSocket server)
   - Removed 1,401 lines of duplicate code!
   - Final: 5 REST + 1 WebSocket endpoint, 19 API tests, 84 total tests

### Key technical concepts

**Hybrid Architecture Pattern**:
- REST API: Stateless CRUD operations (create, join, start, get state, results)
- WebSocket: Stateful real-time gameplay (word submission, live updates)
- Single FastAPI server supporting both protocols
- Shared game state dictionary (single source of truth)
- Common pattern in production apps (Slack, Discord, multiplayer games)

**WebSocket Connection Management**:
- ConnectionManager class tracks active connections per game
- accept() → connect() → receive loop → disconnect()
- Broadcast messages to all clients in a game
- Graceful handling of disconnections
- Clean up disconnected clients automatically

**Architectural Decision Making**:
- Recognized duplication between REST and WebSocket word submission
- Questioned whether duplication was intentional
- Proposed clean separation of concerns
- Systematically removed all duplicate code
- This is professional engineering: question, clarify, simplify

### Challenges overcome

**None!** This session was smooth because:
1. TDD made adding endpoints predictable (RED → GREEN → REFACTOR)
2. FastAPI's WebSocket support is well-designed
3. We caught architectural issues early and fixed them
4. Having a clear plan made execution straightforward

### Mistakes and learnings

**Initial mistake**: Created duplicate word submission endpoints (REST + WebSocket)

**Why it happened**: Built REST API first (for learning), then added WebSockets, creating overlap

**How we fixed it**:
1. I spotted the duplication and questioned it
2. Decided on clean architecture: REST = CRUD, WebSocket = gameplay
3. Systematically deleted duplicate code
4. Removed entire old network/ directory
5. Result: -1,401 lines, zero duplication

**Lesson learned**: Always question duplication. If two parts of the code do the same thing, one should be deleted. Clean architecture has clear boundaries between components.

### Code statistics

**Before cleanup**:
- 6 REST endpoints + duplicate network code
- 24 API tests (20 REST + 4 WebSocket)
- src/network/ with 8 files
- Duplicate word submission logic

**After cleanup**:
- 5 REST endpoints + 1 WebSocket endpoint
- 19 API tests (15 REST + 4 WebSocket)
- No src/network/ directory
- Zero duplication
- **-1,401 lines deleted**

**Total tests**: 84 passing (65 game logic + 19 API)

### Next session

Week 5 starts next! According to learning plan:
1. Database (SQLite + SQLAlchemy)
2. Authentication (User registration/login with JWT)
3. Deployment (Render or Fly.io)

Before starting Week 5, need to verify we completed Week 3-4:
- ✓ REST API design and implementation
- ✓ WebSocket real-time gameplay
- ✓ Hybrid architecture
- ✓ Clean separation of concerns

### Time spent

~2.5 hours

### Reflection

**This was an excellent session!** Three key takeaways:

1. **Questioning is essential**: When I asked "is duplicate word submission by design?", we uncovered a real architectural issue. Never be afraid to question the design, even (especially!) when working with AI. Good engineers push back on bad designs.

2. **Clean architecture matters**: Having clear boundaries (REST = CRUD, WebSocket = gameplay) makes the codebase easier to understand and maintain. The -1,401 lines deleted is a feature, not a loss.

3. **TDD accelerates development**: Once I understood the RED-GREEN-REFACTOR cycle, adding 4 new REST endpoints was fast and confident. Tests document behavior and catch regressions.

4. **Hybrid architectures are powerful**: REST + WebSockets is a common real-world pattern. REST for stable CRUD operations, WebSockets for real-time features. Now I understand why apps like Slack use this pattern.

The learning plan is working great. Week 1-2 gave us solid game logic. Week 3-4 gave us client-server architecture. Week 5 will add persistence and deployment. The incremental approach (CLI → REST → WebSocket → Database → Deploy) makes complex concepts manageable.

Looking forward to Week 5 and getting this deployed to the cloud!

Week 3 Day 5 complete! 🚀

---

## Week 5 Day 1 - Database Fundamentals & SQLAlchemy

**Date**: 2025-10-30
**Focus**: Learn databases from scratch, set up SQLAlchemy, create User model with UUIDs

### What we built

1. **Database setup** (`src/database.py`)
   - SQLAlchemy engine and session management
   - Database URL configuration (SQLite)
   - Base class for all models
   - `get_db()` helper function with proper cleanup

2. **User model with UUID security** (`src/models.py`)
   - UUID primary key instead of auto-increment integers
   - username (unique, max 50 chars)
   - email (unique, max 100 chars)
   - password_hash (will implement hashing in Part 2)
   - created_at timestamp (auto-generated)

3. **Database initialization** (`src/init_db.py`)
   - Script to create all tables
   - Safe to run multiple times
   - Shows generated SQL with echo=True

4. **Comprehensive tests** (`tests/test_database.py`)
   - Test fixture for database sessions
   - Create user test (UUID auto-generation)
   - Retrieve user test
   - Unique username constraint test
   - Unique email constraint test
   - UUID randomness verification

### Key technical concepts learned

**Database Fundamentals:**
- **Database vs Memory**: RAM is fast but volatile, databases persist to disk
- **SQL**: Structured Query Language for talking to databases (CREATE, INSERT, SELECT, UPDATE, DELETE)
- **Tables**: Like spreadsheets with rows and columns
- **Primary Key**: Unique identifier for each row
- **Constraints**: UNIQUE, NOT NULL, etc.

**ORMs (Object-Relational Mapping):**
- Translates Python objects ↔ SQL automatically
- Write Python code instead of SQL strings
- SQLAlchemy is the most powerful Python ORM
- Type-safe with Mapped[] annotations

**Migrations:**
- Scripts that change database structure over time
- Like git for your database schema
- Can upgrade (add columns) or downgrade (remove columns)
- Track database changes incrementally

**SQLite vs PostgreSQL:**
- SQLite: File-based, perfect for learning, no server needed
- PostgreSQL: Production-grade, requires server setup
- We use SQLite for simplicity

**Sessions:**
- A "workspace" for database operations
- Open session → do work → commit → close session
- Like a transaction in traditional databases

**Pytest Fixtures:**
- Setup/teardown automation for tests
- Dependency injection pattern
- Each test gets fresh, isolated database
- `yield` allows cleanup after test runs
- Scope controls when fixture runs (function/module/session)

### Critical architectural decision: UUID vs Auto-increment IDs

**Problem identified**: Auto-increment IDs (1, 2, 3...) are a security risk
- Enumeration attacks: Attacker can guess all user IDs
- Information leakage: IDs reveal user count and join order
- Easy to scrape: Loop through /users/1, /users/2, etc.

**Solution chosen**: UUID primary keys
- Format: `550e8400-e29b-41d4-a716-446655440000`
- Random, not guessable
- Industry standard (Stripe, Auth0, GitHub)
- 36 characters vs 4 bytes (tradeoff: size for security)

**Implementation**:
```python
id: Mapped[str] = mapped_column(
    String(36),
    primary_key=True,
    default=lambda: str(uuid.uuid4())
)
```

This was Amritansh's question - excellent security awareness!

### Challenges overcome

**None!** The session was designed for slow, concept-first learning:
1. Explained every concept before coding
2. Wrote heavily commented code
3. Ran init_db to see SQL generation
4. Tests verified everything works
5. Amritansh asked great questions about security

### Mistakes and learnings

**Initial plan**: Use auto-increment integers (simpler)

**Amritansh's insight**: "Can IDs be guessable? Is that a security risk?"

**Correct answer**: YES! Changed to UUIDs immediately.

**Lesson learned**: Always question security implications. Auto-increment IDs are convenient but expose information. UUIDs are the professional choice for public APIs.

### Code statistics

**New files created:**
- `src/database.py` - 55 lines (database setup)
- `src/models.py` - 62 lines (User model)
- `src/init_db.py` - 20 lines (initialization script)
- `tests/test_database.py` - 155 lines (5 comprehensive tests)

**Total tests**: 89 passing (84 game + 5 database)

**Database file**: `game.db` (20KB, contains users table)

### Concepts explained

**What is a database?**
- Whiteboard (RAM) vs Filing Cabinet (Database)
- Persistent storage that survives server restarts

**What is SQL?**
- Language for databases (like English for humans)
- CREATE TABLE, INSERT, SELECT, UPDATE, DELETE

**What is an ORM?**
- Python objects → SQL translator
- Write `user = User(...)` instead of SQL strings
- Type-safe with modern Python

**What are migrations?**
- Git for database schema
- Track changes over time
- Can rollback if needed

**What are fixtures?**
- Setup/teardown automation
- Dependency injection
- Test isolation (each test gets fresh database)

### Next session

Continue Week 5 Part 1:
1. Add Game model (stores game state)
2. Add GamePlayer model (links users to games)
3. Learn about relationships (foreign keys, one-to-many)
4. Test the relationships

Then Week 5 Part 2:
- Password hashing with bcrypt
- User registration endpoint
- User login endpoint
- JWT tokens for authentication

### Time spent

~3 hours (slow, concept-focused learning)

### Reflection

**Excellent first day with databases!** Three key takeaways:

1. **Concept-first teaching worked perfectly**: By explaining databases, SQL, ORMs, and migrations BEFORE writing code, everything made sense. Amritansh understood WHY we're doing each step, not just HOW.

2. **Security mindset is strong**: The question about auto-increment IDs being guessable shows real engineering thinking. Most tutorials skip this and use integers. We chose the professional approach (UUIDs) from day one.

3. **ORMs are magical but understandable**: SQLAlchemy translates Python classes into SQL CREATE TABLE statements automatically. Seeing the generated SQL with `echo=True` helped demystify the "magic."

4. **Fixtures are powerful**: The `@pytest.fixture` pattern for database sessions ensures test isolation. Each test gets a fresh, empty database. This prevents tests from interfering with each other.

The learning plan is working. Week 1-2 gave us game logic. Week 3-4 gave us APIs and WebSockets. Week 5 is giving us persistence and authentication. The building blocks are coming together.

Database concepts (tables, constraints, sessions, ORMs) are transferable to any backend framework. This foundation applies to Django, Rails, Node.js, Go, etc. Amritansh now understands databases at a fundamental level.

Looking forward to adding relationships tomorrow and then authentication!

Week 5 Day 1 complete! 🚀

---

## 2025-10-31: Week 5, Day 2 - Database Relationships (One-to-Many & Many-to-Many)

### What we did

**Completed database relationships with TDD:**
1. Added `Game` model with one-to-many relationship to User (creator)
2. Added `GamePlayer` join table for many-to-many User↔Game relationships
3. Enabled foreign key constraints for SQLite (not enabled by default!)
4. Wrote 11 comprehensive tests covering relationships and CRUD
5. All 100 tests passing, type checking clean
6. Merged feature branch into main and pushed to remote

**Key accomplishments:**
- Learned dependency injection pattern (how pytest fixtures work)
- Understood the three relationship types (1:1, 1:many, many:many)
- Implemented cascade deletes (delete game → delete all GamePlayer records)
- Used `Text` type for JSON storage (board_state, words_found)
- Made nullable columns optional with proper type hints

### What I learned

**Database Relationships:**
- **One-to-Many**: One user creates many games (`Game.creator_id` → `User.id`)
- **Many-to-Many**: Many users play many games (via `GamePlayer` join table)
- **Join Tables**: Intermediate tables that connect two other tables
- **Foreign Keys**: Columns that reference another table's primary key
- **Referential Integrity**: Database prevents invalid references (can't create game with fake user_id)

**SQLAlchemy Relationships:**
- `relationship()` doesn't create columns, it tells SQLAlchemy how to JOIN
- `back_populates` creates bidirectional navigation (user.created_games ↔ game.creator)
- `cascade="all, delete-orphan"` for automatic cleanup
- `foreign_keys` parameter disambiguates multiple relationships to same table

**Dependency Injection:**
- Give components what they need from outside (don't create internally)
- Makes testing easy (inject mocks instead of real implementations)
- pytest fixtures are a dependency injection framework
- Test declares what it needs → pytest injects it automatically

**SQLite Quirks:**
- Foreign keys disabled by default (must use `PRAGMA foreign_keys=ON`)
- Applied via `@event.listens_for(engine, "connect")` hook
- Needed in both production (database.py) and tests (test fixture)

### Challenges/Issues

**1. Foreign key test initially failed**
- SQLite doesn't enforce foreign keys by default
- Fixed by enabling `PRAGMA foreign_keys=ON` in both database.py and test fixture

**2. Type annotations for database functions**
- `get_db()` needed return type: `Generator[Session, None, None]`
- `set_sqlite_pragma()` parameters needed `Any` type (low-level DBAPI objects)

### Key Commands Learned

```bash
python -m src.init_db              # Initialize database (create tables)
pytest tests/test_database.py -v   # Run database tests
mypy src/                          # Type check source code
git merge feature/branch --no-ff   # Merge with explicit merge commit
git branch -d feature/branch       # Delete merged branch
```

### Code added

**src/models.py:**
- `Game` model (118 lines):
  - UUID primary key
  - Foreign key to User (creator_id)
  - Status, board_size, time_limit, board_state
  - created_at, started_at, ended_at timestamps
  - Relationships to User and GamePlayer

- `GamePlayer` model (83 lines):
  - UUID primary key
  - Foreign keys to both Game and User
  - score, words_found (JSON), joined_at
  - Relationships to Game and User

**tests/test_database.py:**
- 11 new tests (313 lines):
  - test_create_game
  - test_game_creator_relationship
  - test_game_foreign_key_constraint
  - test_retrieve_game_by_id
  - test_update_game_status
  - test_add_player_to_game
  - test_multiple_players_in_game
  - test_gameplayer_relationships
  - test_user_can_join_multiple_games
  - test_update_player_score_and_words
  - test_cascade_delete_game_players

**Total tests**: 100 passing (16 database, 84 game/API/WebSocket)

### Database schema

```
users (id UUID PK, username, email, password_hash, created_at)
  ↓ one-to-many (creator)
games (id UUID PK, creator_id FK→users, status, board_size, time_limit,
       board_state TEXT, created_at, started_at, ended_at)
  ↓ one-to-many
game_players (id UUID PK, game_id FK→games, user_id FK→users,
              score, words_found TEXT, joined_at)
```

**Relationships:**
- `user.created_games` → list of games created by user
- `game.creator` → User who created the game
- `game.players` → list of GamePlayer records for this game
- `game_player.game` → the Game this player is in
- `game_player.user` → the User who is playing

### Example usage

```python
# Create user and game
user = User(username="alice", email="alice@example.com", password_hash="hashed")
db.add(user)
db.commit()

game = Game(creator_id=user.id, board_size=4)
db.add(game)
db.commit()

# Add player to game
game_player = GamePlayer(game_id=game.id, user_id=user.id, score=0)
db.add(game_player)
db.commit()

# Navigate relationships
print(game.creator.username)  # "alice"
print(len(game.players))      # 1
print(user.created_games[0].id == game.id)  # True

# Update player score
game_player.score = 42
game_player.words_found = json.dumps(["CAT", "DOG", "HOUSE"])
db.commit()
```

### Dependency injection example

```python
# WITHOUT dependency injection (BAD)
def test_create_user():
    # Test creates its own database - duplicated setup code
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    # ... do test ...
    session.close()

# WITH dependency injection (GOOD)
@pytest.fixture
def db_session():
    # Fixture creates database once
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session  # INJECT into test
    session.close()

def test_create_user(db_session):  # Dependency INJECTED by pytest
    # Test just uses the database, doesn't create it
    user = User(username="alice")
    db_session.add(user)
    db_session.commit()
```

### Blockers/Questions

None! Everything working smoothly.

### Next session

**Week 5 Part 2: Authentication** (user registration, login, JWT tokens)

1. Install authentication libraries: `uv add bcrypt python-jose[cryptography] passlib[bcrypt]`
2. Implement password hashing (never store plain passwords!)
3. Create POST /auth/register endpoint
4. Create POST /auth/login endpoint (returns JWT token)
5. Create JWT token generation/validation
6. Protect endpoints with authentication
7. Test all auth flows

### Time spent

~2 hours (includes dependency injection explanation, TDD workflow, git merge)

### Reflection

**Excellent progress on database fundamentals!** Key takeaways:

1. **TDD worked perfectly**: Wrote tests first, saw them pass with minimal code. The test for foreign key constraints caught the SQLite quirk immediately.

2. **Relationships are powerful**: Being able to navigate `game.creator.username` or `user.created_games` makes code readable and maintainable. SQLAlchemy handles all the JOINs automatically.

3. **Dependency injection demystified**: The explanation of how pytest fixtures implement DI pattern was a breakthrough. Now it's clear WHY fixtures are valuable (not just HOW to use them).

4. **Type safety matters**: mypy caught missing type annotations. The discipline of typing everything pays off in fewer runtime errors.

5. **Git workflow smooth**: Feature branch → merge → push. Clean history with conventional commits.

The database foundation is now complete:
- ✅ User accounts (Week 5 Day 1)
- ✅ Game instances (Week 5 Day 2)
- ✅ Player participation (Week 5 Day 2)
- ⏳ Authentication (Week 5 Day 3)

Next step is securing the API with authentication. Users will register, login, and get JWT tokens. The database models are ready - we just need the auth endpoints!

Week 5 Day 2 complete! 🚀

---
