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
                Text("Clauddle")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                // Display logged-in user info
                if let displayName = userDisplayName {
                    Text("Welcome, \(displayName)!")
                        .font(.title3)
                        .foregroundStyle(.secondary)
                } else if let email = userEmail {
                    Text("Logged in as \(email)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Text("Ready to play?")
                    .font(.title2)
                    .foregroundStyle(.gray)

                VStack(spacing: 15) {
                    NavigationLink(value: "newGame") {
                        Text("New Game")
                            .frame(width: 200)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.purple)
                    .font(.title3)

                    NavigationLink(value: "joinGame") {
                        Text("Join Game")
                            .frame(width: 200)
                    }
                    .buttonStyle(.bordered)
                    .tint(.purple)
                    .font(.title3)

                    NavigationLink(value: "browseGames") {
                        Text("Browse Public Games")
                            .frame(width: 200)
                    }
                    .buttonStyle(.bordered)
                    .tint(.purple)
                    .font(.title3)

                    HStack(spacing: 15) {
                        NavigationLink(value: "profile") {
                            Label("Profile", systemImage: "person.circle")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)
                        .tint(.purple)
                        .controlSize(.small)

                        NavigationLink(value: "leaderboard") {
                            Label("Board", systemImage: "trophy")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)
                        .tint(.purple)
                        .controlSize(.small)
                    }
                    .frame(width: 200)
                }
            }
            .padding()
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        handleSignOut()
                    } label: {
                        Label("Sign Out", systemImage: "rectangle.portrait.and.arrow.right")
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
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationDestination(for: String.self) { destination in
                if destination == "newGame" {
                    NewGameView(navigationPath: $navigationPath)
                } else if destination == "joinGame" {
                    JoinGameView(navigationPath: $navigationPath)
                } else if destination == "profile" {
                    ProfileView()
                } else if destination == "leaderboard" {
                    LeaderboardView()
                } else if destination == "browseGames" {
                    PublicGamesView(navigationPath: $navigationPath)
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
    }

    private func loadUserInfo() {
        if let user = BoggleAPI.shared.getCurrentUser() {
            userEmail = user.email
            userDisplayName = user.displayName
        }
    }

    private func handleSignOut() {
        BoggleAPI.shared.logout()
        isLoggedIn = false
    }

    private func attemptReconnection() {
        Task {
            isReconnecting = true
            reconnectError = nil

            do {
                if let gameState = try await BoggleAPI.shared.attemptReconnect() {
                    print("INFO [Reconnect] Rejoining game | status=\(gameState.status) game=\(gameState.gameId.prefix(8))")

                    // Save the active game state for future reconnections
                    BoggleAPI.shared.saveActiveGame(gameId: gameState.gameId, playerId: gameState.playerId)

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
                        BoggleAPI.shared.clearActiveGame()
                        isReconnecting = false

                    default:
                        print("WARN [Reconnect] Unknown game status: \(gameState.status)")
                        BoggleAPI.shared.clearActiveGame()
                        isReconnecting = false
                    }

                } else {
                    isReconnecting = false
                }
            } catch {
                // Clear the saved game since it's invalid (game deleted, player removed, etc.)
                BoggleAPI.shared.clearActiveGame()
                // Silently dismiss - don't show error for stale game state
                isReconnecting = false
            }
        }
    }
}

#Preview {
    LobbyView(isLoggedIn: .constant(true))
}
