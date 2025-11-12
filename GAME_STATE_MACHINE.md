# Game State Machine Design

Comprehensive design for game and player state management in Clauddle.

**Created**: November 11, 2025
**Status**: Design Phase - Not Yet Implemented

---

## Overview

This document defines the state machines for:
1. **Game Lifecycle** - States a game progresses through from creation to cleanup
2. **Player Connection State** - States a player can be in within a game

---

## Game State Machine

### States

```
┌─────────────┐
│   CREATED   │ ─────┐
└─────────────┘      │
                     │ (first player joins)
                     ▼
┌─────────────┐
│   WAITING   │ ◄────┐
└─────────────┘      │
       │             │ (player leaves, count < max)
       │             │
       │ (room full OR manual start)
       ▼             │
┌─────────────┐      │
│ IN_PROGRESS │      │
└─────────────┘      │
       │             │
       │ (timer expires - ONLY EXIT)
       ▼             │
┌─────────────┐      │
│  FINISHED   │      │
└─────────────┘      │
       │             │
       │ (retention period expires)
       ▼             │
┌─────────────┐      │
│   DELETED   │      │
└─────────────┘      │
                     │
┌─────────────┐      │
│  ABANDONED  │ ─────┘
└─────────────┘
```

### State Definitions

#### 1. **CREATED**
- **Description**: Game object exists but no players have joined yet
- **Entry Conditions**:
  - User calls POST /games endpoint
- **While in State**:
  - Game configuration is set (board size, time limit, max players)
  - Board is generated
  - Friendly code is assigned
  - Game exists in database
  - No in-memory state yet
- **Exit Conditions**:
  - First player joins → WAITING
  - Timeout (5 minutes with no joins) → DELETED
- **Data**:
  - `status = "created"`
  - `created_at` timestamp
  - `board`, `friendly_code`, `max_players`, `time_limit`
  - `started_at = null`
  - `ended_at = null`

#### 2. **WAITING**
- **Description**: Game is waiting for players to join before starting
- **Entry Conditions**:
  - First player joins a CREATED game
  - Player leaves an IN_PROGRESS game and count drops below max (corner case - should we allow this?)
- **While in State**:
  - Players can join
  - Players can leave
  - Creator can manually start game (if >= 2 players)
  - Game automatically starts when room fills to max_players
  - In-memory game state exists (in `games` dict)
  - WebSocket connections active for joined players
- **Exit Conditions**:
  - Room fills to max_players → IN_PROGRESS (auto-start)
  - Creator manually starts (>= 2 players) → IN_PROGRESS
  - All players leave → ABANDONED
  - Timeout (10 minutes in waiting) → ABANDONED
- **Data**:
  - `status = "waiting"`
  - `created_at` timestamp
  - `started_at = null`
  - `ended_at = null`
  - List of players (GamePlayer rows)
  - In-memory: Player WebSocket connections

#### 3. **IN_PROGRESS**
- **Description**: Game is actively being played
- **Entry Conditions**:
  - Game auto-starts when room fills (WAITING → IN_PROGRESS)
  - Creator manually starts game (WAITING → IN_PROGRESS)
- **While in State**:
  - Timer is running (countdown from time_limit, max 10 minutes)
  - Players submit words via WebSocket
  - Words are validated and scored (provisional scores)
  - All player actions are persisted to database
  - Timer monitor task is running
  - Players can disconnect/reconnect anytime before timer expires
  - **IMPORTANT**: Game continues even if all players disconnect (allows reconnection)
- **Exit Conditions**:
  - Timer expires → FINISHED (automatic, only exit condition)
- **Data**:
  - `status = "in_progress"`
  - `started_at` timestamp (set on entry)
  - `ended_at = null`
  - `time_limit` (in seconds, max 600 = 10 minutes)
  - Player provisional scores and words_found arrays
  - In-memory: Game state, WebSocket connections, timer task

#### 4. **FINISHED**
- **Description**: Game has ended, scores are finalized, results are available
- **Entry Conditions**:
  - Timer expires in IN_PROGRESS state
  - Manual end in IN_PROGRESS state (future)
