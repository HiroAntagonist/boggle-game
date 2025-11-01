# Technical Debt & Future Improvements

This file tracks known issues, shortcuts, and improvements we want to make later.

---

## High Priority

None currently! All high-priority items completed.

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

### 4. Game Lifecycle & Resilience Design (Week 5 Day 5)

**Issue**: Need comprehensive design for game finalization, scoring, and failure handling

**Current state**:
- Games can start but have no automatic finalization
- Provisional scores stored in DB on each word submission (`GamePlayer.score`)
- Results endpoint uses provisional scores (doesn't account for cross-player duplicates)
- No handling of disconnection/reconnection scenarios
- No cleanup of "zombie" games (started but never finished)
- Timer calculations exist but no auto-finalization when timer expires

**Design questions to resolve**:

**A. Score Finalization Strategy:**
- When should final scores be calculated?
  - On timer expiration (automatic)?
  - On manual game end (POST /games/{id}/end)?
  - Lazy in results endpoint (calculate on-demand)?
- Should we preserve both provisional and final scores?
- How do we handle the results endpoint for in-progress vs finished games?

**B. Client Disconnect/Reconnect:**
- Current: Reload words from DB, rebuild Player object, ignore stored score
- Questions:
  - Should we display provisional score to reconnected players?
  - Do we recalculate score from words_found or trust DB?
  - How do we sync in-memory state with DB state?
  - What happens if player reconnects after game ends?

**C. Zombie Game Cleanup:**
- Games stuck in "in_progress" state due to:
  - Server crash during game
  - All players disconnect before timer expires
  - Timer expires but no finalization logic
- Solutions:
  - Background task to monitor and clean up old games?
  - Periodic cleanup job?
  - Lazy finalization on access?
  - TTL-based cleanup?

**D. Timer Expiration & Auto-Finalization:**
- Need background task to monitor game timers
- When timer expires:
  - Calculate duplicates across all players
  - Recalculate final scores (excluding duplicates)
  - Update GamePlayer.score with final values
  - Set Game.status = "finished"
  - Broadcast game_ended message to connected players
- What if no players are connected when timer expires?

**E. Server Crash Recovery:**
- What happens to in-progress games after server restart?
- Can players reconnect and continue?
- Should we auto-fail crashed games?
- How do we distinguish crashed games from legitimate in-progress games?

**Related to**:
- Item #3 (Automatic Timer Broadcasts)
- Item #5 (Authorization & Game Privacy)

**Estimated effort**: 4-6 hours design + implementation

**Recommendation**: Design comprehensive game lifecycle state machine before implementing piecemeal solutions

---

## Low Priority

### 7. Database Migrations with Alembic (Week 6 Day 1)

**Issue**: No database migration tooling for schema changes in production

**Current state**:
- Using `Base.metadata.create_all(bind=engine)` in docker-entrypoint.sh
- Works great for initial deployment and empty databases
- No way to safely update schema in production without losing data
- Schema changes require manual SQL or dropping/recreating tables

**What's missing**:
- Alembic migration framework
- Version-controlled schema changes
- Upgrade/downgrade scripts for each change
- Migration tracking in database

**Why it's needed**:
- Safe schema updates in production (no data loss)
- Track schema changes over time
- Rollback capability if migrations fail
- Team synchronization on schema versions
- Standard practice for production applications

**What needs to be done**:
1. Install Alembic: `uv add alembic`
2. Initialize Alembic: `alembic init alembic`
3. Configure `alembic.ini` with database URL
4. Generate initial migration from current schema
5. Update docker-entrypoint.sh to run `alembic upgrade head`
6. Test migration workflow locally
7. Document migration process in README
8. Redeploy to Fly.io with migration support

**Example use cases**:
- Adding `bio` field to User table
- Creating new `game_stats` table
- Adding indexes for performance
- Renaming columns
- Adding foreign key constraints

**Estimated effort**: 2-3 hours (setup + testing)

**Priority**: Low for now (no schema changes planned), High when we need to modify schema

---

### 8. Health Check Endpoint (Week 6 Day 1)

**Issue**: No health check endpoint for monitoring and orchestration

**Current state**:
- Fly.io has no configured health checks
- No way to verify app is responding correctly
- No database connectivity check
- Manual verification required

**What's missing**:
- `/health` endpoint that returns app status
- Database connectivity check
- Dependency status (dictionary loaded, etc.)
- Response time metrics
- Proper HTTP status codes

**Why it's needed**:
- Fly.io health checks for auto-restart on failures
- Load balancer routing decisions
- Monitoring and alerting
- Quick verification after deployment
- Debugging production issues

**What needs to be done**:
1. Create `/health` GET endpoint
2. Check database connection (simple query)
3. Check critical dependencies (dictionary loaded)
4. Return JSON with status details:
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "dictionary_loaded": true,
     "uptime_seconds": 3600
   }
   ```
5. Return 200 for healthy, 503 for unhealthy
6. Update fly.toml with health check configuration:
   ```toml
   [[services.http_checks]]
     interval = "10s"
     timeout = "2s"
     grace_period = "5s"
     method = "GET"
     path = "/health"
   ```
7. Add tests for health endpoint
8. Redeploy to Fly.io

**Estimated effort**: 1 hour

**Priority**: Low (app is stable), Medium for production best practices

---

### 9. Monitoring and Logging (Week 6 Day 1)

**Issue**: No structured logging, monitoring, or error tracking

**Current state**:
- Basic print/logging to stdout
- Fly.io collects logs but no structure
- No error tracking or alerting
- No performance metrics
- No visibility into production issues

**What's missing**:
- Structured logging (JSON format)
- Error tracking service (Sentry)
- Performance monitoring (request timing)
- Database query monitoring
- WebSocket connection metrics
- Alert notifications for errors

**Why it's needed**:
- Debug production issues quickly
- Proactive error detection
- Performance optimization insights
- User experience monitoring
- Compliance and audit trails

**What needs to be done**:

**Phase 1: Structured Logging (1 hour)**
1. Configure Python logging with JSON formatter
2. Add request IDs for tracing
3. Log key events: game start, word submission, errors
4. Include context: user_id, game_id, timestamp

**Phase 2: Error Tracking (1 hour)**
1. Sign up for Sentry (free tier)
2. Install: `uv add sentry-sdk`
3. Configure Sentry in FastAPI app
4. Add SENTRY_DSN to Fly.io secrets
5. Test error capture and notifications

**Phase 3: Metrics (2 hours)**
1. Add Prometheus metrics endpoint
2. Track: request count, latency, active games, connected players
3. Optional: Set up Grafana dashboard

**Phase 4: Alerts (1 hour)**
1. Configure Sentry alerts for error rate spikes
2. Set up email/Slack notifications
3. Define alert thresholds

**Tools to consider**:
- Sentry (error tracking) - Free tier available
- Prometheus + Grafana (metrics) - Self-hosted or managed
- Fly.io built-in metrics - Available in dashboard
- LogDNA / Datadog (log aggregation) - Paid

**Estimated effort**:
- Basic logging: 1 hour
- Sentry: 1 hour
- Full monitoring stack: 5-6 hours

**Priority**: Low for learning project, High for production with real users

---

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

### 2. WebSocket Database Integration (Week 5 Day 5) - COMPLETED 2025-10-31

**Issue**: WebSocket endpoint used in-memory `games` dict while REST endpoints used database

**Resolution**: Implemented hybrid approach - reconstruct in-memory Game/Board/Player objects from database on WebSocket connection for fast validation, persist word submissions and scores back to database.

**Implementation**:
- Load game and player from database on WebSocket connect
- Reconstruct Board from JSON board_state
- Create in-memory Game/Board/Player objects for validation
- Persist word submissions to GamePlayer.words_found JSON array
- Update GamePlayer.score on each valid word submission
- Calculate time remaining from database timestamps (with timezone handling)

**Files changed**:
- `src/api_server.py` - WebSocket endpoint refactored (lines 441-593)
- `tests/test_websocket.py` - Added auth headers to start_game calls
- All 130 tests now pass (100%)

**Design decisions**:
- Provisional scores: Stored in DB during gameplay, don't account for cross-player duplicates
- Final scoring: Deferred to results endpoint or finalization logic (see item #4)
- Reconnection: Reload words from DB, rebuild Player object (score sync TBD)

---

### 3. WebSocket Message Validation (Week 5 Day 5) - COMPLETED 2025-10-31

**Issue**: WebSocket messages used informal JSON with no type validation

**Resolution**: Created Pydantic models for all WebSocket message types, providing type safety and automatic validation.

**Implementation**:
- Created `src/ws_models.py` with Pydantic models for all message types:
  - Client → Server: `SubmitWordMessage`, `GetStateMessage`
  - Server → Client: `WordResultMessage`, `WordSubmittedMessage`, `GameStateMessage`, `PlayerConnectedMessage`, `PlayerDisconnectedMessage`
- Updated WebSocket handler to validate incoming messages with try/catch
- Use `model_dump_json()` for type-safe outgoing messages
- Added error responses for invalid message format

**Files changed**:
- `src/ws_models.py` - New file with 7 Pydantic models
- `src/api_server.py` - WebSocket handler validates all messages
- `tests/test_websocket.py` - Added validation tests
- All 132 tests passing (100%)

**Benefits**:
- Type safety for WebSocket messages
- Clear API contract documentation via Pydantic models
- Better error messages for clients (field validation, length constraints)
- Validation happens automatically - can't forget to validate

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

**Last Updated**: 2025-11-01 (Week 6 Day 1)
