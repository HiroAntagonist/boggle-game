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
                .font(.system(size: 36, weight: .black, design: .rounded))
                .foregroundStyle(
                    LinearGradient(
                        colors: [.nebulaAccent, .nebulaPrimary],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .shadow(color: .nebulaPrimary.opacity(0.5), radius: 10, x: 0, y: 5)

            // Share code card
            VStack(spacing: 12) {
                Text("Share this code")
                    .font(.subheadline)
                    .foregroundStyle(Color.nebulaTextSecondary)

                Text(friendlyCode)
                    .font(.system(size: 40, weight: .bold, design: .monospaced))
                    .foregroundStyle(Color.nebulaAccent)
                    .tracking(4)
                    .textSelection(.enabled)
                    .nebulaGlow(color: .nebulaAccent, radius: 8)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.nebulaSurface.opacity(0.5))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.nebulaAccent.opacity(0.3), lineWidth: 1)
                    )
            )

            // Players section
            VStack(spacing: 15) {
                Text("\(players.count)/\(maxPlayers) Players")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .foregroundStyle(.white)

                VStack(spacing: 8) {
                    ForEach(players, id: \.self) { player in
                        HStack {
                            Image(systemName: "person.fill")
                                .foregroundStyle(Color.nebulaAccent)
                            Text(player)
                                .foregroundStyle(.white)
                            Spacer()
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundStyle(Color.nebulaSuccess)
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color.nebulaSurface.opacity(0.6))
                        )
                    }

                    // Empty slots
                    ForEach(0..<(maxPlayers - players.count), id: \.self) { _ in
                        HStack {
                            Image(systemName: "person.fill")
                                .foregroundStyle(Color.nebulaTextSecondary.opacity(0.5))
                            Text("Waiting...")
                                .foregroundStyle(Color.nebulaTextSecondary)
                            Spacer()
                            ProgressView()
                                .tint(Color.nebulaTextSecondary)
                                .scaleEffect(0.8)
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color.nebulaSurface.opacity(0.3))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(Color.white.opacity(0.05), lineWidth: 1)
                                )
                        )
                    }
                }
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 20)
                    .fill(Color.nebulaSurface.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: 20)
                            .stroke(Color.white.opacity(0.1), lineWidth: 1)
                    )
            )

            if let error = errorMessage {
                Text(error)
                    .foregroundStyle(Color.nebulaError)
                    .font(.caption)
                    .padding(8)
                    .background(Color.nebulaError.opacity(0.1))
                    .cornerRadius(8)
            }

            Button {
                Task {
                    await startGame()
                }
            } label: {
                HStack {
                    Image(systemName: "play.fill")
                    Text("Start Game")
                }
                .frame(maxWidth: .infinity)
            }
            .nebulaButtonStyle(color: .nebulaPrimary)
            .disabled(isStarting || players.count < 1)

            if isStarting {
                ProgressView()
                    .tint(.nebulaAccent)
            }

            Button {
                leaveGame()
            } label: {
                HStack {
                    Image(systemName: "xmark.circle")
                    Text("Leave Game")
                }
            }
            .nebulaButtonStyle(color: .nebulaSurface)

            Text("Game will auto-start when \(maxPlayers) players join")
                .font(.caption)
                .foregroundStyle(Color.nebulaTextSecondary)
        }
        .padding()
        .withNebulaBackground()
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
        }
    }

    private func loadGameState() async {
        do {
            // Get current game state
            let gameState = try await JumbleAPI.shared.getGameState(gameId: gameId)
            board = gameState.board
            players = gameState.players
            timeLimit = gameState.timeLimit
            startedAt = gameState.startedAt

            // Check if game has already started (handles race condition where game
            // auto-started before we connected to WebSocket)
            if gameState.status == "in_progress" {
                navigateToGame = true
                return
            }

            // Connect WebSocket to listen for game events
            let wsManager = WebSocketManager(gameId: gameId, playerId: playerId)

            // Listen for player_joined messages to update the player list
            wsManager.onPlayerJoined = { joinedMessage in
                self.players = joinedMessage.players
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
            try await JumbleAPI.shared.startGame(gameId: gameId)

            // Get updated game state with started_at timestamp
            let gameState = try await JumbleAPI.shared.getGameState(gameId: gameId)
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

    private func leaveGame() {
        Task {
            do {
                // Call backend API to remove player from game
                try await JumbleAPI.shared.leaveGame(gameId: gameId)
            } catch {
                print("⚠️ Failed to leave game on backend: \(error.localizedDescription)")
                // Continue with local cleanup even if API call fails
            }

            // Disconnect WebSocket
            webSocketManager?.disconnect()

            // Clear active game state
            JumbleAPI.shared.clearActiveGame()

            // Navigate back to lobby by removing all items from navigation path
            navigationPath.removeLast(navigationPath.count)
        }
    }
}

#Preview {
    WaitingRoomView(navigationPath: .constant(NavigationPath()), gameId: "preview-game-123", playerId: "preview-player-456", maxPlayers: 2, friendlyCode: "1234-5678")
}
