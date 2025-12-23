//
// ABOUTME: View for joining an existing game by entering a code or browsing public games.
// ABOUTME: Shows code input at top and public games list below.
//

import SwiftUI
import Combine
import OpenAPIClient

struct JoinGameView: View {
    @Binding var navigationPath: NavigationPath
    @State private var friendlyCode = ""
    @State private var isJoining = false
    @State private var errorMessage: String?
    @State private var navigateToWaitingRoom = false
    @State private var gameId: String?
    @State private var maxPlayers: Int?
    @State private var playerId: String?

    // Public games state
    @State private var publicGames: [PublicGameEntry] = []
    @State private var isLoadingGames = true
    @State private var gamesErrorMessage: String?
    @State private var joiningGameId: String?
    @State private var joinErrorMessage: String?
    @State private var showJoinError = false
    @State private var showGamerTagRequired = false
    @State private var navigateToGame = false
    @State private var gameViewData: (gameId: String, playerId: String, board: [[String]], timeLimit: Int?, startedAt: String?, webSocketManager: WebSocketManager)?

    // Polling timer
    let pollTimer = Timer.publish(every: 5, on: .main, in: .common).autoconnect()

    var body: some View {
        VStack(spacing: 0) {
            // Code input section
            VStack(spacing: 20) {
                Text("Join Game")
                    .font(.system(size: 36, weight: .black, design: .rounded))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.nebulaAccent, .nebulaPrimary],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .shadow(color: .nebulaPrimary.opacity(0.5), radius: 10, x: 0, y: 5)

                Text("Enter a game code")
                    .font(.subheadline)
                    .foregroundStyle(Color.nebulaTextSecondary)

                TextField("XXXX-XXXX", text: $friendlyCode)
                    .textFieldStyle(.plain)
                    .font(.system(size: 28, weight: .bold, design: .monospaced))
                    .multilineTextAlignment(.center)
                    .textInputAutocapitalization(.characters)
                    .autocorrectionDisabled()
                    .padding()
                    .background(Color.nebulaSurface.opacity(0.6))
                    .cornerRadius(12)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.nebulaAccent.opacity(0.5), lineWidth: 1)
                    )
                    .foregroundStyle(.white)
                    .padding(.horizontal)
                    .onChange(of: friendlyCode) { oldValue, newValue in
                        // Auto-format as XXXX-XXXX
                        let filtered = newValue.filter { $0.isNumber }
                        if filtered.count > 4 {
                            friendlyCode = String(filtered.prefix(4)) + "-" + String(filtered.dropFirst(4).prefix(4))
                        } else if filtered.count > 0 {
                            friendlyCode = filtered
                        }
                    }

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
                        await joinGame()
                    }
                } label: {
                    HStack {
                        Image(systemName: "arrow.right.circle.fill")
                        Text("Join by Code")
                    }
                }
                .nebulaButtonStyle(color: .nebulaPrimary)
                .disabled(isJoining || friendlyCode.count < 8)

                if isJoining {
                    ProgressView()
                        .tint(.nebulaAccent)
                }
            }
            .padding()

            // Divider
            HStack {
                Rectangle()
                    .frame(height: 1)
                    .foregroundStyle(Color.white.opacity(0.2))
                Text("OR")
                    .font(.caption)
                    .foregroundStyle(Color.nebulaTextSecondary)
                Rectangle()
                    .frame(height: 1)
                    .foregroundStyle(Color.white.opacity(0.2))
            }
            .padding(.horizontal)
            .padding(.vertical, 10)

            Text("Browse public games")
                .font(.caption)
                .foregroundStyle(Color.nebulaTextSecondary)
                .padding(.bottom, 10)

            // Public games list
            if isLoadingGames {
                Spacer()
                ProgressView()
                    .tint(.nebulaAccent)
                    .scaleEffect(1.2)
                Spacer()
            } else if let error = gamesErrorMessage {
                Spacer()
                VStack(spacing: 15) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 40))
                        .foregroundStyle(Color.nebulaError)

                    Text(error)
                        .foregroundStyle(Color.nebulaTextSecondary)
                        .multilineTextAlignment(.center)

                    Button("Try Again") {
                        loadPublicGames()
                    }
                    .nebulaButtonStyle(color: .nebulaSurface)
                }
                .padding()
                Spacer()
            } else if publicGames.isEmpty {
                Spacer()
                VStack(spacing: 10) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 40))
                        .foregroundStyle(Color.nebulaTextSecondary)

                    Text("No public games available")
                        .font(.headline)
                        .foregroundStyle(.white)

                    Text("Create a public game to get started")
                        .font(.caption)
                        .foregroundStyle(Color.nebulaTextSecondary)
                }
                .padding()
                Spacer()
            } else {
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(publicGames, id: \.gameId) { game in
                            NebulaPublicGameRow(
                                game: game,
                                isJoining: joiningGameId == game.gameId,
                                onJoin: {
                                    joinPublicGame(game)
                                }
                            )
                        }
                    }
                    .padding(.horizontal)
                }
            }
        }
        .withNebulaBackground()
        .navigationDestination(isPresented: $navigateToWaitingRoom) {
            if let players = maxPlayers, let pid = playerId, let gid = gameId {
                WaitingRoomView(navigationPath: $navigationPath, gameId: gid, playerId: pid, maxPlayers: players, friendlyCode: friendlyCode)
            }
        }
        .navigationDestination(isPresented: $navigateToGame) {
            if let data = gameViewData {
                GameView(
                    navigationPath: $navigationPath,
                    gameId: data.gameId,
                    playerId: data.playerId,
                    initialBoard: data.board,
                    initialTimeLimit: data.timeLimit,
                    initialStartedAt: data.startedAt,
                    webSocketManager: data.webSocketManager
                )
            }
        }
        .alert("Unable to Join", isPresented: $showJoinError) {
            Button("OK", role: .cancel) { }
        } message: {
            if let message = joinErrorMessage {
                Text(message)
            }
        }
        .alert("Gamer Tag Required", isPresented: $showGamerTagRequired) {
            Button("Set Gamer Tag") {
                navigationPath.append("profile")
            }
            Button("Cancel", role: .cancel) { }
        } message: {
            Text("You need to set a gamer tag in your profile before joining public games.")
        }
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    loadPublicGames()
                } label: {
                    Image(systemName: "arrow.clockwise")
                        .foregroundStyle(Color.nebulaAccent)
                }
                .disabled(isLoadingGames)
            }
        }
        .onAppear {
            loadPublicGames()
        }
        .onReceive(pollTimer) { _ in
            // Silently refresh public games every 5 seconds
            loadPublicGames()
        }
    }

    private func joinGame() async {
        isJoining = true
        errorMessage = nil

        do {
            // Join the game by friendly code
            let joinResponse = try await JumbleAPI.shared.joinGameByCode(friendlyCode: friendlyCode)
            playerId = joinResponse.playerId
            gameId = joinResponse.gameId

            // Fetch game state to get the actual max_players value
            if let gid = gameId {
                let gameState = try await JumbleAPI.shared.getGameState(gameId: gid)
                maxPlayers = gameState.maxPlayers
            } else {
                maxPlayers = 4 // Fallback if gameId is somehow nil
            }

            // Save active game for reconnection
            if let gid = gameId, let pid = playerId {
                JumbleAPI.shared.saveActiveGame(gameId: gid, playerId: pid)
            }

            // Navigate to waiting room
            navigateToWaitingRoom = true

        } catch let error as APIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "An unexpected error occurred"
        }

        isJoining = false
    }

    private func loadPublicGames() {
        Task {
            isLoadingGames = true
            gamesErrorMessage = nil

            do {
                let response = try await JumbleAPI.shared.getPublicGames(limit: 50)
                publicGames = response.games
                isLoadingGames = false
            } catch {
                gamesErrorMessage = error.localizedDescription
                isLoadingGames = false
            }
        }
    }

    private func joinPublicGame(_ game: PublicGameEntry) {
        Task {
            joiningGameId = game.gameId
            defer { joiningGameId = nil }

            do {
                let response = try await JumbleAPI.shared.joinGame(
                    gameId: game.gameId,
                    playerName: "Player"
                )

                print("INFO [JoinGame] Joined public game | gameId=\(response.gameId.prefix(8)) status=\(response.status)")

                // Save active game for reconnection
                JumbleAPI.shared.saveActiveGame(gameId: response.gameId, playerId: response.playerId)

                // Navigate based on game status
                switch response.status {
                case "waiting", "created":
                    gameId = response.gameId
                    playerId = response.playerId
                    maxPlayers = response.maxPlayers
                    friendlyCode = game.friendlyCode
                    navigateToWaitingRoom = true

                case "in_progress":
                    // Game auto-started, navigate directly to GameView
                    if let timeLimit = response.timeLimit,
                       let startedAt = response.startedAt {
                        // Create WebSocket connection
                        let wsManager = WebSocketManager(gameId: response.gameId, playerId: response.playerId)
                        wsManager.connect()

                        // Set navigation data
                        gameViewData = (
                            gameId: response.gameId,
                            playerId: response.playerId,
                            board: response.board,
                            timeLimit: timeLimit,
                            startedAt: startedAt,
                            webSocketManager: wsManager
                        )

                        // Trigger navigation
                        navigateToGame = true

                        print("INFO [JoinGame] Game auto-started, navigating to GameView | gameId=\(response.gameId.prefix(8))")
                    } else {
                        joinErrorMessage = "Game data incomplete - missing time information"
                        showJoinError = true
                    }

                default:
                    print("WARN [JoinGame] Unexpected game status: \(response.status)")
                    joinErrorMessage = "Unexpected game status: \(response.status)"
                    showJoinError = true
                }

            } catch let error as APIError {
                // Check if this is a gamer tag requirement error
                if let errorDesc = error.errorDescription,
                   errorDesc.contains("gamer tag") {
                    showGamerTagRequired = true
                } else {
                    joinErrorMessage = error.errorDescription
                    showJoinError = true
                }
            } catch {
                joinErrorMessage = "An unexpected error occurred"
                showJoinError = true
            }
        }
    }
}

