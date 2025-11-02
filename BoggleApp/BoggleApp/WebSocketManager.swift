//
// ABOUTME: WebSocket manager for real-time game communication.
// ABOUTME: Handles connection, message sending/receiving, and game state updates.
//

import Foundation
import Combine

// MARK: - WebSocket Messages

struct SubmitWordMessage: Codable {
    let type: String = "submit_word"
    let word: String
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
    let time_remaining: Int?
    let player_count: Int
}

struct PlayerWordResult: Codable {
    let word: String
    let score: Int
    let valid: Bool
}

struct PlayerFinalResult: Codable {
    let player_name: String
    let words: [PlayerWordResult]
    let total_score: Int
}

struct GameEndedMessage: Codable {
    let type: String
    let winner: String?
    let results: [PlayerFinalResult]
}

struct GameStartedMessage: Codable {
    let type: String
    let board: [[String]]
    let time_limit: Int?
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
    private let maxReconnectAttempts = 5
    private var reconnectTask: Task<Void, Never>?

    var onWordResult: ((WordResultMessage) -> Void)?
    var onGameEnded: ((GameEndedMessage) -> Void)?
    var onGameStarted: ((GameStartedMessage) -> Void)?
    var onGameState: ((GameStateMessage) -> Void)?

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
        reconnectAttempts = 0  // Reset on successful connection

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
                        self.timeRemaining = state.time_remaining
                        self.onGameState?(state)
                        print("✅ Game state: \(state.status), time: \(state.time_remaining ?? 0)s")
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
