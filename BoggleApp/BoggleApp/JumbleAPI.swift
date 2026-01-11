//
// ABOUTME: API client for communicating with the Boggle backend server.
// ABOUTME: Handles authentication, game management, and word submission via REST endpoints.
//

import Foundation
import OpenAPIClient

// MARK: - Notification Names

extension Notification.Name {
    static let forceLogout = Notification.Name("forceLogout")
}

// MARK: - API Client

class JumbleAPI {
    static let shared = JumbleAPI()

    private let baseURL = "https://boggle-game-ar.fly.dev"
    private let keychain = KeychainService.shared

    private init() {
        // Load token from Keychain on init for auto-authentication
        if keychain.hasToken() {
            print("✅ Found saved token in Keychain")
        }
    }

    /// Get current access token from Keychain
    private var accessToken: String? {
        return keychain.loadToken()
    }

    /// Check if user is authenticated
    var isAuthenticated: Bool {
        return keychain.hasToken()
    }

    /// Log out user by clearing token from Keychain
    func logout() {
        keychain.deleteToken()
        clearActiveGame()
        print("✅ User logged out")
    }

    /// Delete Account
    func deleteAccount() async throws {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let url = URL(string: "\(baseURL)/auth/me")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "DELETE"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        print("🔴 Deleting account")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
             throw APIError.loginFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
             if let errorString = String(data: data, encoding: .utf8) {
                 print("❌ Delete account error (\(httpResponse.statusCode)): \(errorString)")
             }
             throw APIError.loginFailed
         }

