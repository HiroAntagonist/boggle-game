//
// ABOUTME: Profile view displaying user information and statistics.
// ABOUTME: Shows email, display name, gamer tag, and provides navigation to edit profile.
//

import SwiftUI
import OpenAPIClient

struct ProfileView: View {
    @State private var userInfo: UserResponse?
    @State private var stats: UserStatsResponse?
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var showingEditProfile = false

    var body: some View {
        ScrollView {
            VStack(spacing: 30) {
                if isLoading {
                    ProgressView()
                        .scaleEffect(1.5)
                        .padding()
                } else if let error = errorMessage {
                    VStack(spacing: 15) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.system(size: 50))
                            .foregroundStyle(.red)

                        Text(error)
                            .foregroundStyle(.secondary)
                            .multilineTextAlignment(.center)

                        Button("Try Again") {
                            loadProfile()
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(.purple)
                    }
                    .padding()
                } else {
                    // User Info Section
                    VStack(spacing: 20) {
                        Image(systemName: "person.circle.fill")
                            .font(.system(size: 80))
                            .foregroundStyle(.blue)

                        if let user = userInfo {
                            VStack(spacing: 10) {
                                if let displayName = user.displayName {
                                    Text(displayName)
                                        .font(.title2)
                                        .fontWeight(.bold)
                                }

                                Text(user.email)
                                    .font(.caption)
                                    .foregroundStyle(.secondary)

                                if let gamerTag = user.gamerTag {
                                    HStack {
                                        Image(systemName: "gamecontroller.fill")
                                            .foregroundStyle(.green)
                                        Text(gamerTag)
                                            .font(.headline)
                                    }
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(Color.green.opacity(0.1))
                                    .cornerRadius(8)
                                } else {
                                    Text("No gamer tag set")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                            }
                        }

                        Button {
                            showingEditProfile = true
                        } label: {
                            Label("Edit Profile", systemImage: "pencil")
                        }
                        .buttonStyle(.bordered)
                    }
                    .padding()

                    Divider()

                    // Stats Section
                    if let stats = stats {
                        VStack(alignment: .leading, spacing: 20) {
                            Text("Statistics")
                                .font(.title2)
                                .fontWeight(.bold)

                            VStack(spacing: 15) {
                                StatRow(label: "Games Played", value: "\(stats.totalGames)")
                                StatRow(label: "Games Won", value: "\(stats.totalWins)")
                                StatRow(label: "Win Rate", value: String(format: "%.1f%%", stats.winRate * 100))
                                StatRow(label: "Total Points", value: "\(stats.totalPoints)")
                                StatRow(label: "Average Score", value: String(format: "%.1f", stats.averageScore))
                                StatRow(label: "Best Score", value: "\(stats.bestScore)")
                            }
                        }
                        .padding()
                    }
                }
            }
        }
        .navigationTitle("Profile")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            loadProfile()
        }
        .sheet(isPresented: $showingEditProfile) {
            ProfileEditView(currentGamerTag: userInfo?.gamerTag) { updatedUser in
                userInfo = updatedUser
            }
        }
    }

    private func loadProfile() {
        Task {
            isLoading = true
            errorMessage = nil

            do {
                // Fetch profile and stats in parallel
                async let profileTask = JumbleAPI.shared.getCurrentUserProfile()
                async let statsTask = JumbleAPI.shared.getUserStats()

                userInfo = try await profileTask
                stats = try await statsTask

                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }
}

struct StatRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .foregroundStyle(.secondary)
            Spacer()
            Text(value)
                .fontWeight(.semibold)
        }
    }
}

#Preview {
    NavigationStack {
        ProfileView()
    }
}