// Nebula-themed public game row
struct NebulaPublicGameRow: View {
    let game: PublicGameEntry
    let isJoining: Bool
    let onJoin: () -> Void

    var body: some View {
        HStack(spacing: 15) {
            VStack(alignment: .leading, spacing: 8) {
                // Creator and code
                HStack {
                    if let creator = game.creatorGamerTag {
                        Text(creator)
                            .font(.headline)
                            .foregroundStyle(.white)
                    } else {
                        Text("Anonymous")
                            .font(.headline)
                            .foregroundStyle(Color.nebulaTextSecondary)
                    }

                    Spacer()

                    Text(game.friendlyCode)
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundStyle(Color.nebulaAccent)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.nebulaAccent.opacity(0.2))
                        .cornerRadius(6)
                }

                // Game details
                HStack(spacing: 12) {
                    Label("\(game.currentPlayers)/\(game.maxPlayers)", systemImage: "person.2.fill")
                        .font(.caption)
                        .foregroundStyle(Color.nebulaTextSecondary)

                    Label("\(game.boardSize)×\(game.boardSize)", systemImage: "square.grid.3x3")
                        .font(.caption)
                        .foregroundStyle(Color.nebulaTextSecondary)

                    if let timeLimit = game.timeLimit {
                        Label("\(timeLimit / 60)m", systemImage: "timer")
                            .font(.caption)
                            .foregroundStyle(Color.nebulaTextSecondary)
                    }
                }

                // Time ago
                Text(timeAgo(from: game.createdAt))
                    .font(.caption2)
                    .foregroundStyle(Color.nebulaTextSecondary.opacity(0.7))
            }

            Spacer()

            // Join button
            if isJoining {
                ProgressView()
                    .tint(.nebulaAccent)
            } else if game.currentPlayers >= game.maxPlayers {
                Text("Full")
                    .font(.caption)
                    .foregroundStyle(Color.nebulaTextSecondary)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.nebulaSurface.opacity(0.5))
                    .cornerRadius(8)
            } else {
                Button {
                    onJoin()
                } label: {
                    Text("Join")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundStyle(.white)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.nebulaPrimary)
                        )
                        .nebulaGlow(color: .nebulaPrimary, radius: 3)
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.nebulaSurface.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
        )
    }

    private func timeAgo(from isoString: String) -> String {
        let formatter = ISO8601DateFormatter()
        guard let date = formatter.date(from: isoString) else {
            return "Just now"
        }

        let seconds = Int(Date().timeIntervalSince(date))
        if seconds < 60 {
            return "Just now"
        } else if seconds < 3600 {
            let minutes = seconds / 60
            return "\(minutes)m ago"
        } else if seconds < 86400 {
            let hours = seconds / 3600
            return "\(hours)h ago"
        } else {
            let days = seconds / 86400
            return "\(days)d ago"
        }
    }
}

#Preview {
    JoinGameView(navigationPath: .constant(NavigationPath()))
}
