# Technical Debt & Future Improvements

This file tracks known issues, shortcuts, and improvements we want to make later.

---

## High Priority

### 1. WebSocket Message Validation (Week 3-4)

**Issue**: WebSocket messages use informal JSON with no type validation

**Current state**:
- Messages are plain JSON dicts: `{"type": "submit_word", "word": "CAT"}`
- No Pydantic models for WebSocket messages
- No validation of incoming messages
- Easy to make mistakes with field names/types

**Why it's a problem**:
- No type safety
- Client must guess message structure
- Hard to document
- Easy to introduce bugs

**What needs to be done**:
1. Create `src/ws_models.py` with Pydantic models for all WebSocket messages:
   - Client → Server: `SubmitWordMessage`, `GetStateMessage`
   - Server → Client: `WordResultMessage`, `WordSubmittedMessage`, `GameStateMessage`, etc.
2. Add validation in `api_server.py` WebSocket handler
3. Update tests to use typed messages

**Estimated effort**: 1-2 hours

**Example**:
```python
# ws_models.py
class SubmitWordMessage(BaseModel):
    type: Literal["submit_word"]
    word: str = Field(min_length=1, max_length=20)

class WordResultMessage(BaseModel):
    type: Literal["word_result"]
    word: str
    valid: bool
    score: int
    message: str
```

**Reference**: See REST API models in `src/api_models.py` for the pattern to follow

---

## Medium Priority

### 2. Pre-Game Lobby Phase (Week 4)

**Issue**: Players join via REST, then immediately connect via WebSocket. No "waiting room" phase.

**Current state**:
- Players join game (REST POST /games/{id}/players)
- Game starts immediately (REST POST /games/{id}/start)
- Players connect via WebSocket after game started

**What's missing**:
- Pre-game lobby where players wait
- "Ready" button for each player
- Game starts automatically when all players ready
- Live updates as players join lobby

**Why it's useful**:
- Better UX - players see who's joined
- Natural flow: lobby → ready up → game starts
- Common pattern in multiplayer games

**What needs to be done**:
1. Add lobby state tracking to game
2. Add WebSocket messages for lobby events
3. Add "ready" mechanism
4. Auto-start when all players ready

**Estimated effort**: 2-3 hours

---

### 3. Automatic Timer Broadcasts (Week 4)

**Issue**: Game timer exists but clients must poll for updates

**Current state**:
- Timer runs on server
- Clients can request state via `{"type": "get_state"}`
- No automatic countdown broadcasts

**What's missing**:
- Server broadcasts timer updates every N seconds
- Clients get live countdown without polling
- Game end broadcast when timer expires

**What needs to be done**:
1. Create background task to broadcast timer updates
2. Add timer monitoring per game
3. Broadcast `{"type": "timer_update", "remaining": 150}`
4. Auto-end game when timer expires, broadcast results

**Estimated effort**: 1-2 hours

---

## Medium Priority (continued)

### 4. WebSocket Database Integration (Week 5 Day 4)

**Issue**: WebSocket endpoint still uses in-memory `games` dict

**Current state**:
- REST endpoints all use database (POST /games, GET /games/{id}, etc.)
- WebSocket `/ws/{game_id}/{player_id}` still uses in-memory storage
- 3 WebSocket tests failing, 123 other tests passing

**Why it's a problem**:
- Inconsistent with REST API
- WebSocket games don't persist
- Can't reconnect to games after server restart

**What needs to be done**:
1. Decide on approach:
   - Option A: Keep Game objects in memory during active games, sync to DB periodically
   - Option B: Reconstruct Game objects from DB on each message (simpler but slower)
   - Option C: Move validation logic out of Game class into standalone functions
2. Update WebSocket endpoint to load game state from database
3. Update WebSocket endpoint to persist word submissions to GamePlayer.words_found
4. Update WebSocket endpoint to persist scores to GamePlayer.score
5. Handle timer state (either in-memory or calculate from started_at + time_limit)
6. Update 3 failing WebSocket tests

**Estimated effort**: 3-4 hours

**Note**: Deferred from Day 4 to focus on REST API migration first

---

## Low Priority

### 5. Authorization & Game Privacy (Week 5 Day 4)

**Issue**: Currently implementing participant-only access, but future enhancements needed

**Current state** (being implemented):
- Adding authentication to all GET endpoints
- Adding authorization check: only game participants can view game state/results
- Requires user to be in GamePlayer table for that game

**Future enhancements to consider**:
1. **Public Games Flag**:
   - Add `is_public` boolean to Game model
   - Public games visible to any authenticated user
   - Default to private (current behavior)

