//
// ABOUTME: Leaderboard view displaying top players ranked by wins.
// ABOUTME: Shows player rankings, gamer tags, total wins, and highlights current user's rank.
//

import SwiftUI
import OpenAPIClient

struct LeaderboardView: View {
    @State private var leaderboard: [LeaderboardEntry] = []
    @State private var userRank: LeaderboardEntry?
    @State private var isLoading = true
    @State private var errorMessage: String?

    var body: some View {
        Group {
            if isLoading {
                VStack(spacing: 20) {
                    ProgressView()
                        .scaleEffect(1.5)

                    Text("Loading leaderboard...")
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
                        loadLeaderboard()
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
            } else if leaderboard.isEmpty {
                VStack(spacing: 15) {
                    Image(systemName: "chart.bar")
                        .font(.system(size: 50))
                        .foregroundStyle(.secondary)

                    Text("No players on the leaderboard yet")
                        .foregroundStyle(.secondary)

                    Text("Play public games to appear on the leaderboard!")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding()
            } else {
                List {
                    // User's rank section (if they're ranked)
                    if let rank = userRank {
                        Section {
                            LeaderboardRow(entry: rank, isCurrentUser: true)
                        } header: {
                            Text("Your Rank")
                        }
                    }

                    // Top players section
                    Section {
                        ForEach(leaderboard, id: \.rank) { entry in
                            LeaderboardRow(entry: entry, isCurrentUser: false)
                        }
                    } header: {
                        Text("Top Players")
                    }
                }
                .listStyle(.insetGrouped)
            }
        }
        .navigationTitle("Leaderboard")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    loadLeaderboard()
                } label: {
                    Image(systemName: "arrow.clockwise")
                }
                .disabled(isLoading)
            }
        }
        .onAppear {
            loadLeaderboard()
        }
    }

    private func loadLeaderboard() {
        Task {
            isLoading = true
            errorMessage = nil

            do {
                let response = try await BoggleAPI.shared.getLeaderboard(limit: 50)
                leaderboard = response.leaderboard
                userRank = response.userRank
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }
}

struct LeaderboardRow: View {
    let entry: LeaderboardEntry
    let isCurrentUser: Bool

    var body: some View {
        HStack(spacing: 15) {
            // Rank badge
            Text("#\(entry.rank)")
                .font(.headline)
                .fontWeight(.bold)
                .foregroundStyle(rankColor)
                .frame(width: 50, alignment: .leading)

            VStack(alignment: .leading, spacing: 4) {
                if let gamerTag = entry.gamerTag {
                    HStack {
                        Text(gamerTag)
                            .font(.headline)

                        if isCurrentUser {
                            Text("(You)")
                                .font(.caption)
                                .foregroundStyle(.blue)
                        }
                    }
                } else {
                    Text("Anonymous")
                        .font(.headline)
                        .foregroundStyle(.secondary)
                }

                Text("\(entry.totalWins) wins • \(entry.totalGames) games")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            // Trophy icon for top 3
            if entry.rank <= 3 {
                Image(systemName: "trophy.fill")
                    .foregroundStyle(rankColor)
                    .font(.title2)
            }
        }
        .padding(.vertical, 4)
        .background(isCurrentUser ? Color.blue.opacity(0.05) : Color.clear)
    }

    private var rankColor: Color {
        switch entry.rank {
        case 1: return .yellow
        case 2: return .gray
        case 3: return .orange
        default: return .primary
        }
    }
}

#Preview {
    NavigationStack {
        LeaderboardView()
    }
}
