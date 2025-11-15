//
// ABOUTME: Public games browser view showing available public games to join.
// ABOUTME: Displays game details and allows players to join public games created by others.
//

import SwiftUI
import OpenAPIClient

struct PublicGamesView: View {
    @Binding var navigationPath: NavigationPath
    @State private var games: [PublicGameEntry] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var joiningGameId: String?

    var body: some View {
        Group {
            if isLoading {
                VStack(spacing: 20) {
                    ProgressView()
                        .scaleEffect(1.5)

                    Text("Finding public games...")
                        .foregroundStyle(.secondary)
                }
            } else if let error = errorMessage {
                VStack(spacing: 15) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 50))
                        .foregroundStyle(.red)

                    Text(error)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)

                    Button("Try Again") {
                        loadPublicGames()
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
            } else if games.isEmpty {
                VStack(spacing: 15) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 50))
                        .foregroundStyle(.secondary)

                    Text("No public games available")
                        .font(.headline)

                    Text("Be the first to create a public game!")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)

                    Button("Create Public Game") {
                        navigationPath.append("newGame")
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
            } else {
                List {
                    ForEach(games, id: \.gameId) { game in
                        PublicGameRow(
                            game: game,
                            isJoining: joiningGameId == game.gameId,
                            onJoin: {
                                joinGame(game)
                            }
                        )
                    }
                }
                .listStyle(.insetGrouped)
            }
        }
        .navigationTitle("Public Games")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    loadPublicGames()
                } label: {
                    Image(systemName: "arrow.clockwise")
                }
                .disabled(isLoading)
            }
        }
        .onAppear {
            loadPublicGames()
        }
    }

    private func loadPublicGames() {
        Task {
            isLoading = true
            errorMessage = nil

            do {
                let response = try await BoggleAPI.shared.getPublicGames(limit: 50)
                games = response.games
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }

    private func joinGame(_ game: PublicGameEntry) {
        Task {
            joiningGameId = game.gameId
            defer { joiningGameId = nil }

            do {
                let response = try await BoggleAPI.shared.joinGame(
                    gameId: game.gameId,
                    playerName: "Player"
                )

                print("INFO [PublicGames] Joined game | gameId=\(response.gameId.prefix(8)) status=\(response.status)")

                // Save active game for reconnection
                BoggleAPI.shared.saveActiveGame(gameId: response.gameId, playerId: response.playerId)

                // Navigate based on game status
                switch response.status {
                case "waiting", "created":
                    navigationPath.append("waitingRoom:\(response.gameId):\(response.playerId):\(response.maxPlayers)")

                case "in_progress":
                    // Game already started, navigate directly to game
                    if let timeLimit = response.timeLimit,
                       let startedAt = response.startedAt {
                        // TODO: Navigate to GameView with initial state
                        print("WARN [PublicGames] Game already in progress - need GameView navigation")
                    }

                default:
                    print("WARN [PublicGames] Unexpected game status: \(response.status)")
                }

            } catch {
                errorMessage = "Failed to join game: \(error.localizedDescription)"
            }
        }
    }
}

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
    NavigationStack {
        PublicGamesView(navigationPath: .constant(NavigationPath()))
    }
}