- **While in State**:
  - Final scores are calculated (accounting for duplicates)
  - Results are stored in database
  - Players can view results
  - WebSocket connections may close
  - In-memory state may be cleared after short delay
- **Exit Conditions**:
  - Retention period expires (7 days?) → DELETED
- **Data**:
  - `status = "finished"`
  - `started_at` timestamp
  - `ended_at` timestamp (set on entry)
  - Final scores calculated and stored
  - All player words_found arrays
  - Duplicate word tracking

#### 5. **ABANDONED**
- **Description**: Game was created but never completed
- **Entry Conditions**:
  - All players leave before game starts (WAITING → ABANDONED)
  - All players disconnect during game for > 5 minutes (IN_PROGRESS → ABANDONED)
  - Timeout in WAITING state (10 min)
  - Timeout in CREATED state (5 min)
- **While in State**:
  - Game is marked for cleanup
  - No further player actions allowed
  - Results show as "Game Abandoned"
- **Exit Conditions**:
  - Cleanup job runs → DELETED
  - Immediate deletion possible since no valuable data
- **Data**:
  - `status = "abandoned"`
  - `ended_at` timestamp (time of abandonment)
  - Partial game data preserved for debugging

#### 6. **DELETED**
- **Description**: Game has been removed from database
- **Entry Conditions**:
  - Cleanup job processes FINISHED games past retention period
  - Cleanup job processes ABANDONED games
- **While in State**:
  - Game no longer exists
  - 404 on all endpoints
- **Data**:
  - None (row deleted from database)

---

## State Transitions

### Trigger Events

| Trigger | From State(s) | To State | Notes |
|---------|---------------|----------|-------|
| Game created (POST /games) | - | CREATED | Initial state |
| First player joins | CREATED | WAITING | Activates game |
| Player joins | WAITING | WAITING | No state change |
| Room fills to max_players | WAITING | IN_PROGRESS | Auto-start |
| Manual start by creator | WAITING | IN_PROGRESS | Requires >= 2 players |
| Timer expires | IN_PROGRESS | FINISHED | Automatic finalization (ONLY exit from IN_PROGRESS) |
| All players leave | WAITING | ABANDONED | No players remaining |
| Created timeout (5 min) | CREATED | DELETED | Never started |
| Waiting timeout (10 min) | WAITING | ABANDONED | Players joined but never started |
| Retention period expires | FINISHED | DELETED | Cleanup (7 days) |
| Cleanup runs | ABANDONED | DELETED | Cleanup |

### Special Cases

#### **Player Reconnection**
- If game is IN_PROGRESS: Player can reconnect
  - Restore from database: words_found, provisional_score
  - Sync timer: Calculate time_remaining from started_at + time_limit - now()
  - Restore board state (rotation angle)
  - Resume gameplay

- If game is FINISHED: Player can view results
  - Load final scores from database
  - Display results screen

- If game is ABANDONED: Show error message
  - "Game was abandoned"

#### **Server Restart**
- On startup, scan database for IN_PROGRESS games:
  - Check if timer expired: → FINISHED
  - Check if all players disconnected > 5 min: → ABANDONED
  - Otherwise: Resume timer monitor task

- Don't load WAITING games into memory (lazy load on reconnect)

#### **Score Finalization**
When transitioning IN_PROGRESS → FINISHED:
1. Load all players' words_found arrays from database
2. Count occurrences of each word across all players
3. Mark duplicates (count > 1) as invalid (score = 0)
4. Calculate final score for each player (sum of non-duplicate words)
5. Store final scores in database
6. Broadcast game_ended message with final results

---

## Database Schema Changes

### Current Schema (models.py)
```python
class Game(Base):
    status = Column(String)  # Current: "waiting", "in_progress", "finished"
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    # ... other fields
```

### Proposed Schema
```python
class Game(Base):
    status = Column(String)  # NEW VALUES: "created", "waiting", "in_progress", "finished", "abandoned"
    created_at = Column(DateTime(timezone=True))  # NEW: track creation time
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    abandoned_at = Column(DateTime(timezone=True), nullable=True)  # NEW: track abandonment

    # NEW: Store final results (calculated on FINISHED)
    final_scores = Column(JSON, nullable=True)  # {player_id: final_score, ...}
    duplicate_words = Column(JSON, nullable=True)  # List of words found by multiple players
```

