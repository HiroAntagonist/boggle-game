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
        VStack(spacing: 0) {
            if isLoading {
                Spacer()
                VStack(spacing: 20) {
                    ProgressView()
                        .tint(.nebulaAccent)
                        .scaleEffect(1.5)

                    Text("Loading leaderboard...")
                        .foregroundStyle(Color.nebulaTextSecondary)
                }
                Spacer()
            } else if let error = errorMessage {
                Spacer()
                VStack(spacing: 15) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 50))
                        .foregroundStyle(Color.nebulaError)

                    Text(error)
                        .foregroundStyle(Color.nebulaTextSecondary)
                        .multilineTextAlignment(.center)

                    Button("Try Again") {
                        loadLeaderboard()
                    }
                    .nebulaButtonStyle(color: .nebulaPrimary)
                }
                .padding()
                Spacer()
            } else if leaderboard.isEmpty {
                Spacer()
                VStack(spacing: 15) {
                    Image(systemName: "chart.bar")
                        .font(.system(size: 50))
                        .foregroundStyle(Color.nebulaTextSecondary)

                    Text("No players on the leaderboard yet")
                        .font(.headline)
                        .foregroundStyle(.white)

                    Text("Play public games to appear on the leaderboard!")
                        .font(.caption)
                        .foregroundStyle(Color.nebulaTextSecondary)
                        .multilineTextAlignment(.center)
                }
                .padding()
                Spacer()
            } else {
                ScrollView {
                    VStack(spacing: 16) {
                        // User's rank section (if they're ranked)
                        if let rank = userRank {
                            VStack(alignment: .leading, spacing: 10) {
                                Text("Your Rank")
                                    .font(.headline)
                                    .foregroundStyle(Color.nebulaTextSecondary)

                                NebulaLeaderboardRow(entry: rank, isCurrentUser: true)
                            }
                            .padding(.bottom, 10)
                        }

                        // Top players section
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Top Players")
                                .font(.headline)
                                .foregroundStyle(Color.nebulaTextSecondary)

                            ForEach(leaderboard, id: \.rank) { entry in
                                NebulaLeaderboardRow(entry: entry, isCurrentUser: false)
                            }
                        }
                    }
                    .padding()
                }
            }
        }
        .withNebulaBackground()
        .navigationTitle("Leaderboard")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    loadLeaderboard()
                } label: {
                    Image(systemName: "arrow.clockwise")
                        .foregroundStyle(Color.nebulaAccent)
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
                let response = try await JumbleAPI.shared.getLeaderboard(limit: 50)
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

struct NebulaLeaderboardRow: View {
    let entry: LeaderboardEntry
    let isCurrentUser: Bool

    var body: some View {
        HStack(spacing: 15) {
            // Rank badge
            ZStack {
                if entry.rank <= 3 {
                    Circle()
                        .fill(rankColor.opacity(0.2))
                        .frame(width: 44, height: 44)

                    Image(systemName: entry.rank == 1 ? "crown.fill" : "trophy.fill")
                        .foregroundStyle(rankColor)
                        .font(.system(size: 18))
                } else {
                    Circle()
                        .fill(Color.nebulaSurface.opacity(0.6))
                        .frame(width: 44, height: 44)

                    Text("#\(entry.rank)")
                        .font(.headline)
                        .fontWeight(.bold)
                        .foregroundStyle(Color.nebulaTextSecondary)
                }
            }

            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    if let gamerTag = entry.gamerTag {
                        Text(gamerTag)
                            .font(.headline)
                            .foregroundStyle(.white)
                    } else {
                        Text("Anonymous")
                            .font(.headline)
                            .foregroundStyle(Color.nebulaTextSecondary)
                    }

                    if isCurrentUser {
                        Text("YOU")
                            .font(.caption2)
                            .fontWeight(.bold)
                            .foregroundStyle(.white)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.nebulaAccent)
                            .cornerRadius(4)
                    }
                }

                Text("\(entry.totalWins) wins • \(entry.totalGames) games")
                    .font(.caption)
                    .foregroundStyle(Color.nebulaTextSecondary)
            }

            Spacer()

            // Score/wins display
            VStack(alignment: .trailing, spacing: 2) {
                Text("\(entry.totalWins)")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundStyle(entry.rank <= 3 ? rankColor : Color.nebulaAccent)

                Text("wins")
                    .font(.caption2)
                    .foregroundStyle(Color.nebulaTextSecondary)
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(isCurrentUser ? Color.nebulaAccent.opacity(0.15) : Color.nebulaSurface.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(isCurrentUser ? Color.nebulaAccent.opacity(0.5) : Color.white.opacity(0.1), lineWidth: isCurrentUser ? 2 : 1)
                )
        )
        .nebulaGlow(color: entry.rank == 1 ? .yellow : .clear, radius: entry.rank == 1 ? 5 : 0)
    }

    private var rankColor: Color {
        switch entry.rank {
        case 1: return .yellow
        case 2: return Color(red: 0.75, green: 0.75, blue: 0.8) // Silver
        case 3: return .orange
        default: return Color.nebulaAccent
        }
    }
}

#Preview {
    NavigationStack {
        LeaderboardView()
    }
}
