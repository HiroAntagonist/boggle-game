//
// ABOUTME: WebSocket manager for real-time game communication.
// ABOUTME: Handles connection, message sending/receiving, and game state updates.
//

import Foundation
import Combine

// MARK: - WebSocket Messages

struct SubmitWordMessage: Codable {
    let type: String
    let word: String

    init(word: String) {
        self.type = "submit_word"
        self.word = word
    }
}

struct WordResultMessage: Codable, Equatable {
    let type: String
    let word: String
    let valid: Bool
    let score: Int
    let message: String
}

struct GameStateMessage: Codable {
    let type: String
    let status: String
    let timeRemaining: Int?
    let playerCount: Int

    enum CodingKeys: String, CodingKey {
        case type
        case status
        case timeRemaining = "time_remaining"
        case playerCount = "player_count"
    }
}

struct PlayerWordResult: Codable {
    let word: String
    let score: Int
    let valid: Bool
}

struct PlayerFinalResult: Codable {
    let playerName: String
    let words: [PlayerWordResult]
    let totalScore: Int

    enum CodingKeys: String, CodingKey {
        case playerName = "player_name"
        case words
        case totalScore = "total_score"
    }
}

struct GameEndedMessage: Codable {
    let type: String
    let winner: String?
    let results: [PlayerFinalResult]
}

struct GameStartedMessage: Codable {
    let type: String
    let board: [[String]]
    let startedAt: String
    let timeLimit: Int?

    enum CodingKeys: String, CodingKey {
        case type
        case board
        case startedAt = "started_at"
        case timeLimit = "time_limit"
    }
}

struct PlayerJoinedMessage: Codable {
    let type: String
    let playerName: String
    let playerCount: Int
    let maxPlayers: Int
    let players: [String]

    enum CodingKeys: String, CodingKey {
        case type
        case playerName = "player_name"
        case playerCount = "player_count"
        case maxPlayers = "max_players"
        case players
    }
}

// MARK: - WebSocket Manager

enum ConnectionStatus {
    case disconnected
    case connecting
    case connected
    case reconnecting
}

class WebSocketManager: ObservableObject {
    @Published var isConnected = false
    @Published var connectionStatus: ConnectionStatus = .disconnected
    @Published var lastWordResult: WordResultMessage?
    @Published var timeRemaining: Int?

    private var webSocketTask: URLSessionWebSocketTask?
    private let gameId: String
    private let playerId: String
    private var reconnectAttempts = 0
    private let maxReconnectAttempts = 3  // Reduced from 5 to avoid excessive retries on permanent failures
    private var reconnectTask: Task<Void, Never>?

    var onWordResult: ((WordResultMessage) -> Void)?
    var onGameEnded: ((GameEndedMessage) -> Void)?
    var onGameStarted: ((GameStartedMessage) -> Void)?
    var onGameState: ((GameStateMessage) -> Void)?
    var onPlayerJoined: ((PlayerJoinedMessage) -> Void)?

    init(gameId: String, playerId: String) {
        self.gameId = gameId
        self.playerId = playerId
    }

    func connect() {
        connectionStatus = .connecting

        // wss:// for production HTTPS, ws:// for local HTTP
        let urlString = "wss://boggle-game-ar.fly.dev/ws/\(gameId)/\(playerId)"
        guard let url = URL(string: urlString) else {
            print("❌ Invalid WebSocket URL")
            connectionStatus = .disconnected
            return
        }

        print("🔵 Connecting to WebSocket: \(urlString)")

        webSocketTask = URLSession.shared.webSocketTask(with: url)
        webSocketTask?.resume()
        isConnected = true
        connectionStatus = .connected
        // Note: reconnectAttempts is reset in handleMessage() after first successful message

        // Start listening for messages
        receiveMessage()

        print("✅ WebSocket connected")
    }

    func disconnect() {
        print("🔵 Disconnecting WebSocket")
        reconnectTask?.cancel()
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        isConnected = false
        connectionStatus = .disconnected
        print("✅ WebSocket disconnected")
    }