### Migration Needed
- Add `created_at` column (default to `started_at` or current time for existing games)
- Add `abandoned_at` column (nullable)
- Add `final_scores` column (nullable JSON)
- Add `duplicate_words` column (nullable JSON)
- Update existing games: "waiting" stays "waiting", "in_progress" stays "in_progress", "finished" stays "finished"

---

## Implementation Phases

### Phase 1: Core State Transitions (2-3 hours)
- Add new status values: "created", "abandoned"
- Implement CREATED state (currently games jump straight to WAITING)
- Implement ABANDONED state with transitions
- Add created_at and abandoned_at timestamps
- Update /games POST to create in CREATED state
- Update first join to transition CREATED → WAITING

### Phase 2: Score Finalization (2-3 hours)
- Add final_scores and duplicate_words columns
- Implement finalization logic on IN_PROGRESS → FINISHED
- Update results endpoint to return final scores (not provisional)
- Add duplicate word detection algorithm
- Add tests for score finalization

### Phase 3: Timeout & Cleanup (2-3 hours)
- Add max timer limit validation (10 minutes / 600 seconds)
- Implement CREATED timeout (5 min → DELETED)
- Implement WAITING timeout (10 min → ABANDONED)
- Create background cleanup task for FINISHED → DELETED (7 days)
- Create background cleanup task for ABANDONED → DELETED (immediate)
- Add startup recovery logic for server restarts

### Phase 4: Client Reconnection (2-3 hours)
- Fix timer sync: calculate from started_at + time_limit
- Send time_remaining on reconnect
- Load player state from database
- Handle ABANDONED games gracefully
- Update iOS client to handle reconnection properly

---

## Design Decisions (Finalized)

1. **Can players leave during IN_PROGRESS?**
   - ✅ **Decision**: Yes, mark them as "left" but keep their score
   - Players can close app/disconnect without penalty

2. **Should we show provisional scores during IN_PROGRESS?**
   - ✅ **Decision**: Yes, show live scores (with note they may change due to duplicates)
   - Better engagement and feedback

3. **Retention period for FINISHED games?**
   - ✅ **Decision**: 7 days
   - Manageable database size, sufficient for players to review

4. **Can creator manually end IN_PROGRESS game?**
   - ✅ **Decision**: No (not in v1)
   - Simpler implementation, can add later if needed

5. **What happens to IN_PROGRESS games when all players disconnect?**
   - ✅ **Decision**: Keep game running until timer expires
   - Players can reconnect anytime before timer runs out
   - More forgiving for network issues and app crashes

6. **Maximum game timer limit?**
   - ✅ **Decision**: 10 minutes (600 seconds)
   - Prevents very long-lived IN_PROGRESS games
   - Reasonable for word game sessions

7. **What happens to IN_PROGRESS games during deployment?**
   - ✅ **Decision**: Document graceful shutdown procedure
   - Recommendation: Deploy during low-traffic periods
   - Future: Add deployment hook to finish active games gracefully

---

## Testing Strategy

### Unit Tests
- Test each state transition
- Test invalid state transitions (should fail)
- Test score finalization logic (duplicate detection)
- Test timeout conditions
- Test server restart recovery

### Integration Tests
- Test full game lifecycle (CREATED → FINISHED)
- Test abandonment scenarios
- Test reconnection at each state
- Test cleanup job execution

### Manual Testing
- Play a full game, verify scores are correct
- Disconnect mid-game, reconnect, verify timer sync
- Abandon a game, verify cleanup
- Restart server mid-game, verify recovery

---

## Next Steps

1. **Review this design** - Discuss open questions and get alignment
2. **Implement Phase 1** - Core state transitions
3. **Write tests** - For Phase 1 functionality
4. **Deploy to production** - With monitoring
5. **Repeat for Phases 2-4**

---

## References

- Current code: `src/api_server.py` (WebSocket handlers)
- Current code: `src/models.py` (Game model)
- Current TODO: `TODO.md` (Game Lifecycle section)
