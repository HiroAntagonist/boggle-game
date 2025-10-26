# Multiplayer Boggle: 10-Week Learning Plan

**Student**: Amritansh  
**Mentor**: Claude  
**Goal**: Return to coding by building a real-time multiplayer Boggle game, progressing from Python CLI to iOS app  
**Timeline**: 10 weeks (~7-10 hours/week)  
**Approach**: TDD, incremental feature addition, deep understanding over speed

---

## Technology Stack

### Core Languages & Frameworks
- **Backend**: Python 3.11+, FastAPI, WebSockets
- **Package Management**: uv (modern, fast Python package manager)
- **Type Safety**: Python type hints, Pydantic, mypy, Pylance
- **Frontend**: Swift 5.9+, SwiftUI
- **Database**: SQLite
- **Testing**: pytest (Python), XCTest (Swift)
- **Tools**: VSCode, Claude Code, Git/GitHub

### Key Learning Areas
- Modern Python (type hints, async/await, Pydantic)
- TDD methodology and pytest
- REST APIs and WebSockets
- Git workflow (branching, committing, squashing, rebasing)
- iOS development (Swift, SwiftUI, networking)
- Cloud deployment (Render/Fly.io)

---

## Overall Project Phases

1. **Weeks 1-2**: Python CLI single-player → local multiplayer
2. **Weeks 3-5**: Client-server architecture, real-time networking, cloud deployment
3. **Weeks 6-10**: iOS app development and multiplayer integration

---

## Week 1: Foundation & Single-Player CLI

**Time**: 5-7 hours  
**Goal**: Set up development environment and build a working single-player Boggle CLI with TDD

### Learning Objectives
- VSCode setup and essential extensions
- Git basics: init, add, commit, status, log
- Python type hints and Pylance
- pytest fundamentals
- TDD red-green-refactor cycle

### Deliverables
1. ✅ Development environment fully configured
2. ✅ Git repo initialized with proper .gitignore
3. ✅ Single-player CLI Boggle that:
   - Generates a random 4x4 board
   - Accepts player word submissions
   - Validates words exist on board (path-finding)
   - Validates words against dictionary
   - Calculates Fibonacci scoring
   - All features test-driven

### Detailed Tasks

#### Day 1 (45 min): Environment Setup
**Git workflow**: Initialize repo, connect to GitHub, first commit

**Tasks**:
1. **Install VSCode extensions**:
   - Pylance (Microsoft)
   - Python (Microsoft)
   - Python Test Explorer
   - GitLens
   - Error Lens

2. **Authenticate GitHub CLI** (one-time setup):
   ```bash
   gh auth login
   # Choose: GitHub.com
   # Choose: HTTPS or SSH (recommend HTTPS for simplicity)
   # Choose: Login with a web browser
   # Follow the prompts
   ```

3. **Create project directory and initialize git**:
   ```bash
   mkdir boggle-game
   cd boggle-game
   git init
   git branch -M main
   ```