2. **Spectator Mode**:
   - Generate special invite links for spectators
   - Spectators can view but not submit words
   - Useful for tournaments or teaching

3. **Shareable Result Links**:
   - Generate time-limited tokens for sharing final results
   - Allow unauthenticated access to results only (not live game)
   - Example: `/games/{id}/results?token=abc123`

4. **Tournament Mode**:
   - Games in tournaments have public results
   - Leaderboard endpoint showing aggregate stats
   - No individual game details exposed

5. **Deleted User Handling**:
   - What happens when a user is deleted?
   - Do other players still see their participation?
   - Archive games vs cascade delete?

**Estimated effort**:
- Public games flag: 1 hour
- Spectator mode: 3-4 hours
- Shareable result links: 2 hours
- Tournament mode: 4-6 hours

---

### 6. REST API Client CLI (Week 3)

**Issue**: No CLI client that uses the REST API

**Current state**:
- Original CLI uses game logic directly (`src/cli.py`)
- REST API exists but no client CLI
- Can test via FastAPI `/docs` or curl

**What's missing**:
- CLI that creates games via POST /games
- CLI that joins games via POST /games/{id}/players
- CLI that fetches results via GET /games/{id}/results

**Why it's useful**:
- Complete the learning plan's Week 3 goals
- Demonstrates REST client patterns
- Useful for testing

**What needs to be done**:
1. Create `src/rest_cli.py`
2. Use `httpx` library to call REST endpoints
3. Handle network errors gracefully
4. Simple menu-driven interface

**Estimated effort**: 2-3 hours

**Note**: Not critical since we have FastAPI's `/docs` for testing

---

### 5. Reconnection Logic (Future)

**Issue**: If WebSocket disconnects, game is lost

**What's missing**:
- Reconnection after disconnect
- Resume game state
- Store connection tokens

**Estimated effort**: 3-4 hours

---

### 6. Concurrent Access Control (Future)

**Issue**: In-memory game state dict has no locking

**Current state**:
- `games: Dict[str, Dict] = {}`
- Multiple requests could race

**What's needed**:
- Add locks for game state mutations
- Or use async-safe data structures

**Estimated effort**: 1-2 hours

**Note**: Not urgent for learning/development, critical for production

---

## Completed Items

### 1. Auth API Test Database Setup (Week 5) - COMPLETED 2025-10-31

**Issue**: Test fixture for auth API endpoints didn't properly create database tables

**Resolution**: Fixed by adding `poolclass=StaticPool` to SQLAlchemy engine configuration in test fixture. This ensures all connections share the same in-memory database instance.

**Files changed**:
- `tests/test_auth_api.py` - Added StaticPool to test fixture
- All 17 auth API tests now pass

---

## How to Use This File

1. **Before starting new features**: Check if related debt exists
2. **When fixing debt**: Move item to "Completed Items" section
3. **Add new debt**: Use template below

### Template for New Debt Items:

```markdown
### N. Title (When introduced)

**Issue**: Brief description

**Current state**: What we have now

**What's missing/wrong**: What needs to change

**What needs to be done**:
1. Step 1
2. Step 2

**Estimated effort**: X hours
```

---

## Deployment Strategy

### Fly.io + PostgreSQL Migration Plan

**Decision Made**: 2025-10-31 (Week 5 Day 3)

**Platform**: Fly.io with PostgreSQL database

**Rationale**:
- ✅ Free PostgreSQL included (vs $7/month on Render)
- ✅ Better for learning Docker and production deployment
- ✅ Geographic distribution for global users
- ✅ Industry-standard stack (Docker + PostgreSQL)
- ✅ More control and flexibility for future scaling

**Migration Steps (Week 6)**:
1. Add PostgreSQL support to codebase (keep SQLite for local dev)
2. Install `psycopg2-binary` for PostgreSQL driver
3. Make database URL configurable via environment variable
4. Test locally with PostgreSQL
5. Create `Dockerfile` for containerization
6. Create `fly.toml` configuration file
7. Deploy to Fly.io with `flyctl deploy`
8. Move SECRET_KEY to environment variables
9. Set up Alembic for database migrations
10. Test production deployment end-to-end

**Prerequisites**:
- Install Docker Desktop (for local testing)
- Install Fly.io CLI: `brew install flyctl` (Mac) or `curl -L https://fly.io/install.sh | sh`
- Create Fly.io account (free tier)

**Estimated effort**: 3-4 hours (learning + implementation)

---

**Last Updated**: 2025-10-31 (Week 5 Day 3)
