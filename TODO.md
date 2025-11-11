# Technical Debt & Improvements

Consolidated tracking of known issues, shortcuts, and future improvements.

**Last Updated**: 2025-01-11

---

## High Priority

### Authentication & Security

- [ ] **Add Client ID validation**: OAuth endpoint should validate that the Client ID in the ID token matches our expected Client ID for additional security (src/api_server.py:1314-1392)

- [ ] **Implement refresh tokens**: Currently using 30-day JWT tokens; should implement refresh token mechanism for better security

- [ ] **Add rate limiting**: OAuth endpoint needs rate limiting to prevent abuse

### iOS App

- [ ] **Implement secure token storage**: Currently storing JWT token in memory; should use iOS Keychain for persistent, secure storage
  - Estimated effort: 2-3 hours

- [ ] **Add OAuth error handling**: Better error messages for OAuth failures (network errors, invalid tokens, server errors)
  - Estimated effort: 1 hour

### Database & Infrastructure

- [ ] **Database migrations**: Currently using `Base.metadata.create_all()` which doesn't handle schema changes; need proper migration tool (Alembic)
  - Priority: Low now (no schema changes planned), High when we need to modify schema
  - Estimated effort: 2-3 hours (setup + testing)

- [ ] **Add database connection pooling monitoring**: Log pool metrics to catch connection leaks
  - Estimated effort: 1-2 hours

### Testing

- [ ] **Add integration tests**: End-to-end OAuth flow testing with real database
  - Estimated effort: 3-4 hours

- [ ] **Add iOS unit tests**: Test OAuth flow, error handling, and token management
  - Estimated effort: 3-4 hours

---

## Medium Priority

### Game Lifecycle & Resilience Design

**Status**: Partially completed - some components done, design questions remain

**What's been completed:**
- ✅ Timer Expiration & Auto-Finalization (completed Nov 2, 2025)
- ✅ Server Crash Recovery (partial - timer monitor resumes on restart)

**What remains to be resolved:**

- [ ] **Score Finalization Strategy** - Need to decide on approach:
  - When should final scores be calculated? (On timer expiration? Manual game end? Lazy in results endpoint?)
  - Should we preserve both provisional and final scores in database?
  - How do we handle the results endpoint for in-progress vs finished games?
  - **Current issue**: Results endpoint uses provisional scores, doesn't account for cross-player duplicates
  - Estimated effort: 2-3 hours design + implementation

- [ ] **Client Disconnect/Reconnect (detailed)** - Multiple unresolved questions:
  - **Timer sync issue**: Client runs local countdown timer with no server sync on reconnect
  - Should we display provisional score to reconnected players?
  - Do we recalculate score from words_found array or trust stored DB score?
  - How do we sync in-memory game state with database state?
  - What happens if player reconnects after game ends?
  - How does client get accurate time remaining on reconnect? (currently uses stale local timer)
  - **Current state**: Reload words from DB, rebuild Player object, timer may be out of sync
  - Estimated effort: 3-4 hours

- [ ] **Zombie Game Cleanup** - Handle abandoned games:
  - Games stuck in "in_progress" state due to:
    - Server crash during game
    - All players disconnect before timer expires
    - Network issues preventing finalization
  - **Solutions to consider**:
    - Background task to monitor and clean up old games?
    - Periodic cleanup job?
    - Lazy finalization on next access?
    - TTL-based cleanup?
  - **Current state**: Timer monitor handles timer expiration, but not abandoned games with no timer
  - Estimated effort: 2-3 hours

**Recommendation**: Design comprehensive game lifecycle state machine before implementing piecemeal solutions

**Total estimated effort**: 4-6 hours for complete design + implementation

---

### Authentication & Security

- [ ] **Support additional OAuth providers**: Currently only Google; could add Apple Sign-In, GitHub, etc.
  - Estimated effort: 3-4 hours per provider

- [ ] **Add user email verification**: Email/password registrations should verify email addresses
  - Estimated effort: 2-3 hours

- [ ] **Implement account deletion**: Users should be able to delete their accounts (GDPR compliance)
  - Estimated effort: 2-3 hours

### iOS App

- [ ] **Add loading states**: OAuth login should show loading indicator during token exchange (partially done, could be improved)

- [ ] **Add biometric authentication**: Support Face ID/Touch ID for repeat logins after Keychain storage is implemented
  - Estimated effort: 2-3 hours

- [ ] **Handle OAuth token expiration**: Gracefully handle expired JWT tokens and prompt re-authentication
  - Estimated effort: 2-3 hours

### Database & Infrastructure

- [ ] **Add database backups**: Set up automated backups for production PostgreSQL database via Fly.io
  - Estimated effort: 1-2 hours