4. **Create initial files**:
   - `.gitignore` (Python template - we'll create this together)
   - `README.md` (project description)
   - `JOURNAL.md` (your learning journal)
   - `LEARNING_PLAN.md` (copy the plan we created)

5. **Create private GitHub repo and connect**:
   ```bash
   gh repo create boggle-game --private --source=. --remote=origin
   ```

6. **First commit and push**:
   ```bash
   git add .
   git commit -m "Initial commit: project structure"
   git push -u origin main
   ```

7. **Install uv** (modern Python package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Restart terminal or source your shell config
   ```

8. **Initialize Python project with uv**:
   ```bash
   uv init --no-readme  # We already created README.md
   uv venv
   source .venv/bin/activate.fish  # for fish shell
   ```

9. **Install initial dependencies**:
   ```bash
   uv add --dev pytest pytest-watch mypy
   ```

10. **Configure mypy**: create `mypy.ini` with basic settings

11. **Set up VSCode settings**: create `.vscode/settings.json`

12. **Commit Python setup**:
    ```bash
    git add .
    git commit -m "chore: configure Python environment and tooling"
    git push
    ```

13. **First journal entry!** Write in JOURNAL.md about what you learned today, then:
    ```bash
    git add JOURNAL.md
    git commit -m "docs: add first journal entry"
    git push
    ```

**Learning focus**: 
- VSCode navigation (Cmd+P, Cmd+Shift+P)
- GitHub CLI (gh) for repo management
- Git fundamentals (init, add, commit, push)
- uv for fast, modern Python package management
- Remote repositories and backup

**Git commits**: ~3 commits (all pushed to GitHub)
- "Initial commit: project structure"
- "chore: configure Python environment and tooling"
- "docs: add first journal entry"

**Verification checklist**:
- ✅ Can see your repo at `https://github.com/yourusername/boggle-game`
- ✅ Repo is marked as private
- ✅ All commits visible on GitHub
- ✅ VSCode has Python extensions working
- ✅ `uv` command works in terminal
- ✅ Virtual environment activates successfully

---

#### Day 2 (45 min): First TDD Cycle - Board Generation
**Git workflow**: Create feature branch
```bash
git checkout -b feature/board-generation
```

**TDD Cycle**:
1. Write failing test: `tests/test_board.py`
   ```python
   def test_board_generates_4x4_grid():
       board = Board(size=4)
       assert board.size == 4
       assert len(board.grid) == 4
       assert all(len(row) == 4 for row in board.grid)
   ```
2. Run test: `pytest` → RED ❌
3. Write minimal code to pass: `src/board.py`
4. Run test: `pytest` → GREEN ✅
5. Refactor if needed

**Tasks**:
- Create `src/board.py` with `Board` class
- Create `tests/test_board.py`
- Implement board generation with configurable size (4x4 or 5x5)
- Use standard Boggle dice distribution
- Add type hints to all functions

**Learning focus**:
- TDD red-green-refactor cycle
- Python type hints (List[List[str]])
- pytest basics

**Git commits**: ~2-3 commits
- "test: add failing test for board generation"
- "feat: implement Board class with size configuration"
- "refactor: improve board initialization"

---

#### Day 3 (Weekend - 90 min): Word Path Validation
**Git workflow**: Continue on feature branch or new branch

**TDD Cycles**:
1. Test: Word exists on board (simple case: "CAT")
2. Test: Word follows valid path (adjacent letters)
3. Test: Word cannot reuse same cell
4. Test: Diagonal adjacency works
5. Test: Word not on board returns False

**Tasks**:
- Implement depth-first search (DFS) for path-finding
- Handle 8-directional adjacency (including diagonals)
- Create helper function to get adjacent cells
- Write comprehensive tests for edge cases

**Learning focus**:
- Algorithm implementation (DFS)
- Complex type hints (Tuple[int, int], Set, etc.)
- Test-driven algorithm development
- Parametrized tests in pytest

**Git commits**: ~4-5 commits
- "test: add failing tests for word path validation"
- "feat: implement DFS path-finding algorithm"
- "test: add edge cases for path validation"
- "refactor: extract adjacency helper function"

---

#### Day 4 (45 min): Dictionary Validation
**TDD Cycle**:
1. Test: Load dictionary file
2. Test: Valid word returns True
3. Test: Invalid word returns False
4. Test: Case-insensitive validation

**Tasks**:
- Download SOWPODS word list (or similar)
- Create `Dictionary` class
- Implement efficient word lookup (set-based)
- Handle case normalization

**Learning focus**:
- File I/O in Python
- Set data structures for O(1) lookup
- Test fixtures in pytest

**Git commits**: ~2-3 commits
- "chore: add SOWPODS dictionary file"
- "test: add dictionary validation tests"
- "feat: implement Dictionary class with word lookup"

---

#### Day 5 (45 min): Scoring System
**TDD Cycle**:
1. Test: 3-letter word scores 1
2. Test: 4-letter word scores 2
3. Test: Fibonacci progression (5→3, 6→5, 7→8, etc.)
4. Test: Configurable minimum word length

**Tasks**:
- Create `Scorer` class
- Implement Fibonacci scoring
- Make minimum word length configurable
- Validate words meet minimum length

**Learning focus**:
- Simple algorithms
- Configuration management
- More pytest practice

**Git commits**: ~2 commits
- "test: add scoring system tests"
- "feat: implement Fibonacci scoring with configurable minimum"

---

#### Day 6 (Weekend - 90 min): CLI Interface & Integration
**TDD for game flow**:
1. Test: Game initializes with board
2. Test: Game accepts word submissions
3. Test: Game ends after time limit (we'll mock time for now)
4. Test: Game calculates final score

**Tasks**:
- Create `Game` class that orchestrates everything
- Build simple CLI interface (input/output)
- Integrate Board, Dictionary, Scorer
- Display board nicely in terminal
- Accept word input
- Show results

**Learning focus**:
- Integration vs unit tests
- Dependency injection
- Python CLI basics
- Mocking in tests (for time)

**Git commits**: ~3-4 commits
- "test: add game orchestration tests"
- "feat: implement Game class"
- "feat: add CLI interface for single player"
- "docs: update README with usage instructions"

**Merge to main**:
```bash
git checkout main
git merge feature/board-generation
git push origin main  # Don't forget to push!
```

**Note**: From now on, after every local commit, remember to `git push` to back up to GitHub. It'll become second nature!

---

### Week 1 Checkpoint

**Before moving to Week 2, verify**:
- ✅ All tests pass (`pytest`)
- ✅ Type checking passes (`mypy src/`)
- ✅ Can play a complete single-player game from CLI
- ✅ Code is committed with clear messages
- ✅ JOURNAL.md has entries for each session
- ✅ You understand every line of code

**Reflection Questions**:
1. How comfortable are you with the TDD cycle?
2. Are the Git commits feeling natural or forced?
3. Is the pacing too fast/slow?
4. What was the hardest concept this week?

**Adjust plan if needed**: If Week 1 took longer, that's fine! We'll adjust Week 2 accordingly.

---

## Week 2: Local Multiplayer & Word Validation

**Time**: 5-7 hours  
**Goal**: Support multiple players on same machine, implement word validation rules, add game configuration

### Learning Objectives
- Managing multiple players in game state
- More complex test scenarios
- Configuration management (Pydantic)
- Git branching strategies
- More advanced pytest features (fixtures, parametrize)

### Deliverables
1. ✅ Local multiplayer (2-4 players)
2. ✅ Word submission and strike-out logic (duplicate words across players)
3. ✅ Configurable game options (board size, time limit, min word length)
4. ✅ Enhanced CLI interface
5. ✅ Comprehensive test coverage

### Detailed Tasks

#### Day 1 (45 min): Game Configuration with Pydantic
**Git workflow**: New feature branch
```bash
git checkout -b feature/game-configuration
```

**TDD Cycle**:
1. Test: GameConfig with default values
2. Test: GameConfig with custom values
3. Test: GameConfig validation (e.g., size must be 4 or 5)

**Tasks**:
- Install Pydantic: `uv add pydantic`
- Create `GameConfig` model with:
  - `board_size: int` (4 or 5)
  - `time_limit_seconds: int` (default 180)
  - `min_word_length: int` (default 3)
  - `max_players: int` (default 4)
- Add validation rules
- Update `Game` class to accept config

**Learning focus**:
- Pydantic models for data validation
- Configuration best practices
- Python dataclasses vs Pydantic

**Git commits**: ~2-3 commits

---

#### Day 2 (45 min): Multi-Player Game State
**TDD Cycle**:
1. Test: Game supports multiple players
2. Test: Each player has their own word list
3. Test: Players cannot submit duplicate words (in their own list)

**Tasks**:
- Create `Player` class (id, name, words, score)
- Update `Game` to manage list of players
- Refactor to support multiple player submissions
- Add player registration/setup phase

**Learning focus**:
- Managing collections of objects
- More complex game state
- Type hints for complex structures (Dict[str, Player])

**Git commits**: ~3 commits

---

#### Day 3 (Weekend - 90 min): Word Strike-Out Logic
**TDD Cycle**:
1. Test: Duplicate words across players are removed
2. Test: Unique words are kept
3. Test: Scoring only counts non-struck words
4. Test: Edge case - all players have same word

**Tasks**:
- Implement word comparison across all players
- Create strike-out algorithm
- Update scoring to only count valid, unique words
- Display struck-out words differently in results

**Learning focus**:
- Set operations (intersection, difference)
- Complex game logic
- Clear test naming for complex scenarios

**Git commits**: ~3-4 commits

---

#### Day 4 (45 min): Enhanced CLI for Multiplayer
**Tasks**:
- Update CLI to support player registration
- Show whose turn it is
- Display all player scores at end
- Show which words were struck out and why
- Improve board display

**Learning focus**:
- CLI user experience
- String formatting in Python
- Iterating over collections

**Git commits**: ~2 commits

---

#### Day 5 (45 min): Timer Implementation
**TDD Cycle**:
1. Test: Game tracks elapsed time
2. Test: Game prevents word submission after time limit
3. Test: Timer can be paused/resumed (for future use)

**Tasks**:
- Implement actual timer (not mocked)
- Add countdown display in CLI
- Handle timer expiration gracefully

**Learning focus**:
- Python `time` module
- Threading or async for timer (simple version)
- Testing time-dependent code

**Git commits**: ~2-3 commits

---

#### Day 6 (Weekend - 90 min): Polish & Edge Cases
**Tasks**:
- Write tests for edge cases:
  - Empty word submissions
  - Words with invalid characters
  - Extremely long words
  - Single player game
  - Maximum players (4)
- Add input validation
- Improve error messages
- Update documentation
- Final refactoring pass

**Learning focus**:
- Comprehensive testing
- Error handling
- Code cleanup

**Git commits**: ~4-5 commits
- Multiple feature/fix commits
- "docs: update README with multiplayer instructions"
- Merge to main

---

### Week 2 Checkpoint

**Verify**:
- ✅ Can play full 4-player game locally
- ✅ Word strike-out works correctly
- ✅ All configuration options work
- ✅ Test coverage is comprehensive
- ✅ Code is clean and well-organized
- ✅ Git history is clear and meaningful

**Git Skills Check**:
- Comfortable with branches?
- Want to learn about `git log --oneline --graph`?
- Ready to learn about amending commits?

---

## Week 3: Client-Server Architecture

**Time**: 6-8 hours  
**Goal**: Split the game into client (CLI) and server (FastAPI), design REST API

### Learning Objectives
- REST API design principles
- FastAPI basics
- HTTP methods and status codes
- API testing
- Separation of concerns (client vs server)
- Running multiple processes

### Deliverables
1. ✅ FastAPI server with game endpoints
2. ✅ Refactored CLI client that calls API
3. ✅ API tests using pytest and FastAPI TestClient
4. ✅ Documentation (API endpoints)
5. ✅ Both client and server run independently

### High-Level Tasks

#### Part 1: API Design (Day 1-2)
- Design REST API endpoints:
  - `POST /games` - Create new game
  - `GET /games/{game_id}` - Get game state
  - `POST /games/{game_id}/players` - Join game
  - `POST /games/{game_id}/words` - Submit word
  - `GET /games/{game_id}/results` - Get final results
- Create API request/response models with Pydantic
- Set up FastAPI project structure

**Git**: New branch `feature/api-server`

---

#### Part 2: FastAPI Implementation (Day 3-4)
- Install FastAPI and uvicorn: `uv add fastapi uvicorn[standard]`
- Implement endpoints with TDD
- Add in-memory game state storage (dict)
- Handle concurrent access (basic locking)
- Add proper error responses

**Learning**: FastAPI decorators, async/await basics, HTTP status codes

---

#### Part 3: Refactor CLI Client (Day 5-6)
- Extract game logic into shared library
- CLI becomes thin client
- Install and use `httpx` library to call API: `uv add httpx`
- Handle network errors gracefully
- Update tests (separate client tests from server tests)

**Learning**: HTTP clients, error handling, project structure

**Note**: We're using `httpx` instead of `requests` - it's more modern and supports async/await

---

### Week 3 Checkpoint
- ✅ Server runs independently: `uvicorn main:app`
- ✅ Client connects to server successfully
- ✅ Can play multiplayer game via API
- ✅ Tests pass for both client and server
- ✅ API documentation auto-generated (FastAPI's `/docs`)

**Question**: Ready for real-time WebSockets, or need more time with REST APIs?

---

## Week 4: Real-Time Multiplayer with WebSockets

**Time**: 6-8 hours  
**Goal**: Add WebSockets for real-time game updates, handle concurrent players

### Learning Objectives
- WebSocket protocol basics
- FastAPI WebSocket support
- Async/await in Python
- Broadcasting to multiple clients
- Connection management

### Deliverables
1. ✅ WebSocket endpoints for real-time updates
2. ✅ Game lobby (players can see when others join)
3. ✅ Live game timer visible to all players
4. ✅ Automatic game state synchronization
5. ✅ Graceful disconnect handling

### High-Level Tasks

#### Part 1: WebSocket Basics (Day 1-2)
- Add WebSocket endpoint to FastAPI
- Implement connection manager
- Test basic message sending
- Handle player connections/disconnections

---

#### Part 2: Game Lobby (Day 3-4)
- Players can create/join lobbies
- Show who's in the lobby
- Game starts when all players ready
- Broadcast lobby updates to all players

---

#### Part 3: Live Game Updates (Day 5-6)
- Broadcast timer updates
- Show when game starts/ends
- Synchronize game state
- Handle edge cases (disconnects during game)

---

### Week 4 Checkpoint
- ✅ Multiple clients can connect simultaneously
- ✅ Real-time updates work smoothly
- ✅ Game flow feels responsive
- ✅ Disconnects are handled gracefully

**Reflection**: This is complex! Don't rush. Real-time systems have lots of edge cases.

---

## Week 5: Database, Authentication & Deployment

**Time**: 6-8 hours  
**Goal**: Add persistent storage, user authentication, deploy to cloud

### Learning Objectives
- SQLite with SQLAlchemy
- User authentication (hashing passwords)
- Database migrations
- Environment variables and secrets
- Cloud deployment (Render or Fly.io)
- Production vs development configuration

### Deliverables
1. ✅ User registration and login
2. ✅ Persistent game history
3. ✅ Player statistics
4. ✅ Server deployed to cloud
5. ✅ CLI can connect to remote server

### High-Level Tasks

#### Part 1: Database & Models (Day 1-2)
- Install database libraries: `uv add sqlalchemy alembic`
- Set up SQLAlchemy
- Create User, Game, GamePlayer models
- Implement migrations (Alembic)
- Write database tests

---

#### Part 2: Authentication (Day 3-4)
- Install auth libraries: `uv add bcrypt python-jose[cryptography] passlib[bcrypt]`
- Hash passwords with bcrypt
- Create login/register endpoints
- JWT tokens for session management
- Protected endpoints

---

#### Part 3: Deployment (Day 5-6)
- Choose Render or Fly.io
- Configure environment variables
- Set up database in production
- Deploy server
- Update CLI to support remote URL
- Test end-to-end

---

### Week 5 Checkpoint
- ✅ Users can register and login
- ✅ Games are saved to database
- ✅ Server is running in the cloud
- ✅ CLI works with both local and remote server
- ✅ Production deployment is stable

**Major Milestone**: You now have a fully functional, deployed multiplayer game backend! 🎉

---

## Week 6: iOS Basics & SwiftUI Introduction

**Time**: 6-8 hours  
**Goal**: Learn Swift fundamentals and create first SwiftUI app

### Learning Objectives
- Swift syntax and basics
- SwiftUI view hierarchy
- State management (@State, @Binding)
- Xcode navigation
- iOS Simulator

### Deliverables
1. ✅ Simple "Hello World" SwiftUI app
2. ✅ Understanding of Swift types (like your C/Go knowledge)
3. ✅ Basic SwiftUI layouts
4. ✅ Simple interactive components
5. ✅ Comfortable with Xcode

### High-Level Tasks

#### Part 1: Swift Fundamentals (Day 1-2)
- Swift types (Int, String, Bool, etc.)
- Optionals (similar to Go's nil)
- Collections (Array, Dictionary, Set)
- Functions and closures
- Structs vs Classes
- Write simple Swift playground exercises

**Learning**: Swift is strongly typed like C/Go but more modern

---

#### Part 2: SwiftUI Basics (Day 3-4)
- Create new Xcode project
- Understand View protocol
- Basic views: Text, Image, Button, VStack, HStack
- Modifiers
- Preview system
- Simple @State for button clicks

---

#### Part 3: Practice App (Day 5-6)
- Build simple counter app
- Or to-do list app
- Focus on understanding SwiftUI patterns
- Get comfortable with Xcode

---

### Week 6 Checkpoint
- ✅ Comfortable navigating Xcode
- ✅ Can create and modify SwiftUI views
- ✅ Understand @State and data flow
- ✅ Can run app in simulator
- ✅ Swift syntax feels familiar

**Note**: iOS is very different from CLI! Take time to understand SwiftUI's declarative approach.

---

## Week 7: Boggle Board in SwiftUI

**Time**: 7-9 hours  
**Goal**: Create Boggle game UI - board display and word input

### Learning Objectives
- SwiftUI Grid layouts
- Custom views and view composition
- User input handling
- View models (MVVM pattern)
- More complex state management

### Deliverables
1. ✅ Boggle board display (4x4 or 5x5 grid)
2. ✅ Letter tiles with proper styling
3. ✅ Word input field
4. ✅ Submit button
5. ✅ Word list display
6. ✅ Timer display
7. ✅ Local game logic (reuse Python logic concepts)

### High-Level Tasks

#### Part 1: Board Display (Day 1-2)
- Create LazyVGrid for board
- Style letter tiles
- Make it responsive to different screen sizes
- Add animations (tiles appearing)

---

#### Part 2: Input & Interaction (Day 3-4)
- Text field for word input
- Submit button
- Display submitted words
- Clear input after submission
- Basic validation

---

#### Part 3: Game Logic in Swift (Day 5-7)
- Port core game logic to Swift
- Board generation
- Word validation (path finding)
- Scoring
- Timer
- TDD with XCTest!

---

### Week 7 Checkpoint
- ✅ Can play single-player Boggle on iOS (local only)
- ✅ UI looks good and feels responsive
- ✅ Game logic works correctly
- ✅ Tests pass

**Reflection**: How does Swift compare to Python for game logic?

---

## Week 8: iOS Networking

**Time**: 7-9 hours  
**Goal**: Connect iOS app to your deployed backend

### Learning Objectives
- URLSession for HTTP requests
- Async/await in Swift
- JSON encoding/decoding (Codable)
- Error handling in Swift
- WebSocket client in Swift
- State management for network data (@Published, ObservableObject)

### Deliverables
1. ✅ API client for backend
2. ✅ User login/registration screens
3. ✅ Game lobby (create/join games)
4. ✅ WebSocket connection for real-time updates
5. ✅ Network error handling

### High-Level Tasks

#### Part 1: HTTP Networking (Day 1-3)
- Create API client class
- Implement login/register
- Handle JWT tokens
- Error handling
- Loading states in UI

---

#### Part 2: WebSocket Integration (Day 4-6)
- WebSocket client for real-time updates
- Connect to game lobby
- Receive live game updates
- Handle disconnections
- Reconnection logic

---

#### Part 3: UI for Networking (Day 7)
- Login screen
- Registration screen
- Lobby list
- Loading indicators
- Error messages

---

### Week 8 Checkpoint
- ✅ Can login from iOS app
- ✅ Can create/join games
- ✅ Real-time updates work
- ✅ Error handling is smooth
- ✅ App feels polished

---

## Week 9: Multiplayer Game Flow

**Time**: 7-9 hours  
**Goal**: Complete multiplayer experience on iOS

### Learning Objectives
- Complex state management
- Navigation in SwiftUI
- Timer and animations
- Multiple views coordination
- Game flow UX

### Deliverables
1. ✅ Complete game flow (lobby → game → results)
2. ✅ Live timer display
3. ✅ Other players' word counts visible
4. ✅ End game screen with scores
5. ✅ Strike-out words displayed
6. ✅ Smooth transitions

### High-Level Tasks

#### Part 1: Game Flow (Day 1-3)
- Navigate from lobby to game
- Start game when all players ready
- Display countdown
- Lock input when time expires
- Show results screen

---

#### Part 2: Real-Time Updates (Day 4-5)
- Show player count in lobby
- Display timer to all players
- Synchronize game state
- Handle players leaving

---

#### Part 3: Results & Polish (Day 6-7)
- Results screen with all players
- Highlight struck-out words
- Show Fibonacci scoring breakdown
- "Play Again" functionality
- Final polish and animations

---

### Week 9 Checkpoint
- ✅ Full multiplayer game works end-to-end
- ✅ Multiple devices can play together
- ✅ UX is smooth and intuitive
- ✅ Edge cases handled

---

## Week 10: Polish, Testing & Future Features

**Time**: 7-9 hours  
**Goal**: Bug fixes, testing, documentation, and plan for future

### Deliverables
1. ✅ Comprehensive testing (backend and iOS)
2. ✅ Bug fixes from testing
3. ✅ Documentation updated
4. ✅ Code cleanup and refactoring
5. ✅ Future feature roadmap

### High-Level Tasks

#### Part 1: Testing (Day 1-3)
- Add missing tests
- Integration tests
- UI tests (XCUITest basics)
- Fix any failing tests
- Test edge cases

---

#### Part 2: Polish (Day 4-5)
- Code review and refactoring
- Remove dead code
- Improve error messages
- Performance optimization
- UI polish

---

#### Part 3: Documentation & Planning (Day 6-7)
- Update README
- API documentation
- Architecture documentation
- Git cleanup (squash if needed)
- Plan future features:
  - Top 2000 words option
  - Player word challenge
  - AI judge
  - Game statistics
  - Leaderboards
  - Friend system

---

### Week 10 Checkpoint - Final Review

**Technical Achievements**:
- ✅ Full-stack application (backend + iOS)
- ✅ Real-time multiplayer game
- ✅ Cloud deployed
- ✅ Tested and polished

**Skills Gained**:
- ✅ Modern Python (FastAPI, Pydantic, async)
- ✅ TDD methodology
- ✅ Git workflow (branching, committing, merging)
- ✅ REST APIs and WebSockets
- ✅ Swift and SwiftUI
- ✅ iOS development basics
- ✅ Cloud deployment
- ✅ Working with AI coding tools (Claude Code)

**Next Steps**:
1. Keep playing and find bugs
2. Add the word challenge feature
3. Improve UI/UX based on feedback
4. Build the AI judge feature
5. Share with friends and get real users!

---

## Git Skills Progression Throughout Plan

### Weeks 1-2: Basics
- init, add, commit, status, log
- .gitignore
- Remote repositories (origin, push, pull)
- Commit message best practices
- Basic branching and merging
- **Daily habit**: commit locally, push to GitHub

### Weeks 3-5: Intermediate
- Feature branches (push branches to GitHub)
- Merge conflicts resolution
- git diff
- git stash
- Pull requests (optional - we can merge locally or use PRs)
- Remote repositories (push, pull, fetch)

### Weeks 6-8: Advanced
- Interactive rebase (`git rebase -i`)
- Squashing commits before pushing
- Amending commits
- Cherry-picking
- Force push (with caution)

### Weeks 9-10: Expert
- Worktrees (parallel work on different branches)
- Stacked commits
- Reflog (undo mistakes)
- Advanced history viewing
- Clean git history management

---

## Testing Philosophy Throughout

### Unit Tests
- Test individual functions/methods
- Fast, isolated, deterministic
- Mock external dependencies

### Integration Tests
- Test multiple components together
- Database, API endpoints
- More realistic but slower

### End-to-End Tests
- Test full user flows
- Most realistic
- Slowest, run less frequently

**We'll write mostly unit tests, some integration tests, and a few E2E tests.**

---

## Weekly Rhythm

### Weekdays (Mon-Fri)
- 30-45 min sessions
- Focus on one small feature
- At least one commit per session
- **Push to GitHub** after each session (backup!)
- Journal entry

### Weekends (Sat-Sun)
- 90-120 min sessions
- Tackle bigger features
- Integration work
- Refactoring and cleanup
- Multiple commits and pushes throughout

### Weekly Review (Sunday evening)
- Review the week's progress (check GitHub commits!)
- Update JOURNAL.md with learnings
- Push all changes
- Adjust next week's plan if needed
- Celebrate wins! 🎉

---

## When Things Go Wrong

### If You're Stuck (>30 min on one thing)
1. STOP and write in journal what you're stuck on
2. Take a break
3. Ask Claude for help in next session
4. It's okay to move to something else and come back

### If You're Behind Schedule
- **Don't panic!** Learning takes time
- Skip or simplify less critical features
- Extend the timeline
- Quality > speed

### If You're Ahead of Schedule
- Add polish and tests
- Refactor for better code quality
- Explore advanced features
- Help document for others

---

## Success Metrics

### Technical
- ✅ All tests pass
- ✅ Type checking passes (mypy, Swift compiler)
- ✅ App works on multiple devices
- ✅ No critical bugs
- ✅ Code is readable and maintainable

### Learning
- ✅ You understand all the code
- ✅ You can explain architectural decisions
- ✅ You're comfortable with TDD
- ✅ Git feels natural
- ✅ You can debug issues independently

### Personal
- ✅ You're having fun!
- ✅ You feel accomplished
- ✅ You want to keep coding
- ✅ You're proud to show others

---

## Resources & References

### Python
- [Real Python](https://realpython.com/) - Excellent tutorials
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Official documentation
- [Pydantic Docs](https://docs.pydantic.dev/)

### Swift/iOS
- [Swift.org](https://swift.org/documentation/)
- [Apple SwiftUI Tutorials](https://developer.apple.com/tutorials/swiftui)
- [Hacking with Swift](https://www.hackingwithswift.com/) - Great learning resource

### Git
- [Pro Git Book](https://git-scm.com/book/en/v2) - Free, comprehensive
- [Oh Shit, Git!?!](https://ohshitgit.com/) - For when things go wrong

### Testing
- [pytest Documentation](https://docs.pytest.org/)
- [TDD By Example](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530) - Kent Beck's book

---

## Final Notes

**Remember**:
- This is YOUR learning journey
- Go at YOUR pace
- Ask questions constantly
- Make mistakes - that's how we learn
- Have fun!

**Claude's Role**:
- Guide and mentor
- Catch mistakes
- Explain concepts
- Pair program with you
- Push back when needed

**Your Role**:
- Write code (with Claude's help)
- Ask questions
- Test thoroughly
- Document learnings
- Stay curious

Let's build something great together! 🚀

---

**Last Updated**: 2025-01-15  
**Status**: Ready to begin Week 1
