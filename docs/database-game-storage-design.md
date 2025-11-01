# Database Game Storage Design

## Current State (In-Memory)

```python
games: Dict[str, Dict] = {
    "abc123": {
        "game": Game(...),        # src/game.py Game object
        "config": GameConfig(...), # Game configuration
        "players": {              # player_id -> Player object
            "p1": Player(...),
            "p2": Player(...)
        },
        "status": "waiting",      # Game status
        "created_at": "2025-10-31T..."
    }
}
```

## Target State (Database)

### What Goes in Database

**Game Table** (already exists in `src/models.py`):
- ✅ `id` - Game UUID
- ✅ `creator_id` - User who created the game
- ✅ `status` - "waiting", "in_progress", "finished"
- ✅ `board_size` - 4 or 5
- ✅ `time_limit` - Seconds (nullable)
- ✅ `board_state` - JSON string of board grid
- ✅ `created_at`, `started_at`, `ended_at` - Timestamps

**GamePlayer Table** (already exists):
- ✅ `id` - Player UUID
- ✅ `game_id` - Which game
- ✅ `user_id` - Which user
- ✅ `score` - Current score
- ✅ `words_found` - JSON array of submitted words
- ✅ `joined_at` - When they joined

### What Stays in Memory

**WebSocket Connections** (can't persist):
```python
manager.active_connections: Dict[str, Set[WebSocket]] = {
    "game_id": {websocket1, websocket2, ...}
}
```

**Temporary Game Objects** (for performance during active game):
```python
# Optional: Keep active Game/Player objects in memory during gameplay
# Sync to database periodically
active_games: Dict[str, Game] = {}  # game_id -> Game object
```

## Migration Strategy

### Phase 1: Game Creation (POST /games)
- Create `Game` record in database
- Store `board_state` as JSON
- Return game_id from database

### Phase 2: Join Game (POST /games/{id}/players)
- Query `Game` from database
- Create `GamePlayer` record
- Associate user with game

### Phase 3: Start Game (POST /games/{id}/start)
- Update `Game.status` to "in_progress"
- Set `Game.started_at` timestamp

### Phase 4: Word Submission (WebSocket)
**Challenge**: High frequency updates during active game

**Option A** (Simple): Write to DB on every word
- Pro: Always consistent
- Con: DB writes on every word submission

**Option B** (Optimized): Keep in memory, sync periodically
- Pro: Fast during game
- Con: More complex, risk of data loss on crash

**Recommendation**: Start with Option A (simple), optimize later if needed

### Phase 5: Get Results (GET /games/{id}/results)
- Query `Game` and all `GamePlayer` records
- Calculate duplicates from `words_found`
- Return results

## Data Flow Example

### Creating a Game
```
1. User (authenticated) calls POST /games
2. Create Game record in DB:
   - id = uuid.uuid4()
   - creator_id = current_user.id
   - status = "waiting"
   - board_state = JSON of generated board
   - created_at = now()
3. Return game_id and board to user
```

### Joining a Game
```
1. User (authenticated) calls POST /games/{id}/players
2. Query Game from DB (verify exists and not full)
3. Create GamePlayer record:
   - game_id = {id}
   - user_id = current_user.id
   - score = 0
   - words_found = "[]"
   - joined_at = now()
4. Return player info
```

### Starting a Game
```
1. Call POST /games/{id}/start
2. Update Game in DB:
   - status = "in_progress"
   - started_at = now()
3. Broadcast to WebSocket clients
```

### Submitting Words (During Game)
```
1. WebSocket message: {"type": "submit_word", "word": "CAT"}
2. Query GamePlayer from DB
3. Validate word (dictionary, board path, not duplicate)
4. If valid:
   - Update GamePlayer.words_found (append word)
   - Update GamePlayer.score (add points)
   - Commit to DB
5. Broadcast result to all players
```

### Ending Game
```
1. Timer expires OR manual end
2. Update Game in DB:
   - status = "finished"
   - ended_at = now()
3. Calculate final scores and duplicates
4. Broadcast results
5. Close WebSocket connections
```

## Implementation Plan

### Files to Modify

1. **`src/api_server.py`**
   - Replace `games: Dict` with database queries
   - Keep `ConnectionManager` for WebSockets
   - Add helper functions for common queries

2. **`src/models.py`**
   - Already complete! No changes needed.

3. **`tests/test_api.py`**
   - Update tests to use database fixture (like test_auth_api.py)
   - Verify games persist correctly

### Helper Functions to Add

```python
def get_game_or_404(db: Session, game_id: str) -> Game:
    """Get game from DB or raise 404."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(404, "Game not found")
    return game

def get_game_player(db: Session, game_id: str, user_id: str) -> GamePlayer:
    """Get or create GamePlayer for user in game."""
    # ...
```

## Considerations

### Max Players Check
Currently: `len(game_state["players"]) >= max_players`
Database: `db.query(GamePlayer).filter(GamePlayer.game_id == game_id).count() >= game.???`

**Issue**: We don't store `max_players` in Game table!

**Solution**: Add `max_players` column to Game model

### Board State Storage
Currently: In-memory `Board` object
Database: JSON string

**Conversion**:
```python
# To JSON
board_json = json.dumps([[cell for cell in row] for row in board.grid])

# From JSON
board_data = json.loads(game.board_state)
board = Board(size=game.board_size)
board.grid = board_data  # Reconstruct board
```

### Game Logic Objects
Currently: `Game` object from `src/game.py` has timer, validation logic
Database: Only stores state, not logic

**Solution**:
- Store state in database (Game, GamePlayer models)
- Recreate `src/game.py` Game object when needed for validation
- Or: Move validation logic to separate functions (cleaner)

## Open Questions

1. **Do we need to recreate `src/game.py` Game objects?**
   - Pro: Reuse existing validation logic
   - Con: Overhead of reconstructing objects
   - Alternative: Extract validation to standalone functions

2. **How to handle timer expiration?**
   - Option A: Background task checks `started_at + time_limit`
   - Option B: Client-side timers, server validates on submission
   - Recommendation: Option B (simpler, clients already have timers)

3. **Should we cache active games in memory?**
   - For now: No - keep it simple, query DB each time
   - Later: Yes, if performance becomes an issue

## Success Criteria

- ✅ All game data persists in database
- ✅ Games survive server restart
- ✅ All existing tests pass (after updating for DB)
- ✅ New tests verify persistence
- ✅ No data loss on crashes
- ✅ Clean separation: state in DB, logic in code

---

**Last Updated**: 2025-10-31
