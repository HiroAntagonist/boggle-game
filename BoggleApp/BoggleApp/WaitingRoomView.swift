//
// ABOUTME: Waiting room view showing connected players before game starts.
// ABOUTME: Displays player list, allows manual start, and auto-starts when room is full.
//

import SwiftUI
import OpenAPIClient

struct WaitingRoomView: View {
    @Binding var navigationPath: NavigationPath
    let gameId: String
    let playerId: String
    let maxPlayers: Int
    let friendlyCode: String

    @State private var players: [String] = []
    @State private var board: [[String]] = []
    @State private var timeLimit: Int?
    @State private var startedAt: String?
    @State private var isStarting = false
    @State private var errorMessage: String?
    @State private var webSocketManager: WebSocketManager?
    @State private var navigateToGame = false

    var body: some View {
        VStack(spacing: 25) {
            Text("Waiting Room")
                .font(.largeTitle)
                .fontWeight(.bold)

            VStack(spacing: 8) {
                Text("Share this code:")
                    .font(.headline)
                    .foregroundStyle(.secondary)

                Text(friendlyCode)
                    .font(.system(size: 36, weight: .bold, design: .monospaced))
                    .foregroundStyle(.purple)
                    .tracking(3)
                    .textSelection(.enabled)
                    .padding(.horizontal)
                    .padding(.vertical, 12)
                    .background(Color.purple.opacity(0.1))
                    .cornerRadius(10)
            }
            .padding(.bottom, 10)

            VStack(spacing: 10) {
                Text("\(players.count)/\(maxPlayers) Players")
                    .font(.title2)
                    .fontWeight(.semibold)

                List(players, id: \.self) { player in
                    HStack {
                        Image(systemName: "person.fill")
                            .foregroundStyle(.purple)
                        Text(player)
                    }
                }
                .frame(height: 200)
                .listStyle(.plain)
            }

            if let error = errorMessage {
                Text(error)
                    .foregroundStyle(.red)
                    .font(.caption)
            }

            Button("Start Game") {
                Task {
                    await startGame()
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(isStarting || players.count < 1)
            .font(.title3)

            if isStarting {
                ProgressView("Starting game...")
            }

            Text("Game will auto-start when \(maxPlayers) players join")
                .font(.caption)
                .foregroundStyle(.gray)
        }
        .padding()
        .task {
            await loadGameState()
        }
        .navigationDestination(isPresented: $navigateToGame) {
            if !board.isEmpty {
                GameView(navigationPath: $navigationPath, gameId: gameId, playerId: playerId, initialBoard: board, initialTimeLimit: timeLimit, initialStartedAt: startedAt, webSocketManager: webSocketManager)
            }
        }
        .navigationBarBackButtonHidden(true)
        .onDisappear {
            // Don't disconnect - GameView will reuse the same connection
            // The server handles reconnection automatically if needed
            print("🔵 WaitingRoomView disappeared (keeping WebSocket connected)")
        }
    }

    private func loadGameState() async {
        do {
            // Get current game state
            let gameState = try await BoggleAPI.shared.getGameState(gameId: gameId)
            board = gameState.board
            players = gameState.players
            timeLimit = gameState.timeLimit
            startedAt = gameState.startedAt

            // Check if game has already started (handles race condition where game
            // auto-started before we connected to WebSocket)
            if gameState.status == "in_progress" {
                print("✅ Game already started - navigating immediately")
                navigateToGame = true
                return
            }

            // Connect WebSocket to listen for game events
            let wsManager = WebSocketManager(gameId: gameId, playerId: playerId)

            // Listen for player_joined messages to update the player list
            wsManager.onPlayerJoined = { joinedMessage in
                self.players = joinedMessage.players
                print("✅ Updated player list: \(joinedMessage.players.joined(separator: ", "))")
            }

            // Listen for game_started messages (auto-start)
            wsManager.onGameStarted = { startMessage in
                // Auto-start: game started by another player or when room filled
                self.board = startMessage.board
                self.timeLimit = startMessage.timeLimit
                self.startedAt = startMessage.startedAt
                self.navigateToGame = true
            }

            wsManager.connect()
            webSocketManager = wsManager

        } catch let error as APIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "Failed to load game state"
        }
    }

    private func startGame() async {
        isStarting = true
        errorMessage = nil

        do {
            try await BoggleAPI.shared.startGame(gameId: gameId)

            // Get updated game state with started_at timestamp
            let gameState = try await BoggleAPI.shared.getGameState(gameId: gameId)
            board = gameState.board
            timeLimit = gameState.timeLimit
            startedAt = gameState.startedAt

            // Navigate to game
            navigateToGame = true

        } catch let error as APIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "Failed to start game"
        }

        isStarting = false
    }
}

#Preview {
    WaitingRoomView(navigationPath: .constant(NavigationPath()), gameId: "preview-game-123", playerId: "preview-player-456", maxPlayers: 2, friendlyCode: "1234-5678")
}
