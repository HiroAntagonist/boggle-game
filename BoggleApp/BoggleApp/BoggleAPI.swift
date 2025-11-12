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

class BoggleAPI {
    static let shared = BoggleAPI()

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

    // MARK: - Game Management

    func createGame(boardSize: Int = 4, timeLimitSeconds: Int = 180, maxPlayers: Int = 4) async throws -> CreateGameResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let request = CreateGameRequest(
            boardSize: boardSize,
            timeLimitSeconds: timeLimitSeconds,
            maxPlayers: maxPlayers
        )
        let url = URL(string: "\(baseURL)/games")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        urlRequest.httpBody = try JSONEncoder().encode(request)

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

        print("✅ Game created successfully!")
        return try JSONDecoder().decode(CreateGameResponse.self, from: data)
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

        print("✅ Joined game successfully!")
        return try JSONDecoder().decode(JoinGameResponse.self, from: data)
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

        print("✅ Joined game by code successfully!")
        return try JSONDecoder().decode(JoinGameResponse.self, from: data)
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

    func getGameState(gameId: String) async throws -> GameStateResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let url = URL(string: "\(baseURL)/games/\(gameId)")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

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

        return try JSONDecoder().decode(GameStateResponse.self, from: data)
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
        }
    }
}

// MARK: - Request/Response Models
// All models are now imported from OpenAPIClient (generated from backend schema)
