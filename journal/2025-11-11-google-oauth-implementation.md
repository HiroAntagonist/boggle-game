# Google OAuth Implementation - November 11, 2025

## Overview
Successfully implemented Google OAuth authentication for the Boggle iOS app with full account linking, auto-registration, and display name extraction from Google profiles.

## Implementation Details

### Backend Changes (src/)
1. **Added Google OAuth library**: `google-auth==2.43.0` and `requests==2.32.5` to pyproject.toml
2. **Database already supported OAuth**: `password_hash` was already `Optional[str]` in User model (src/models.py:50)
3. **Created OAuth endpoint** (src/api_server.py:1314-1392):
   - Endpoint: `POST /auth/google`
   - Accepts: `GoogleAuthRequest` with `id_token` field
   - Verifies ID token with Google's servers using `google.oauth2.id_token.verify_oauth2_token()`
   - Auto-creates users if they don't exist
   - Links OAuth to existing email/password accounts
   - Extracts display name from Google profile (`idinfo.get('name')`)
   - Returns standard JWT token for API authentication
4. **Added OAuth models** (src/api_models.py:103-105): `GoogleAuthRequest` with `id_token` field
5. **Comprehensive tests** (tests/test_oauth.py): 8 test cases covering all OAuth scenarios

### iOS Changes (BoggleApp/)
1. **Added Google Sign-In SDK** via Swift Package Manager
2. **Created configuration files**:
   - `GoogleSignInConfig.swift`: Stores Client ID
   - `GoogleAuthService.swift`: Handles Google Sign-In flow using `GIDSignIn.sharedInstance.signIn()`
3. **Updated BoggleAPI.swift**:
   - Added `loginWithGoogle(idToken:)` method
   - **Critical fix**: Added `CodingKeys` enum to map `idToken` → `id_token` for JSON encoding (line 320-322)
4. **Updated LoginView.swift**: Added Google Sign-In button with OR divider
5. **Updated BoggleAppApp.swift**: Added `.onOpenURL` handler for OAuth callback
6. **Created Info.plist**: All required iOS bundle keys + OAuth URL scheme

### App Rebranding
- Changed bundle ID to `com.drishtilabs.Clauddle`
- Changed display name to "Clauddle"

## Issues Encountered and Fixed

### Issue 1: JSON Encoding Mismatch (422 Error)
**Problem**: iOS app sent `idToken` (camelCase) but backend expected `id_token` (snake_case)
**Error**: `{"detail":[{"type":"missing","loc":["body","id_token"],"msg":"Field required"}]}`
**Fix**: Added `CodingKeys` enum in `GoogleAuthRequest` struct (BoggleAPI.swift:320-322):
```swift
enum CodingKeys: String, CodingKey {
    case idToken = "id_token"
}
```

### Issue 2: Database Connection Confusion
**Problem**: Couldn't find users table when querying database
**Cause**: `flyctl postgres connect --app boggle-db` connects to default `postgres` database, but app uses `boggle_game_ar` database
**Solution**: Use `flyctl postgres connect --app boggle-db --database boggle_game_ar`
**Databases in boggle-db**:
- `boggle_game_ar` - actual app database ✓
- `postgres` - default PostgreSQL database
- `repmgr` - replication manager

### Issue 3: App Not Starting (Load Balancer Error)
**Problem**: "Machines are not listening on 0.0.0.0:8000"
**Cause**: Old deployment had missing `psycopg2-binary` dependency
**Error in logs**: `sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres`
**Fix**: Redeployment with correct dependencies fixed it (`psycopg2-binary` was already in pyproject.toml but needed fresh build)

## OAuth Flow (End-to-End)
1. User taps "Sign in with Google" in iOS app
2. Google Sign-In SDK (`GIDSignIn`) presents authentication UI
3. User authenticates with Google
4. SDK returns ID token to app
5. App sends ID token to `POST /auth/google` endpoint
6. Backend verifies ID token with Google's servers
7. Backend extracts email, name, and Google ID from verified token
8. Backend checks if user exists by email:
   - **If exists**: Links OAuth provider/ID to existing account
   - **If new**: Creates user with OAuth data, no password, display name from Google
9. Backend returns JWT token
10. App stores token and navigates to lobby

## Key Design Decisions

### Account Linking Strategy
- Email is the unique identifier across all authentication methods
- Users can have both email/password AND OAuth authentication on same account
- OAuth users have `password_hash = NULL` in database
- Display name automatically populated from Google profile

### Security
- Native Google Sign-In SDK (not web-based OAuth)
- ID token verification performed server-side with Google's official library
- JWT tokens with 30-day expiration for API authentication
- Race condition handling in user creation with IntegrityError catch

## Files Modified

### Backend
- `pyproject.toml`: Added google-auth and requests dependencies
- `src/api_models.py`: Added `GoogleAuthRequest` model
- `src/api_server.py`: Added `/auth/google` endpoint
- `tests/test_oauth.py`: Complete test suite (NEW FILE)

### iOS
- `BoggleApp.xcodeproj/project.pbxproj`: Updated bundle IDs and Info.plist config
- `GoogleSignInConfig.swift`: OAuth configuration (NEW FILE)
- `GoogleAuthService.swift`: Sign-in handler (NEW FILE)
- `BoggleAPI.swift`: Added `loginWithGoogle()` method with CodingKeys fix
- `LoginView.swift`: Added Google Sign-In button and handler
- `BoggleAppApp.swift`: Added OAuth URL handling
- `Info.plist`: Complete iOS app configuration (NEW FILE)

## Production Deployment
- Backend deployed to Fly.io with `flyctl deploy`
- Database: PostgreSQL on Fly.io (`boggle-db` app, `boggle_game_ar` database)
- All OAuth tests passing locally
- End-to-end OAuth flow verified in production

## Testing Results
- ✅ New user OAuth registration works
- ✅ Display name "Amritansh Raghav" pulled from Google profile
- ✅ User successfully logged into lobby
- ✅ Backend created user in `boggle_game_ar` database
- ✅ All 8 OAuth unit tests passing

## Important Database Commands
```bash
# Connect to correct database
flyctl postgres connect --app boggle-db --database boggle_game_ar

# List databases
flyctl postgres db list --app boggle-db

# Query users
SELECT email, display_name, oauth_provider, oauth_id, password_hash IS NOT NULL as has_password FROM users;
```

## OAuth Configuration
- **Client ID**: `100702603925-nvckevroeb4factu9je5remisk6i8316.apps.googleusercontent.com`
- **OAuth URL Scheme**: `com.googleusercontent.apps.100702603925-nvckevroeb4factu9je5remisk6i8316`
- **Backend Endpoint**: `https://boggle-game-ar.fly.dev/auth/google`

## Lessons Learned
1. **Always check JSON field naming** between client and server (camelCase vs snake_case)
2. **PostgreSQL instances can have multiple databases** - always specify which one to connect to
3. **Docker layer caching** can mask dependency issues - use `--no-cache` when debugging build problems
4. **CodingKeys enum in Swift** is essential for mapping property names to different JSON keys
5. **Fly.io deployment troubleshooting**: Check logs for startup failures, not just runtime errors
