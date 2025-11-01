# Backend API Summary

Quick reference for iOS development - what endpoints exist and how to use them.

## Base URL
- **Local**: `http://localhost:8000`
- **Production**: `https://boggle-game-ar.fly.dev`

## Authentication

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "player1",
  "email": "player1@example.com",
  "password": "securepass123"
}

Response 200:
{
  "user_id": "uuid",
  "username": "player1",
  "message": "User registered successfully"
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "player1",
  "password": "securepass123"
}

Response 200:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Use token in all subsequent requests:**
```
Authorization: Bearer eyJhbGc...
```

## Game Management

### Create Game
```http
POST /games
Authorization: Bearer <token>
Content-Type: application/json

{
  "board_size": 4,
  "time_limit_seconds": 180,
  "max_players": 4
}

Response 200:
{
  "game_id": "uuid",
  "board": [["D","R","A","T"], ...],
  "created_at": "2025-11-01T20:52:01.260275",
  "status": "waiting"
}
```

### Join Game
```http
POST /games/{game_id}/players
Authorization: Bearer <token>

Response 200:
{
  "game_id": "uuid",
  "player_id": "uuid",
  "message": "Player joined successfully"
}
```

### Start Game
```http
POST /games/{game_id}/start
Authorization: Bearer <token>

Response 200:
{
  "game_id": "uuid",
  "status": "in_progress",
  "started_at": "2025-11-01T21:00:00.123456"
}
```

### Get Game State
```http
GET /games/{game_id}
Authorization: Bearer <token>

Response 200:
{
  "game_id": "uuid",
  "board": [["D","R","A","T"], ...],
  "status": "in_progress",
  "time_limit_seconds": 180,
  "created_at": "...",
  "started_at": "...",
  "players": [
    {"player_id": "uuid", "username": "player1"},
    ...
  ]
}
```

### Get Results
```http
GET /games/{game_id}/results
Authorization: Bearer <token>

Response 200:
{
  "game_id": "uuid",
  "status": "finished",
  "players": [
    {
      "username": "player1",
      "score": 15,
      "words_found": ["cat", "dog", "tree"],
      "valid_words": ["cat", "dog"],
      "invalid_words": ["xyz"],
      "duplicate_words": ["tree"]
    },
    ...
  ]
}
```

## WebSocket Real-Time Game

### Connect
```
ws://localhost:8000/ws/{game_id}/{player_id}
wss://boggle-game-ar.fly.dev/ws/{game_id}/{player_id}
```

**Authentication:** Include JWT token in connection (implementation varies by client)

### Client → Server Messages

**Submit Word:**
```json
{
  "type": "submit_word",
  "word": "CAT"
}
```

**Get State:**
```json
{
  "type": "get_state"
}
```

### Server → Client Messages

**Word Result (to submitter):**
```json
{
  "type": "word_result",
  "word": "CAT",
  "valid": true,
  "reason": "Valid word!",
  "score": 1
}
```

**Word Submitted Broadcast (to all players):**
```json
{
  "type": "word_submitted",
  "player": "player1",
  "word": "CAT"
}
```

**Player Connected:**
```json
{
  "type": "player_connected",
  "player": "player1"
}
```

**Player Disconnected:**
```json
{
  "type": "player_disconnected",
  "player": "player1"
}
```

**Game State:**
```json
{
  "type": "game_state",
  "status": "in_progress",
  "board": [["D","R","A","T"], ...],
  "time_remaining": 120,
  "players": [
    {
      "username": "player1",
      "words_found": ["cat", "dog"],
      "score": 3
    }
  ]
}
```

## Game Rules

### Board
- 4x4 or 5x5 grid
- Standard Boggle dice distribution
- Letters randomly placed

### Word Validation
- Minimum 3 letters
- Must exist in SOWPODS dictionary
- Must form connected path on board
- Adjacent cells (including diagonals)
- Each cell used once per word

### Scoring (Fibonacci)
- 3 letters: 1 point
- 4 letters: 2 points
- 5 letters: 3 points
- 6 letters: 5 points
- 7 letters: 8 points
- 8+ letters: 13 points

### Multiplayer Strike-Out
- Words found by multiple players score 0 for all
- Final scoring happens at game end

### Timer
- Configurable time limit (default 180 seconds)
- Game ends when time expires
- No word submissions after time expires

## Database Schema

### User
- id (UUID, primary key)
- username (unique)
- email (unique)
- hashed_password
- created_at

### Game
- id (UUID, primary key)
- board_state (JSON array)
- board_size (4 or 5)
- time_limit_seconds
- max_players
- status (waiting, in_progress, finished)
- created_at
- started_at (nullable)
- creator_id (foreign key to User)

### GamePlayer
- id (UUID, primary key)
- game_id (foreign key to Game)
- user_id (foreign key to User)
- score
- words_found (JSON array)
- joined_at

## Error Responses

All errors return appropriate HTTP status codes with JSON:

```json
{
  "detail": "Error message here"
}
```

Common status codes:
- 400: Bad request (validation error)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (not a participant)
- 404: Not found (game/user doesn't exist)
- 500: Internal server error

## Testing the API

**Interactive docs:** https://boggle-game-ar.fly.dev/docs

**Example flow:**
1. Register user
2. Login (get token)
3. Create game (get game_id)
4. Join game (get player_id)
5. Start game
6. Connect WebSocket: ws://host/ws/{game_id}/{player_id}
7. Submit words via WebSocket
8. Get results when game ends