         print("✅ Account deleted successfully")
         logout()
    }

    /// Handle 401 Unauthorized - token is invalid (user deleted from database)
    private func handleUnauthorized(_ statusCode: Int) {
        if statusCode == 401 {
            print("⚠️ 401 Unauthorized - Token invalid, forcing logout")
            logout()
            // Post notification to force re-login in UI
            NotificationCenter.default.post(name: .forceLogout, object: nil)
        }
    }

    /// Get current user info from JWT token
    func getCurrentUser() -> (email: String, displayName: String?)? {
        guard let token = accessToken else { return nil }

        // JWT format: header.payload.signature
        let parts = token.components(separatedBy: ".")
        guard parts.count == 3 else {
            print("❌ Invalid JWT format")
            return nil
        }

        // Decode the payload (second part)
        let payload = parts[1]

        // Base64url decode - need to handle padding
        var base64 = payload
            .replacingOccurrences(of: "-", with: "+")
            .replacingOccurrences(of: "_", with: "/")

        // Add padding if needed
        let remainder = base64.count % 4
        if remainder > 0 {
            base64 += String(repeating: "=", count: 4 - remainder)
        }

        guard let data = Data(base64Encoded: base64),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let email = json["email"] as? String else {
            print("❌ Failed to decode JWT payload")
            return nil
        }

        let displayName = json["display_name"] as? String
        return (email: email, displayName: displayName)
    }

    // Helper to check if HTTP status code indicates success
    private func isSuccessStatusCode(_ code: Int) -> Bool {
        return code == 200 || code == 201
    }

    // MARK: - Authentication

    func register(email: String, password: String, displayName: String? = nil) async throws {
        let request = RegisterRequest(email: email, password: password, displayName: displayName)
        let url = URL(string: "\(baseURL)/auth/register")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        print("🔵 Registering user: \(email)")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.registrationFailed("Invalid response from server")
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            // Try to parse error message from response
            if let errorBody = try? JSONDecoder().decode([String: String].self, from: data),
               let detail = errorBody["detail"] {
                throw APIError.registrationFailed(detail)
            }

            // Try to parse Pydantic validation errors
            if httpResponse.statusCode == 422,
               let errorString = String(data: data, encoding: .utf8) {
                print("❌ Validation error: \(errorString)")
                throw APIError.registrationFailed("Validation error - check email format and password (min 8 chars)")
            }

            throw APIError.registrationFailed("Status code: \(httpResponse.statusCode)")
        }

        print("✅ Registration successful!")
    }

    func login(email: String, password: String) async throws {
        let request = LoginRequest(email: email, password: password)
        let url = URL(string: "\(baseURL)/auth/login")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        print("🔵 Logging in user: \(email)")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.loginFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Login error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.loginFailed
        }

        let loginResponse = try JSONDecoder().decode(LoginResponse.self, from: data)
        if keychain.saveToken(loginResponse.accessToken) {
            print("✅ Login successful!")
        } else {
            print("⚠️ Login successful but failed to save token to Keychain")
        }
    }

    func loginWithGoogle(idToken: String) async throws {
        let request = GoogleAuthRequest(idToken: idToken)
        let url = URL(string: "\(baseURL)/auth/google")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        print("🔵 Logging in with Google")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.googleAuthFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Google auth error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.googleAuthFailed
        }

        let loginResponse = try JSONDecoder().decode(LoginResponse.self, from: data)
        if keychain.saveToken(loginResponse.accessToken) {
            print("✅ Google login successful!")
        } else {
            print("⚠️ Google login successful but failed to save token to Keychain")
        }
    }

    /// Login with Apple
    func loginWithApple(idToken: String, nonce: String? = nil) async throws {
        // Create request object
        // Note: passing nonce/user if we had them and model supported it, but our minimal model just takes idToken
        let request = AppleAuthRequest(idToken: idToken)

        let url = URL(string: "\(baseURL)/auth/apple")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        print("🔵 Logging in with Apple")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.loginFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
             if let errorString = String(data: data, encoding: .utf8) {
                 print("❌ Apple auth error (\(httpResponse.statusCode)): \(errorString)")
             }
             throw APIError.loginFailed
         }

        let loginResponse = try JSONDecoder().decode(LoginResponse.self, from: data)

        if keychain.saveToken(loginResponse.accessToken) {
             print("✅ Apple login successful!")
        }
    }

    // MARK: - Game Management

    func createGame(boardSize: Int = 4, timeLimitSeconds: Int = 180, maxPlayers: Int = 4, isPublic: Bool = false) async throws -> CreateGameResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let request = CreateGameRequest(
            boardSize: boardSize,
            timeLimitSeconds: timeLimitSeconds,
            maxPlayers: maxPlayers,
            isPublic: isPublic
        )
        let url = URL(string: "\(baseURL)/games")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        print("🔵 Creating game: boardSize=\(boardSize), timeLimit=\(timeLimitSeconds)s, maxPlayers=\(maxPlayers), isPublic=\(isPublic)")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.gameCreationFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            handleUnauthorized(httpResponse.statusCode)
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Game creation error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.gameCreationFailed
        }

        let game = try JSONDecoder().decode(CreateGameResponse.self, from: data)
        print("✅ Game created successfully: gameId=\(game.gameId), code=\(game.friendlyCode)")
        return game
    }

    func joinGame(gameId: String, playerName: String = "Player") async throws -> JoinGameResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let request = JoinGameRequest(playerName: playerName)
        let url = URL(string: "\(baseURL)/games/\(gameId)/players")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        print("🔵 Joining game: \(gameId) as \(playerName)")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.joinGameFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            handleUnauthorized(httpResponse.statusCode)
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Join game error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.joinGameFailed
        }

        let joinResponse = try JSONDecoder().decode(JoinGameResponse.self, from: data)
        print("✅ Joined game successfully: playerId=\(joinResponse.playerId), status=\(joinResponse.status)")
        return joinResponse
    }

    func joinGameByCode(friendlyCode: String, playerName: String = "Player") async throws -> JoinGameResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let request = JoinGameRequest(playerName: playerName)
        let url = URL(string: "\(baseURL)/games/code/\(friendlyCode)/join")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        print("🔵 Joining game with code: \(friendlyCode) as \(playerName)")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.joinGameFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            handleUnauthorized(httpResponse.statusCode)
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Join game by code error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.joinGameFailed
        }

        let joinResponse = try JSONDecoder().decode(JoinGameResponse.self, from: data)
        print("✅ Joined game by code successfully: gameId=\(joinResponse.gameId), playerId=\(joinResponse.playerId), status=\(joinResponse.status)")
        return joinResponse
    }

    func startGame(gameId: String) async throws {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let url = URL(string: "\(baseURL)/games/\(gameId)/start")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        print("🔵 Starting game: \(gameId)")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.startGameFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            handleUnauthorized(httpResponse.statusCode)
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Start game error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.startGameFailed
        }

        print("✅ Game started successfully!")
    }

    func leaveGame(gameId: String) async throws {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let url = URL(string: "\(baseURL)/games/\(gameId)/leave")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        print("👋 Leaving game: \(gameId)")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.leaveGameFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            handleUnauthorized(httpResponse.statusCode)
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Leave game error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.leaveGameFailed
        }

        print("✅ Left game successfully!")
    }

    func getGameState(gameId: String) async throws -> GameStateResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let url = URL(string: "\(baseURL)/games/\(gameId)")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        print("🔵 Getting game state: \(gameId)")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.fetchGameFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            handleUnauthorized(httpResponse.statusCode)
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Get game state error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.fetchGameFailed
        }

        let gameState = try JSONDecoder().decode(GameStateResponse.self, from: data)
        print("✅ Game state fetched: status=\(gameState.status), players=\(gameState.players.count)")
        return gameState
    }

    // MARK: - User Profile & Stats

    func getCurrentUserProfile() async throws -> UserResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let url = URL(string: "\(baseURL)/auth/me")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        print("🔵 Fetching current user profile")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.fetchGameFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            handleUnauthorized(httpResponse.statusCode)
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Fetch profile error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.fetchGameFailed
        }

        let userResponse = try JSONDecoder().decode(UserResponse.self, from: data)
        print("✅ Profile fetched: email=\(userResponse.email), gamerTag=\(userResponse.gamerTag ?? "nil")")
        return userResponse
    }

    func updateProfile(gamerTag: String?) async throws -> UserResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let request = UpdateProfileRequest(gamerTag: gamerTag)
        let url = URL(string: "\(baseURL)/auth/profile")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "PATCH"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        print("🔵 Updating profile: gamerTag=\(gamerTag ?? "nil")")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.updateProfileFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            handleUnauthorized(httpResponse.statusCode)
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Update profile error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.updateProfileFailed
        }

        let userResponse = try JSONDecoder().decode(UserResponse.self, from: data)
        print("✅ Profile updated successfully: gamerTag=\(userResponse.gamerTag ?? "nil")")
        return userResponse
    }

    func getUserStats() async throws -> UserStatsResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let url = URL(string: "\(baseURL)/users/me/stats")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        print("🔵 Fetching user stats")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.fetchStatsFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            handleUnauthorized(httpResponse.statusCode)
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Fetch stats error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.fetchStatsFailed
        }

        let stats = try JSONDecoder().decode(UserStatsResponse.self, from: data)
        print("✅ Stats fetched: games=\(stats.totalGames), wins=\(stats.totalWins)")
        return stats
    }

    func getLeaderboard(limit: Int = 10) async throws -> LeaderboardResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let url = URL(string: "\(baseURL)/leaderboard?limit=\(limit)")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        print("🔵 Fetching leaderboard (limit=\(limit))")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.fetchLeaderboardFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            handleUnauthorized(httpResponse.statusCode)
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Fetch leaderboard error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.fetchLeaderboardFailed
        }

        let leaderboard = try JSONDecoder().decode(LeaderboardResponse.self, from: data)
        print("✅ Leaderboard fetched: \(leaderboard.leaderboard.count) entries")
        return leaderboard
    }

    func getPublicGames(limit: Int = 20) async throws -> PublicGamesResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let url = URL(string: "\(baseURL)/games/public?limit=\(limit)")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        print("🔵 Fetching public games (limit=\(limit))")

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.fetchPublicGamesFailed
        }

        if !isSuccessStatusCode(httpResponse.statusCode) {
            handleUnauthorized(httpResponse.statusCode)
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Fetch public games error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.fetchPublicGamesFailed
        }

        let publicGames = try JSONDecoder().decode(PublicGamesResponse.self, from: data)
        print("✅ Public games fetched: \(publicGames.games.count) games")
        return publicGames
    }

    // MARK: - Reconnection Support

    /// Save active game state for reconnection after app restart/crash
    func saveActiveGame(gameId: String, playerId: String) {
        UserDefaults.standard.set(gameId, forKey: "activeGameId")
        UserDefaults.standard.set(playerId, forKey: "activePlayerId")
        print("💾 Saved active game: \(gameId), player: \(playerId)")
    }

    /// Get saved active game state (if any)
    func getActiveGame() -> (gameId: String, playerId: String)? {
        guard let gameId = UserDefaults.standard.string(forKey: "activeGameId"),
              let playerId = UserDefaults.standard.string(forKey: "activePlayerId") else {
            return nil
        }
        return (gameId, playerId)
    }

    /// Clear saved game state (call when game ends)
    func clearActiveGame() {
        UserDefaults.standard.removeObject(forKey: "activeGameId")
        UserDefaults.standard.removeObject(forKey: "activePlayerId")
        print("🗑️  Cleared active game state")
    }

    /// Attempt to rejoin a previously active game
    func attemptReconnect() async throws -> JoinGameResponse? {
        guard let (gameId, playerId) = getActiveGame() else {
            print("ℹ️  No active game to reconnect to")
            return nil
        }

        print("🔄 Attempting to reconnect to game: \(gameId), player: \(playerId)")

        do {
            // Call the join endpoint - backend now allows rejoining!
            let response = try await joinGame(gameId: gameId, playerName: "Reconnecting")

            // Verify we got the same player_id back (sanity check)
            if response.playerId == playerId {
                print("✅ Successfully reconnected to game!")
                return response
            } else {
                print("⚠️  Reconnected but got different player_id - clearing old state")
                clearActiveGame()
                return nil
            }
        } catch {
            print("❌ Failed to reconnect: \(error.localizedDescription)")
            // Game might have ended or been deleted - clear saved state
            clearActiveGame()
            throw error
        }
    }
}

