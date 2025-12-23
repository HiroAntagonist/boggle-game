//
// ABOUTME: Lobby view where players choose to create a new game or join an existing one.
// ABOUTME: Acts as the main menu after login, routing to game creation or game joining flows.
//

import SwiftUI
import OpenAPIClient

struct LobbyView: View {
    @Binding var isLoggedIn: Bool
    @State private var navigationPath = NavigationPath()
    @State private var userDisplayName: String?
    @State private var userEmail: String?
    @State private var isReconnecting = false
    @State private var reconnectError: String?
    @State private var reconnectedGameState: JoinGameResponse?
    @State private var navigateToReconnectedGame = false

    var body: some View {
        NavigationStack(path: $navigationPath) {
            VStack(spacing: 30) {
                Text("Jumble")
                    .font(.system(size: 48, weight: .black, design: .rounded))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.nebulaAccent, .nebulaPrimary],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .shadow(color: .nebulaPrimary.opacity(0.5), radius: 10, x: 0, y: 5)

                // Display logged-in user info
                if let displayName = userDisplayName {
                    Text("Welcome, \(displayName)!")
                        .font(.title3)
                        .foregroundStyle(Color.nebulaTextSecondary)
                } else if let email = userEmail {
                    Text("Logged in as \(email)")
                        .font(.caption)
                        .foregroundStyle(Color.nebulaTextSecondary)
                }

                Text("Ready to play?")
                    .font(.title2)
                    .foregroundStyle(Color.nebulaTextSecondary)

                VStack(spacing: 20) {
                    NavigationLink(value: "hostGame") {
                        HStack {
                            Image(systemName: "play.fill")
                            Text("Host Game")
                        }
                        .frame(maxWidth: .infinity)
                    }
                    .nebulaButtonStyle(color: .nebulaPrimary)

                    NavigationLink(value: "joinGame") {
                        HStack {
                            Image(systemName: "person.3.fill")
                            Text("Join Game")
                        }
                        .frame(maxWidth: .infinity)
                    }
                    .nebulaButtonStyle(color: .nebulaSurface)

                    NavigationLink(value: "leaderboard") {
                        HStack {
                            Image(systemName: "trophy.fill")
                            Text("Leaderboard")
                        }
                        .frame(maxWidth: .infinity)
                    }
                    .nebulaButtonStyle(color: .nebulaSurface)
                }
                .padding(.horizontal, 40)
            }
            .padding()
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    NavigationLink(value: "profile") {
                        Image(systemName: "person.circle")
                            .font(.title2)
                    }
                }
            }
            .onAppear {
                loadUserInfo()
                attemptReconnection()
            }
            .overlay {
                if isReconnecting {
                    ZStack {
                        Color.black.opacity(0.4)
                            .ignoresSafeArea()

                        VStack(spacing: 20) {
                            ProgressView()
                                .scaleEffect(1.5)

                            Text("Reconnecting to game...")
                                .font(.title3)
                                .foregroundStyle(.white)

                            if let error = reconnectError {
                                Text(error)
                                    .font(.caption)
                                    .foregroundStyle(.red)
                                    .padding()
                                    .background(Color.white)
                                    .cornerRadius(8)

                                Button("Continue") {
                                    isReconnecting = false
                                    reconnectError = nil
                                }
                                .buttonStyle(.borderedProminent)
                                .tint(.purple)
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationDestination(for: String.self) { destination in
                if destination == "hostGame" {
                    NewGameView(navigationPath: $navigationPath)
                } else if destination == "joinGame" {
                    JoinGameView(navigationPath: $navigationPath)
                } else if destination == "profile" {
                    ProfileView(isLoggedIn: $isLoggedIn)
                } else if destination == "leaderboard" {
                    LeaderboardView()
                } else if destination.hasPrefix("waitingRoom:") {
                    // Parse reconnection to waiting room: "waitingRoom:gameId:playerId:maxPlayers"
                    let parts = destination.split(separator: ":").map(String.init)
                    if parts.count == 4 {
                        WaitingRoomView(
                            navigationPath: $navigationPath,
                            gameId: parts[1],
                            playerId: parts[2],
                            maxPlayers: Int(parts[3]) ?? 2,
                            friendlyCode: "RECONNECTED"
                        )
                    } else {
                        EmptyView()
                    }
                } else {
                    EmptyView()
                }
            }
            .navigationDestination(isPresented: $navigateToReconnectedGame) {
                if let gameState = reconnectedGameState {
                    GameView(
                        navigationPath: $navigationPath,
                        gameId: gameState.gameId,
                        playerId: gameState.playerId,
                        initialBoard: gameState.board,
                        initialTimeLimit: gameState.timeLimit,
                        initialStartedAt: gameState.startedAt,
                        initialWords: gameState.wordsByPlayer[gameState.playerId] ?? []
                    )
                }
            }
        }
        .withNebulaBackground()
    }

    private func loadUserInfo() {
        if let user = JumbleAPI.shared.getCurrentUser() {
            userEmail = user.email
            userDisplayName = user.displayName
        }
    }

    private func attemptReconnection() {
        Task {
            isReconnecting = true
            reconnectError = nil

            do {
                if let gameState = try await JumbleAPI.shared.attemptReconnect() {
                    print("INFO [Reconnect] Rejoining game | status=\(gameState.status) game=\(gameState.gameId.prefix(8))")

                    // Save the active game state for future reconnections
                    JumbleAPI.shared.saveActiveGame(gameId: gameState.gameId, playerId: gameState.playerId)

                    // Navigate based on game status
                    switch gameState.status {
                    case "waiting":
                        navigationPath.append("waitingRoom:\(gameState.gameId):\(gameState.playerId):\(gameState.maxPlayers)")
                        isReconnecting = false

                    case "in_progress":
                        reconnectedGameState = gameState
                        navigateToReconnectedGame = true
                        isReconnecting = false

                    case "finished":
                        JumbleAPI.shared.clearActiveGame()
                        isReconnecting = false

                    default:
                        print("WARN [Reconnect] Unknown game status: \(gameState.status)")
                        JumbleAPI.shared.clearActiveGame()
                        isReconnecting = false
                    }

                } else {
                    isReconnecting = false
                }
            } catch {
                // Clear the saved game since it's invalid (game deleted, player removed, etc.)
                JumbleAPI.shared.clearActiveGame()
                // Silently dismiss - don't show error for stale game state
                isReconnecting = false
            }
        }
    }
}

#Preview {
    LobbyView(isLoggedIn: .constant(true))
}
