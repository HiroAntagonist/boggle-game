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
    @State private var navigateToGame = false
    @State private var gameViewData: (gameId: String, playerId: String, board: [[String]], timeLimit: Int?, startedAt: String?, webSocketManager: WebSocketManager)?

    // Polling timer
    let pollTimer = Timer.publish(every: 5, on: .main, in: .common).autoconnect()

    var body: some View {
        VStack(spacing: 0) {
            // Code input section
            VStack(spacing: 20) {
                Text("Join Game")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text("Enter a game code")
                    .font(.subheadline)
                    .foregroundStyle(.gray)

                TextField("XXXX-XXXX", text: $friendlyCode)
                    .textFieldStyle(.roundedBorder)
                    .font(.system(size: 24, weight: .semibold, design: .monospaced))
                    .multilineTextAlignment(.center)
                    .textInputAutocapitalization(.characters)
                    .autocorrectionDisabled()
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
                        .foregroundStyle(.red)
                        .font(.caption)
                }

                Button("Join by Code") {
                    Task {
                        await joinGame()
                    }
                }
                .buttonStyle(.borderedProminent)
                .tint(.purple)
                .disabled(isJoining || friendlyCode.count < 8)
                .font(.title3)

                if isJoining {
                    ProgressView("Joining game...")
                }
            }
            .padding()

            // Divider
            VStack(spacing: 8) {
                Divider()
                    .padding(.horizontal)

                Text("Or browse public games")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            // Public games list
            if isLoadingGames {
                Spacer()
                ProgressView()
                    .scaleEffect(1.2)
                Spacer()
            } else if let error = gamesErrorMessage {
                Spacer()
                VStack(spacing: 15) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 40))
                        .foregroundStyle(.red)

                    Text(error)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)

                    Button("Try Again") {
                        loadPublicGames()
                    }
                    .buttonStyle(.bordered)
                    .tint(.purple)
                }
                .padding()
                Spacer()
            } else if publicGames.isEmpty {
                Spacer()
                VStack(spacing: 10) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 40))
                        .foregroundStyle(.secondary)

                    Text("No public games available")
                        .font(.headline)

                    Text("Create a public game to get started")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .padding()
                Spacer()
            } else {
                List {
                    ForEach(publicGames, id: \.gameId) { game in
                        PublicGameRow(
                            game: game,
                            isJoining: joiningGameId == game.gameId,
                            onJoin: {
                                joinPublicGame(game)
                            }
                        )
                    }
                }
                .listStyle(.plain)
            }
        }
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
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    loadPublicGames()
                } label: {
                    Image(systemName: "arrow.clockwise")
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
                joinErrorMessage = error.errorDescription
                showJoinError = true
            } catch {
                joinErrorMessage = "An unexpected error occurred"
                showJoinError = true
            }
        }
    }
}

// PublicGameRow component (copied from PublicGamesView)
struct PublicGameRow: View {
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
                    } else {
                        Text("Anonymous")
                            .font(.headline)
                            .foregroundStyle(.secondary)
                    }

                    Spacer()

                    Text(game.friendlyCode)
                        .font(.caption)
                        .fontWeight(.semibold)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(6)
                }

                // Game details
                HStack(spacing: 12) {
                    Label("\(game.currentPlayers)/\(game.maxPlayers)", systemImage: "person.2.fill")
                        .font(.caption)
                        .foregroundStyle(.secondary)

                    Label("\(game.boardSize)×\(game.boardSize)", systemImage: "square.grid.3x3")
                        .font(.caption)
                        .foregroundStyle(.secondary)

                    if let timeLimit = game.timeLimit {
                        Label("\(timeLimit)s", systemImage: "timer")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }

                // Time ago
                Text(timeAgo(from: game.createdAt))
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }

            Spacer()

            // Join button
            if isJoining {
                ProgressView()
            } else if game.currentPlayers >= game.maxPlayers {
                Text("Full")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } else {
                Button {
                    onJoin()
                } label: {
                    Text("Join")
                        .fontWeight(.semibold)
                }
                .buttonStyle(.borderedProminent)
                .tint(.purple)
                .controlSize(.small)
            }
        }
        .padding(.vertical, 4)
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