- [ ] **Document database connection setup**: Create clear documentation for connecting to correct database (`boggle_game_ar` vs `postgres`) in CLAUDE.md

### Testing

- [ ] **Add API contract tests**: Verify iOS models match backend Pydantic models
  - Can be automated once iOS uses generated models
  - Estimated effort: 2-3 hours

- [ ] **Test account linking scenarios**: Comprehensive tests for all account linking edge cases
  - Estimated effort: 2-3 hours

### Code Quality

- [ ] **Extract OAuth verification logic**: Move Google ID token verification to separate service class
  - Estimated effort: 1 hour

- [ ] **Add OpenAPI documentation**: Document OAuth endpoint in FastAPI's auto-generated docs with proper examples
  - Estimated effort: 30 minutes

- [ ] **Standardize error responses**: Create consistent error response format across all endpoints
  - Estimated effort: 2-3 hours

### Documentation

- [ ] **Document OAuth setup process**: Step-by-step guide for setting up Google Cloud OAuth credentials
  - Estimated effort: 1 hour

- [ ] **Document deployment process**: Clear instructions for deploying backend changes to Fly.io
  - Estimated effort: 1 hour

- [ ] **Update API documentation**: Add OAuth endpoints to API documentation in CLAUDE.md
  - Estimated effort: 30 minutes

- [ ] **Document database queries**: Add commonly used database queries to CLAUDE.md (connection, user lookups, etc.)

### Game Features

- [ ] **Authorization & Game Privacy**: Future enhancements for game access control
  - Public games flag (`is_public` boolean)
  - Spectator mode (view-only access)
  - Shareable result links (time-limited tokens)
  - Tournament mode with public leaderboards
  - Estimated effort: 1-6 hours depending on feature

- [ ] **Concurrent Access Control**: Add locking for in-memory game state mutations
  - Currently: `games: Dict[str, Dict] = {}` has no locking
  - Risk: Race conditions with multiple concurrent requests
  - Estimated effort: 1-2 hours
  - Priority: Low for development, High for production

### Monitoring

- [ ] **Structured Logging**: Add structured logging with JSON format, request IDs, and context
  - Estimated effort: 1 hour

- [ ] **Error Tracking**: Set up Sentry for error tracking and alerting
  - Estimated effort: 1 hour

- [ ] **Performance Metrics**: Add Prometheus metrics endpoint tracking request count, latency, active games
  - Estimated effort: 2 hours

---

## Low Priority

- [ ] **Add OAuth sign-out**: Implement sign-out that clears both app state and Google Sign-In session

- [ ] **Clean up background Bash shells**: Many long-running background processes from deployment/debugging (see git status reminders)

- [ ] **Remove or document fly.toml**: Current git status shows untracked `fly.toml` file

- [ ] **REST API Client CLI**: CLI that uses REST API instead of direct game logic (useful for testing, not critical)
  - Estimated effort: 2-3 hours

---

## Completed Items

### iOS Model Generation & Integration (Week 6 Day 4 - Nov 11, 2025)
- [x] Replace manual models with generated OpenAPI models
- [x] Remove all manual struct definitions from BoggleAPI.swift
- [x] Add all generated files to Xcode project
- [x] Update imports to use OpenAPIClient package
- [x] Achieve single source of truth for iOS models (auto-generated from backend)

### OAuth Implementation (Week 6 Day 4 - Nov 11, 2025)
- [x] Implement Google OAuth authentication with native iOS SDK
- [x] Add account linking by email (OAuth + email/password on same account)
- [x] Auto-registration for OAuth users
- [x] Pull display name from Google profile
- [x] Add comprehensive OAuth tests (8 test cases)
- [x] Fix JSON encoding mismatch (camelCase/snake_case) with CodingKeys
- [x] Deploy OAuth to production
- [x] Verify end-to-end OAuth flow
- [x] Migrate authentication from username to email throughout stack

### OpenAPI Schema Generation (Week 6 Day 2 - Nov 2, 2025)
- [x] Install openapi-generator tool
- [x] Generate 22 Swift Codable models from backend OpenAPI schema
- [x] Create automation script: `scripts/generate_ios_models.sh`
- [x] Document schema generation workflow in CLAUDE.md
- **Note**: Models generated but not yet integrated into iOS app (see High Priority: "Replace manual models")

### iOS GameView Layout (Week 6 Day 3 - Nov 10, 2025)
- [x] Implement responsive layout system (20-40-40 split)
- [x] Fix board grid centering in portrait mode
- [x] Fix rotate button overlapping with tiles
- [x] Fix landscape layout alignment
- [x] Implement orientation-aware tile sizing
- [x] Test on multiple device sizes (SE, Pro, Pro Max)

