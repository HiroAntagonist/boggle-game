# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Boggle is a multiplayer word game implementation in Python with both local and network multiplayer modes. It uses a clean architecture with Test-Driven Development (TDD) and comprehensive type safety via mypy.

## Essential Commands

### Development
```bash
# Run the local game (single or local multiplayer)
boggle

# Run network game server
python -m src.network.game_server

# Run network game client
python -m src.network.network_cli
```

### Testing
```bash
pytest                        # Run all tests
pytest -v                     # Verbose output
pytest tests/test_board.py    # Run specific test file
pytest -k "test_name"         # Run tests matching pattern
pytest --cov=src tests/       # Run with coverage report
pytest-watch                  # Continuous testing during development
```

### Type Checking
```bash
mypy src/                     # Type check all source code
```

### Package Management
```bash
uv pip install -e .           # Install package in development mode
uv add package-name           # Add production dependency
uv add --dev package-name     # Add development dependency
```

## Architecture

### Core Components (Single-Player & Local Multiplayer)

**Board** (`src/board.py`): Generates random 4x4 or 5x5 boards using official Boggle dice. Validates word paths using depth-first search (DFS) with backtracking to check if letters form a connected path on the board.

**Dictionary** (`src/dictionary.py`): Loads 267,000+ SOWPODS words into a set for O(1) lookup. Validates whether submitted words exist in the official dictionary.

**Scorer** (`src/scorer.py`): Calculates points using Fibonacci sequence (3-letter word = 1pt, 4-letter = 2pts, 5-letter = 3pts, 6-letter = 5pts, etc.).

**Player** (`src/player.py`): Tracks individual player state including submitted words and name.

**Game** (`src/game.py`): Orchestrates all components. Enforces game rules including word validation, duplicate detection (strike-out logic), timer management, and board rotation. Supports both single-player mode and local multiplayer (2-4 players on same machine).

**Config** (`src/config.py`): Validates game settings using Pydantic (board size, time limits, player counts, etc.).

**CLI** (`src/cli.py`): Command-line interface for local gameplay (single-player and pass-and-play multiplayer).

### Network Architecture (Async WebSocket-Based)

**Protocol** (`src/network/protocol.py`): JSON message definitions for client-server communication. Uses MessageType enum for all message types (CREATE_ROOM, JOIN_ROOM, SUBMIT_WORD, GAME_STARTED, etc.).

**GameServer** (`src/network/game_server.py`): Manages multiple concurrent game rooms via WebSockets. Routes messages between clients, broadcasts game state changes, and manages player connections. Each room runs independently with its own Game instance. Server handles timer expiration by spawning background async tasks (`monitor_game_timer`) that automatically end games and broadcast final scores.

**GameRoom** (`src/network/game_room.py`): Manages a single game session including players, WebSocket connections, and game state. Supports auto-start when room fills to max_players.

**GameClient** (`src/network/game_client.py`): WebSocket client for connecting to game server. Handles message routing and maintains local game state. Uses two concurrent async tasks: `receive_messages()` (background listener) and input loops (foreground).

**Network CLI** (`src/network/network_cli.py`): Async command-line interface using `aioconsole` for non-blocking input. Implements lobby loop pattern with state checking to handle race conditions (game starting while waiting for input).

### Key Design Patterns

**Dependency Injection**: Game components (Board, Dictionary, Scorer) are passed to Game constructor, not created internally. This enables testing with mocks and allows GameServer to share expensive resources (Dictionary) across rooms.

**Concurrent Async Design**: Network multiplayer uses asyncio for non-blocking I/O. All players submit words simultaneously (no turn-taking). Server spawns background tasks for timer monitoring. Client runs two concurrent tasks (receive + input).

**State Synchronization**: GameClient maintains local state (in_game, connected flags) synchronized with server. Uses "defense in depth" pattern with multiple state checks to prevent race conditions.

**Strike-Out Logic**: Multiplayer game tracks duplicate words across all players. Words submitted by multiple players score zero for all (classic Boggle rule). Implemented by counting word occurrences across players and filtering duplicates from valid words.

## Type Safety

This project uses strict mypy configuration (`mypy.ini`):
- Full type hints required on all function signatures
- Strict None checking enabled
- Python 3.12 syntax supported (using `|` for unions instead of `Union`)
- All source code in `src/` must pass type checking
- Tests have relaxed type checking

Always run `mypy src/` before committing to catch type errors.

## Testing Philosophy

This project follows Test-Driven Development (TDD):
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor while keeping tests green (REFACTOR)

Tests must:
- Cover all functionality comprehensively
- Use real data and logic (no mocking of business logic)
- Test actual behavior, not implementation details
- Pass with pristine output (no unexpected logs or warnings)

## Project Structure

```
boggle/
├── src/
│   ├── board.py           # Board generation and path validation (DFS)
│   ├── dictionary.py      # Word dictionary loading and validation
│   ├── scorer.py          # Fibonacci-based scoring
│   ├── player.py          # Player state management
│   ├── game.py            # Game orchestration and rules
│   ├── config.py          # Pydantic configuration models
│   ├── cli.py             # Local multiplayer CLI
│   └── network/           # Network multiplayer components
│       ├── protocol.py    # Message type definitions
│       ├── game_server.py # WebSocket server managing rooms
│       ├── game_room.py   # Single room state management
│       ├── game_client.py # WebSocket client
│       └── network_cli.py # Async network game CLI
├── tests/                 # Comprehensive test suite (mirrors src/)
├── data/
│   └── sowpods.txt        # 267k word dictionary
├── pyproject.toml         # Project metadata and dependencies
└── mypy.ini               # Type checking configuration
```

## Game Rules Summary

- **Board**: 4x4 or 5x5 grid with randomized Boggle dice
- **Words**: Minimum 3 letters, must exist in dictionary, path must be valid
- **Path**: Adjacent letters (including diagonals), each cell used once per word
- **Scoring**: Fibonacci sequence based on word length
- **Multiplayer Strike-Out**: Words found by multiple players score zero for all
- **Timer**: Optional time limit (configurable), game ends when time expires
- **Board Rotation**: Players can rotate board 90° for different perspectives

## Network Protocol Flow

### Creating and Joining Room
1. Client connects to ws://localhost:8765
2. CREATE_ROOM → Server responds with ROOM_CREATED + room_id
3. Other clients JOIN_ROOM with room_id → Server broadcasts PLAYER_JOINED
4. When room is full, auto-start sends GAME_STARTED with board data

### During Game
1. All players submit words concurrently (no turns)
2. SUBMIT_WORD → Server validates and broadcasts WORD_ACCEPTED or WORD_REJECTED
3. Server monitors timer in background task
4. When time expires, server broadcasts GAME_ENDED with final scores and duplicates

### Key Implementation Details
- Server uses `asyncio.create_task()` for timer monitoring and room cleanup
- Client uses `aioconsole.ainput()` for non-blocking input (no threads needed)
- Lobby loop polls `client.in_game` flag to exit when game starts
- WebSocket connections handle both str and bytes messages
