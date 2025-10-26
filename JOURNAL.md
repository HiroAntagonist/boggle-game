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
I didnt realize that gh repo create created a commit so the commits collided. I think the right flow is to do a pull after a repo create

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
2025-01-XX: Week 1, Day 2 - First TDD Cycle
What we did

Created project structure (src/, tests/ directories)
Wrote first failing tests for Board class (RED phase)
Implemented Board class with type hints (GREEN phase)
All tests passing with pytest
Type checking passing with mypy
Used feature branch workflow
Merged to main and pushed to GitHub

What I learned

TDD red-green-refactor cycle in practice
Python has no char type - everything is str
Type hints: List[List[str]] for 2D grid
pytest discovers and runs tests automatically
Feature branch workflow: create branch, commit, merge, delete
Python random module for shuffling dice
Private methods convention: _generate_grid()

Challenges/Issues

None! Everything worked smoothly

Key Commands Learned
bashgit checkout -b feature/branch-name  # Create and switch to new branch
pytest tests/test_board.py -v        # Run specific test file with verbose output
mypy src/                            # Type check source code
git merge feature/branch-name        # Merge feature branch into current branch
git branch -d branch-name            # Delete local branch
Code Concepts

Type hints for function signatures: def __init__(self, size: int) -> None:
List comprehensions: [random.choice(die) for die in dice]
Raising exceptions: raise ValueError(f"...")
2D list slicing: letters[i * 4:(i + 1) * 4]

Blockers/Questions

Understood the difference between C's char vs Python's str

Next session

Day 3: Word Path Validation
Implement depth-first search (DFS) for finding words on board
Test adjacency logic (including diagonals)
Learn about more complex type hints (Tuple, Set)

Time spent
~45 minutes
Reflection
First real code! TDD feels different from how I used to code - writing the test first seemed backwards at first, but I can see how it forces you to think about the interface before implementation. The test failure → implementation → test pass cycle is satisfying. Python's type hints are lighter than C's strict typing, but mypy catches issues. The List[List[str]] type hint clearly documents the 2D grid structure.
---
