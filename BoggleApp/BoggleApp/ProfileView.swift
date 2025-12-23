//
// ABOUTME: Profile view displaying user information and statistics.
// ABOUTME: Shows email, display name, gamer tag, and provides navigation to edit profile.
//

import SwiftUI
import OpenAPIClient

struct ProfileView: View {
    @Binding var isLoggedIn: Bool
    @State private var userInfo: UserResponse?
    @State private var stats: UserStatsResponse?
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var showingEditProfile = false

    var body: some View {
        ScrollView {
            VStack(spacing: 25) {
                if isLoading {
                    Spacer()
                        .frame(height: 100)
                    ProgressView()
                        .tint(.nebulaAccent)
                        .scaleEffect(1.5)
                } else if let error = errorMessage {
                    VStack(spacing: 15) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.system(size: 50))
                            .foregroundStyle(Color.nebulaError)

                        Text(error)
                            .foregroundStyle(Color.nebulaTextSecondary)
                            .multilineTextAlignment(.center)

                        Button("Try Again") {
                            loadProfile()
                        }
                        .nebulaButtonStyle(color: .nebulaPrimary)
                    }
                    .padding()
                } else {
                    // User Info Section
                    VStack(spacing: 20) {
                        // Avatar
                        ZStack {
                            Circle()
                                .fill(
                                    LinearGradient(
                                        colors: [.nebulaPrimary, .nebulaAccent],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .frame(width: 100, height: 100)
                                .nebulaGlow(color: .nebulaPrimary, radius: 10)

                            Image(systemName: "person.fill")
                                .font(.system(size: 50))
                                .foregroundStyle(.white)
                        }

                        if let user = userInfo {
                            VStack(spacing: 12) {
                                if let displayName = user.displayName {
                                    Text(displayName)
                                        .font(.title2)
                                        .fontWeight(.bold)
                                        .foregroundStyle(.white)
                                }

                                Text(user.email)
                                    .font(.caption)
                                    .foregroundStyle(Color.nebulaTextSecondary)

                                if let gamerTag = user.gamerTag {
                                    HStack {
                                        Image(systemName: "gamecontroller.fill")
                                            .foregroundStyle(Color.nebulaAccent)
                                        Text(gamerTag)
                                            .font(.headline)
                                            .foregroundStyle(.white)
                                    }
                                    .padding(.horizontal, 16)
                                    .padding(.vertical, 8)
                                    .background(
                                        Capsule()
                                            .fill(Color.nebulaAccent.opacity(0.2))
                                            .overlay(
                                                Capsule()
                                                    .stroke(Color.nebulaAccent.opacity(0.5), lineWidth: 1)
                                            )
                                    )
                                } else {
                                    VStack(spacing: 8) {
                                        HStack {
                                            Image(systemName: "info.circle")
                                                .foregroundStyle(Color.nebulaAccent)
                                            Text("No gamer tag set")
                                                .font(.caption)
                                                .fontWeight(.semibold)
                                                .foregroundStyle(.white)
                                        }
                                        .padding(.horizontal, 12)
                                        .padding(.vertical, 6)
                                        .background(Color.nebulaAccent.opacity(0.2))
                                        .cornerRadius(8)

                                        Text("Set a gamer tag to join public games and appear on the leaderboard")
                                            .font(.caption2)
                                            .foregroundStyle(Color.nebulaTextSecondary)
                                            .multilineTextAlignment(.center)
                                            .padding(.horizontal)
                                    }
                                }
                            }
                        }

                        VStack(spacing: 12) {
                            Button {
                                showingEditProfile = true
                            } label: {
                                HStack {
                                    Image(systemName: "pencil")
                                    Text("Edit Profile")
                                }
                            }
                            .nebulaButtonStyle(color: .nebulaSurface)

                            Button {
                                handleSignOut()
                            } label: {
                                HStack {
                                    Image(systemName: "rectangle.portrait.and.arrow.right")
                                    Text("Sign Out")
                                }
                            }
                            .nebulaButtonStyle(color: .nebulaError.opacity(0.8))
                        }
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 24)
                            .fill(Color.nebulaSurface.opacity(0.5))
                            .overlay(
                                RoundedRectangle(cornerRadius: 24)
                                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
                            )
                    )

                    // Stats Section
                    if let stats = stats {
                        VStack(alignment: .leading, spacing: 20) {
                            Text("Statistics")
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundStyle(.white)

                            VStack(spacing: 12) {
                                NebulaStatRow(label: "Games Played", value: "\(stats.totalGames)", icon: "gamecontroller")
                                NebulaStatRow(label: "Games Won", value: "\(stats.totalWins)", icon: "trophy")
                                NebulaStatRow(label: "Win Rate", value: String(format: "%.1f%%", stats.winRate * 100), icon: "percent")
                                NebulaStatRow(label: "Total Points", value: "\(stats.totalPoints)", icon: "star.fill")
                                NebulaStatRow(label: "Average Score", value: String(format: "%.1f", stats.averageScore), icon: "chart.bar")
                                NebulaStatRow(label: "Best Score", value: "\(stats.bestScore)", icon: "crown")
                            }
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 20)
                                .fill(Color.nebulaSurface.opacity(0.5))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 20)
                                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                                )
                        )
                    }
                }
            }
            .padding()
        }
        .withNebulaBackground()
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

    private func handleSignOut() {
        JumbleAPI.shared.logout()
        isLoggedIn = false
    }
}

struct NebulaStatRow: View {
    let label: String
    let value: String
    let icon: String

    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundStyle(Color.nebulaAccent)
                .frame(width: 24)

            Text(label)
                .foregroundStyle(Color.nebulaTextSecondary)

            Spacer()

            Text(value)
                .fontWeight(.bold)
                .foregroundStyle(.white)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.nebulaSurface.opacity(0.4))
        )
    }
}

#Preview {
    NavigationStack {
        ProfileView(isLoggedIn: .constant(true))
    }
}