// MARK: - Errors

enum APIError: Error, LocalizedError {
    case notAuthenticated
    case registrationFailed(String)
    case loginFailed
    case googleAuthFailed
    case gameCreationFailed
    case joinGameFailed
    case startGameFailed
    case fetchGameFailed
    case updateProfileFailed
    case fetchStatsFailed
    case fetchLeaderboardFailed
    case fetchPublicGamesFailed
    case leaveGameFailed

    var errorDescription: String? {
        switch self {
        case .notAuthenticated:
            return "You must be logged in to perform this action"
        case .registrationFailed(let message):
            return "Registration failed: \(message)"
        case .loginFailed:
            return "Login failed. Check your email and password"
        case .googleAuthFailed:
            return "Google Sign-In failed. Please try again"
        case .gameCreationFailed:
            return "Failed to create game"
        case .joinGameFailed:
            return "Failed to join game"
        case .startGameFailed:
            return "Failed to start game"
        case .fetchGameFailed:
            return "Failed to fetch game state"
        case .updateProfileFailed:
            return "Failed to update profile"
        case .fetchStatsFailed:
            return "Failed to fetch user stats"
        case .fetchLeaderboardFailed:
            return "Failed to fetch leaderboard"
        case .fetchPublicGamesFailed:
            return "Failed to fetch public games"
        case .leaveGameFailed:
            return "Failed to leave game"
        }
    }
}

// MARK: - Request/Response Models
// All models are now imported from OpenAPIClient (generated from backend schema)
