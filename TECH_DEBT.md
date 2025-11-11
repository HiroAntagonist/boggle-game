# Technical Debt & Improvements

## Authentication & Security

### High Priority
- [ ] **Add Client ID validation**: OAuth endpoint should validate that the Client ID in the ID token matches our expected Client ID for additional security
- [ ] **Implement refresh tokens**: Currently using 30-day JWT tokens; should implement refresh token mechanism for better security
- [ ] **Add rate limiting**: OAuth endpoint needs rate limiting to prevent abuse

### Medium Priority
- [ ] **Support additional OAuth providers**: Currently only Google; could add Apple Sign-In, GitHub, etc.
- [ ] **Add user email verification**: Email/password registrations should verify email addresses
- [ ] **Implement account deletion**: Users should be able to delete their accounts (GDPR compliance)

## Database & Infrastructure

### High Priority
- [ ] **Database migrations**: Currently using `Base.metadata.create_all()` which doesn't handle schema changes; need proper migration tool (Alembic)
- [ ] **Add database connection pooling monitoring**: Log pool metrics to catch connection leaks

### Medium Priority
- [ ] **Add database backups**: Set up automated backups for production PostgreSQL database
- [ ] **Document database connection setup**: Create clear documentation for connecting to correct database (`boggle_game_ar` vs `postgres`)

## iOS App

### High Priority
- [ ] **Replace manual models with generated ones**: BoggleAPI.swift has manually defined models; should use OpenAPI-generated models from `BoggleApp/Generated/Sources/OpenAPIClient/Models/`
- [ ] **Add OAuth error handling**: Better error messages for OAuth failures (network errors, invalid tokens, etc.)
- [ ] **Implement secure token storage**: Currently storing JWT token in memory; should use iOS Keychain

### Medium Priority
- [ ] **Add loading states**: OAuth login should show loading indicator during token exchange
- [ ] **Add biometric authentication**: Support Face ID/Touch ID for repeat logins
- [ ] **Handle OAuth token expiration**: Gracefully handle expired JWT tokens and prompt re-authentication

### Low Priority
- [ ] **Add OAuth sign-out**: Implement sign-out that clears both app state and Google Sign-In session

## Testing

### High Priority
- [ ] **Add integration tests**: End-to-end OAuth flow testing with real database
- [ ] **Add iOS unit tests**: Test OAuth flow, error handling, and token management

### Medium Priority
- [ ] **Add API contract tests**: Verify iOS models match backend Pydantic models
- [ ] **Test account linking scenarios**: Comprehensive tests for all account linking edge cases

## Code Quality

### Medium Priority
- [ ] **Extract OAuth verification logic**: Move Google ID token verification to separate service class
- [ ] **Add OpenAPI documentation**: Document OAuth endpoint in FastAPI's auto-generated docs
- [ ] **Standardize error responses**: Create consistent error response format across all endpoints

### Low Priority
- [ ] **Clean up background Bash shells**: Many long-running background processes from deployment/debugging
- [ ] **Remove or document fly.toml untracked file**: Current git status shows untracked `fly.toml`

## Documentation

### High Priority
- [ ] **Document OAuth setup process**: Step-by-step guide for setting up Google Cloud OAuth credentials
- [ ] **Document deployment process**: Clear instructions for deploying backend changes to Fly.io

### Medium Priority
- [ ] **Document database queries**: Add commonly used database queries to CLAUDE.md
- [ ] **Update API documentation**: Add OAuth endpoints to API documentation

## Completed (Reference)
- [x] Implement Google OAuth authentication
- [x] Add account linking by email
- [x] Auto-registration for OAuth users
- [x] Pull display name from Google profile
- [x] Add comprehensive OAuth tests
- [x] Fix JSON encoding mismatch (camelCase/snake_case)
- [x] Deploy OAuth to production
- [x] Verify end-to-end OAuth flow