### WebSocket & Game Lifecycle (Week 6 Day 2 - Nov 2, 2025)
- [x] Implement on-demand timer monitor (starts/stops automatically)
- [x] Add automatic game finalization when timer expires
- [x] Broadcast game_ended message with final results
- [x] Add client-side countdown timer display
- [x] Implement pre-game lobby/waiting room
- [x] Add real-time player join notifications
- [x] Implement auto-start when room fills

### WebSocket Database Integration (Week 5 Day 5 - Oct 31, 2025)
- [x] Integrate WebSocket endpoint with database
- [x] Persist word submissions to GamePlayer.words_found
- [x] Update provisional scores in database
- [x] Reconstruct in-memory Game objects from database state
- [x] Handle timezone-aware timestamp calculations

### Pydantic Message Validation (Week 5 Day 5 - Oct 31, 2025)
- [x] Create Pydantic models for all WebSocket message types
- [x] Implement automatic validation in WebSocket handler
- [x] Add error responses for invalid messages
- [x] Document message contracts via type-safe models

### Mypy Type Safety (Week 6 Day 2 - Nov 2, 2025)
- [x] Fix all 15 pre-existing mypy type errors
- [x] Add proper None checks for User queries
- [x] Add conditional checks for json.loads() calls
- [x] Add default values for optional GameConfig fields
- [x] Achieve full type safety: "Success: no issues found"

### Health Check Endpoint (Week 6 Day 2 - Nov 2, 2025)
- [x] Implement GET /health endpoint with system status
- [x] Add database connectivity check with response time
- [x] Add WebSocket connection metrics
- [x] Add background task monitoring
- [x] Add game statistics (total, in_progress, waiting, finished)

### Docker & Fly.io Deployment (Week 6 Day 1 - Oct 31, 2025)
- [x] Add PostgreSQL support to codebase
- [x] Create Dockerfile for containerization
- [x] Create fly.toml configuration
- [x] Deploy to Fly.io with PostgreSQL database
- [x] Move secrets to environment variables
- [x] Test production deployment end-to-end

### Authentication & Authorization (Week 5 Day 4 - Oct 30, 2025)
- [x] Implement JWT token authentication
- [x] Add authentication to all game endpoints
- [x] Implement participant-only authorization (users can only view games they're in)
- [x] Add proper 401/403 error responses

---

## Next Steps Recommendation

Based on recent completions (OAuth + iOS Model Generation), suggested next priorities:

**Path A - iOS Polish (3-4 hours remaining)**:
1. ✅ ~~Replace manual models with generated OpenAPI models~~ (COMPLETED)
2. Implement iOS Keychain for secure token storage
3. Add better OAuth error handling

**Path B - Backend Security (2-3 hours)**:
1. Add Client ID validation to OAuth endpoint
2. Implement rate limiting for OAuth endpoint
3. Add Sentry error tracking

**Path C - Testing (6-8 hours)**:
1. Add OAuth integration tests with real database
2. Add iOS unit tests for OAuth flow
3. Add API contract tests

---

## How to Use This File

1. **Before starting features**: Check if related debt exists
2. **When fixing debt**: Move item to "Completed Items" section with date
3. **Add new debt**: Include issue description, current state, what needs to be done, and estimated effort

---

## Reference: Deployment Strategy

### Fly.io + PostgreSQL Migration (Completed Oct 31, 2025)

**Platform**: Fly.io with PostgreSQL database

**Rationale**:
- ✅ Free PostgreSQL included (vs $7/month on other platforms)
- ✅ Better for learning Docker and production deployment
- ✅ Geographic distribution for global users
- ✅ Industry-standard stack (Docker + PostgreSQL)
- ✅ More control and flexibility for future scaling

**Completed migration steps:**
1. ✅ Added PostgreSQL support to codebase (kept SQLite for local dev)
2. ✅ Installed `psycopg2-binary` for PostgreSQL driver
3. ✅ Made database URL configurable via environment variable
4. ✅ Tested locally with PostgreSQL
5. ✅ Created `Dockerfile` for containerization
6. ✅ Created `fly.toml` configuration file
7. ✅ Deployed to Fly.io with `flyctl deploy`
8. ✅ Moved SECRET_KEY to environment variables
9. ⚠️ Alembic migrations (not yet set up - see Database & Infrastructure TODO)
10. ✅ Tested production deployment end-to-end

**Prerequisites met:**
- ✅ Docker Desktop installed
- ✅ Fly.io CLI installed: `brew install flyctl`
- ✅ Fly.io account created (free tier)
