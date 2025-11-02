//
// ABOUTME: Waiting room view showing connected players before game starts.
// ABOUTME: Displays player list, allows manual start, and auto-starts when room is full.
//

import SwiftUI

struct WaitingRoomView: View {
    let gameId: String
    let playerId: String
    let maxPlayers: Int

    @State private var players: [String] = []
    @State private var board: [[String]] = []
    @State private var isStarting = false
    @State private var errorMessage: String?
    @State private var webSocketManager: WebSocketManager?
    @State private var navigateToGame = false

    var body: some View {
        VStack(spacing: 25) {
            Text("Waiting Room")
                .font(.largeTitle)
                .fontWeight(.bold)

            Text("Game ID: \(gameId)")
                .font(.caption)
                .foregroundStyle(.gray)
                .textSelection(.enabled)

            VStack(spacing: 10) {
                Text("\(players.count)/\(maxPlayers) Players")
                    .font(.title2)
                    .fontWeight(.semibold)

                List(players, id: \.self) { player in
                    HStack {
                        Image(systemName: "person.fill")
                            .foregroundStyle(.blue)
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
                GameView(gameId: gameId, playerId: playerId, initialBoard: board)
            }
        }
        .navigationBarBackButtonHidden(true)
    }

    private func loadGameState() async {
        do {
            // Get current game state
            let gameState = try await BoggleAPI.shared.getGameState(gameId: gameId)
            board = gameState.board
            players = gameState.players

            // Connect WebSocket to listen for game_started messages (auto-start)
            let wsManager = WebSocketManager(gameId: gameId, playerId: playerId)
            wsManager.onGameStarted = { startMessage in
                // Auto-start: game started by another player or when room filled
                self.board = startMessage.board
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
    WaitingRoomView(gameId: "preview-game-123", playerId: "preview-player-456", maxPlayers: 2)
}