    private func attemptReconnect() {
        guard reconnectAttempts < maxReconnectAttempts else {
            print("❌ Max reconnection attempts reached")
            connectionStatus = .disconnected
            return
        }

        reconnectAttempts += 1
        connectionStatus = .reconnecting

        // Exponential backoff: 1s, 2s, 4s, 8s, 16s
        let delay = min(pow(2.0, Double(reconnectAttempts - 1)), 16.0)
        print("🔄 Reconnecting in \(delay)s (attempt \(reconnectAttempts)/\(maxReconnectAttempts))...")

        reconnectTask = Task {
            try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))

            guard !Task.isCancelled else { return }

            await MainActor.run {
                self.connect()
            }
        }
    }

    func submitWord(_ word: String) {
        let message = SubmitWordMessage(word: word.uppercased())

        guard let data = try? JSONEncoder().encode(message),
              let jsonString = String(data: data, encoding: .utf8) else {
            print("❌ Failed to encode word submission")
            return
        }

        print("🔵 Submitting word: \(word)")

        let wsMessage = URLSessionWebSocketTask.Message.string(jsonString)
        webSocketTask?.send(wsMessage) { error in
            if let error = error {
                print("❌ WebSocket send error: \(error)")
            } else {
                print("✅ Word submitted: \(word)")
            }
        }
    }

    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    self?.handleMessage(text)
                case .data(let data):
                    if let text = String(data: data, encoding: .utf8) {
                        self?.handleMessage(text)
                    }
                @unknown default:
                    break
                }

                // Keep listening for next message
                self?.receiveMessage()

            case .failure(let error):
                print("❌ WebSocket receive error: \(error)")
                self?.isConnected = false
                self?.connectionStatus = .disconnected

                // Attempt to reconnect
                self?.attemptReconnect()
            }
        }
    }

    private func handleMessage(_ text: String) {
        print("📩 Received: \(text)")

        // Reset reconnection counter on first successful message (proves connection works)
        if reconnectAttempts > 0 {
            print("✅ Connection verified - resetting reconnection counter")
            reconnectAttempts = 0
        }

        guard let data = text.data(using: .utf8) else { return }

        // Try to determine message type
        if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let type = json["type"] as? String {

            switch type {
            case "word_result":
                if let result = try? JSONDecoder().decode(WordResultMessage.self, from: data) {
                    DispatchQueue.main.async {
                        self.lastWordResult = result
                        self.onWordResult?(result)
                        print("✅ Word result: \(result.word) - \(result.valid ? "VALID" : "INVALID")")
                    }
                }

            case "game_state":
                if let state = try? JSONDecoder().decode(GameStateMessage.self, from: data) {
                    DispatchQueue.main.async {
                        self.timeRemaining = state.timeRemaining
                        self.onGameState?(state)
                        print("✅ Game state: \(state.status), time: \(state.timeRemaining ?? 0)s")
                    }
                }

            case "game_ended":
                if let endMessage = try? JSONDecoder().decode(GameEndedMessage.self, from: data) {
                    DispatchQueue.main.async {
                        self.onGameEnded?(endMessage)
                        print("🏁 Game ended! Winner: \(endMessage.winner ?? "TIE")")
                    }
                }

            case "game_started":
                if let startMessage = try? JSONDecoder().decode(GameStartedMessage.self, from: data) {
                    DispatchQueue.main.async {
                        self.onGameStarted?(startMessage)
                        print("🎮 Game started!")
                    }
                }

            case "player_joined":
                if let joinedMessage = try? JSONDecoder().decode(PlayerJoinedMessage.self, from: data) {
                    DispatchQueue.main.async {
                        self.onPlayerJoined?(joinedMessage)
                        print("👋 Player joined: \(joinedMessage.playerName) (\(joinedMessage.playerCount)/\(joinedMessage.maxPlayers))")
                    }
                }

            case "player_connected":
                print("👋 Player connected")

            case "player_disconnected":
                print("👋 Player disconnected")

            default:
                print("⚠️ Unknown message type: \(type)")
            }
        }
    }

    deinit {
        disconnect()
    }
}
