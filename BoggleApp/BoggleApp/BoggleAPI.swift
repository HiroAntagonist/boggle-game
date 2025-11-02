//
// ABOUTME: API client for communicating with the Boggle backend server.
// ABOUTME: Handles authentication, game management, and word submission via REST endpoints.
//

import Foundation

// MARK: - API Models

struct RegisterRequest: Codable {
    let username: String
    let email: String
    let password: String
}

struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct LoginResponse: Codable {
    let access_token: String
    let token_type: String
}

struct CreateGameRequest: Codable {
    let board_size: Int
    let time_limit_seconds: Int
    let max_players: Int
}

struct CreateGameResponse: Codable {
    let game_id: String
    let board: [[String]]
    let created_at: String
    let status: String
}

struct GameResponse: Codable {
    let game_id: String
    let board: [[String]]
    let status: String
    let time_remaining: Int?
    let players: [String]
}

struct JoinGameRequest: Codable {
    let player_name: String
}

struct JoinGameResponse: Codable {
    let player_id: String
    let player_name: String
    let players: [String]
}

// MARK: - API Client

class BoggleAPI {
    static let shared = BoggleAPI()

    private let baseURL = "https://boggle-game-ar.fly.dev"
    private var accessToken: String?

    private init() {}

    // Helper to check if HTTP status code indicates success
    private func isSuccessStatusCode(_ code: Int) -> Bool {
        return code == 200 || code == 201
    }

    // MARK: - Authentication

    func register(username: String, email: String, password: String) async throws {
        let request = RegisterRequest(username: username, email: email, password: password)
        let url = URL(string: "\(baseURL)/auth/register")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        print("🔵 Registering user: \(username)")

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
                throw APIError.registrationFailed("Validation error - check username (min 3 chars), email format, and password (min 8 chars)")
            }

            throw APIError.registrationFailed("Status code: \(httpResponse.statusCode)")
        }

        print("✅ Registration successful!")
    }

    func login(username: String, password: String) async throws {
        let request = LoginRequest(username: username, password: password)
        let url = URL(string: "\(baseURL)/auth/login")!

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        print("🔵 Logging in user: \(username)")

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
        self.accessToken = loginResponse.access_token
        print("✅ Login successful!")
    }

    // MARK: - Game Management

    func createGame(boardSize: Int = 4, timeLimitSeconds: Int = 180, maxPlayers: Int = 4) async throws -> CreateGameResponse {
        guard let token = accessToken else {
            throw APIError.notAuthenticated
        }

        let request = CreateGameRequest(
            board_size: boardSize,
            time_limit_seconds: timeLimitSeconds,
            max_players: maxPlayers
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

        let request = JoinGameRequest(player_name: playerName)
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
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Join game error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.joinGameFailed
        }

        print("✅ Joined game successfully!")
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
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Start game error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.startGameFailed
        }

        print("✅ Game started successfully!")
    }

    func getGameState(gameId: String) async throws -> GameResponse {
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
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ Get game state error (\(httpResponse.statusCode)): \(errorString)")
            }
            throw APIError.fetchGameFailed
        }

        return try JSONDecoder().decode(GameResponse.self, from: data)
    }
}

// MARK: - Errors

enum APIError: Error, LocalizedError {
    case notAuthenticated
    case registrationFailed(String)
    case loginFailed
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
            return "Login failed. Check your username and password"
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
