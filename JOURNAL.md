Lots of initialization today
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
