//
// ABOUTME: View for creating a new game with customizable settings.
// ABOUTME: Allows configuration of board size, time limit, and maximum players before game creation.
//

import SwiftUI
import OpenAPIClient

struct NewGameView: View {
    @Binding var navigationPath: NavigationPath
    @State private var boardSize = 4
    @State private var timeLimit = 180
    @State private var maxPlayers = 2
    @State private var isPublic = false
    @State private var isCreating = false
    @State private var errorMessage: String?
    @State private var navigateToWaitingRoom = false
    @State private var showGamerTagAlert = false
    @State private var userGamerTag: String?
    @State private var createdGameId: String?
    @State private var createdFriendlyCode: String?
    @State private var playerId: String?

    let boardSizes = [4, 5]
    let timeLimits = [60, 120, 180, 240, 300] // 1-5 minutes
    let playerCounts = [2, 3, 4]

    var body: some View {
        ScrollView {
            VStack(spacing: 25) {
                Text("New Game")
                    .font(.system(size: 36, weight: .black, design: .rounded))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.nebulaAccent, .nebulaPrimary],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .shadow(color: .nebulaPrimary.opacity(0.5), radius: 10, x: 0, y: 5)

                // Settings card
                VStack(spacing: 20) {
                    Text("Game Settings")
                        .font(.headline)
                        .foregroundStyle(Color.nebulaTextSecondary)
                        .frame(maxWidth: .infinity, alignment: .leading)

                    // Board Size
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Board Size")
                            .font(.subheadline)
                            .foregroundStyle(Color.nebulaTextSecondary)

                        HStack(spacing: 12) {
                            ForEach(boardSizes, id: \.self) { size in
                                Button {
                                    boardSize = size
                                } label: {
                                    Text("\(size)×\(size)")
                                        .font(.headline)
                                        .frame(maxWidth: .infinity)
                                        .padding(.vertical, 12)
                                        .background(
                                            RoundedRectangle(cornerRadius: 10)
                                                .fill(boardSize == size ? Color.nebulaPrimary : Color.nebulaSurface.opacity(0.6))
                                        )
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(boardSize == size ? Color.nebulaAccent : Color.white.opacity(0.1), lineWidth: 1)
                                        )
                                }
                                .foregroundStyle(.white)
                            }
                        }
                    }

                    // Time Limit
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Time Limit")
                            .font(.subheadline)
                            .foregroundStyle(Color.nebulaTextSecondary)

                        HStack(spacing: 8) {
                            ForEach(timeLimits, id: \.self) { seconds in
                                Button {
                                    timeLimit = seconds
                                } label: {
                                    Text("\(seconds / 60)m")
                                        .font(.subheadline)
                                        .fontWeight(.semibold)
                                        .frame(maxWidth: .infinity)
                                        .padding(.vertical, 10)
                                        .background(
                                            RoundedRectangle(cornerRadius: 8)
                                                .fill(timeLimit == seconds ? Color.nebulaPrimary : Color.nebulaSurface.opacity(0.6))
                                        )
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 8)
                                                .stroke(timeLimit == seconds ? Color.nebulaAccent : Color.white.opacity(0.1), lineWidth: 1)
                                        )
                                }
                                .foregroundStyle(.white)
                            }
                        }
                    }

                    // Max Players
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Max Players")
                            .font(.subheadline)
                            .foregroundStyle(Color.nebulaTextSecondary)

                        HStack(spacing: 12) {
                            ForEach(playerCounts, id: \.self) { count in
                                Button {
                                    maxPlayers = count
                                } label: {
                                    Text("\(count)")
                                        .font(.headline)
                                        .frame(maxWidth: .infinity)
                                        .padding(.vertical, 12)
                                        .background(
                                            RoundedRectangle(cornerRadius: 10)
                                                .fill(maxPlayers == count ? Color.nebulaPrimary : Color.nebulaSurface.opacity(0.6))
                                        )
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(maxPlayers == count ? Color.nebulaAccent : Color.white.opacity(0.1), lineWidth: 1)
                                        )
                                }
                                .foregroundStyle(.white)
                            }
                        }
                    }

                    // Public Toggle
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Make Public")
                                .font(.subheadline)
                                .foregroundStyle(.white)

                            if isPublic {
                                Text("Discoverable by all players")
                                    .font(.caption)
                                    .foregroundStyle(Color.nebulaTextSecondary)
                            }
                        }

                        Spacer()

                        Toggle("", isOn: $isPublic)
                            .tint(.nebulaPrimary)
                            .onChange(of: isPublic) { oldValue, newValue in
                                if newValue && userGamerTag == nil {
                                    isPublic = false
                                    showGamerTagAlert = true
                                }
                            }
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(Color.nebulaSurface.opacity(0.6))
                    )
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
                        await createGame()
                    }
                } label: {
                    HStack {
                        Image(systemName: "play.fill")
                        Text("Create Game")
                    }
                    .frame(maxWidth: .infinity)
                }
                .nebulaButtonStyle(color: .nebulaPrimary)
                .disabled(isCreating)

                if isCreating {
                    ProgressView()
                        .tint(.nebulaAccent)
                }
            }
            .padding()
        }
        .withNebulaBackground()
        .navigationDestination(isPresented: $navigateToWaitingRoom) {
            if let gameId = createdGameId, let pid = playerId, let friendlyCode = createdFriendlyCode {
                WaitingRoomView(navigationPath: $navigationPath, gameId: gameId, playerId: pid, maxPlayers: maxPlayers, friendlyCode: friendlyCode)
            }
        }
        .onAppear {
            // Reset to defaults when view appears to prevent state persistence
            boardSize = 4
            timeLimit = 180
            maxPlayers = 2
            isPublic = false
            errorMessage = nil

            // Fetch user's gamer tag to validate public game creation
            Task {
                do {
                    let profile = try await JumbleAPI.shared.getCurrentUserProfile()
                    userGamerTag = profile.gamerTag
                } catch {
                    print("⚠️ Failed to fetch user profile: \(error.localizedDescription)")
                }
            }
        }
        .alert("Gamer Tag Required", isPresented: $showGamerTagAlert) {
            Button("Set Gamer Tag") {
                navigationPath.append("profile")
            }
            Button("Cancel", role: .cancel) { }
        } message: {
            Text("You must set a gamer tag in your profile before creating public games.")
        }
    }

    private func createGame() async {
        isCreating = true
        errorMessage = nil

        // Final validation: prevent public game without gamer tag
        if isPublic && userGamerTag == nil {
            errorMessage = "You must set a gamer tag before creating public games"
            isCreating = false
            return
        }

        do {
            let game = try await JumbleAPI.shared.createGame(
                boardSize: boardSize,
                timeLimitSeconds: timeLimit,
                maxPlayers: maxPlayers,
                isPublic: isPublic
            )
            createdGameId = game.gameId
            createdFriendlyCode = game.friendlyCode

            // Join the game
            let joinResponse = try await JumbleAPI.shared.joinGame(gameId: game.gameId)
            playerId = joinResponse.playerId

            // Save active game for reconnection
            JumbleAPI.shared.saveActiveGame(gameId: game.gameId, playerId: joinResponse.playerId)

            // Navigate to waiting room
            navigateToWaitingRoom = true

        } catch let error as APIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "An unexpected error occurred"
        }

        isCreating = false
    }
}

#Preview {
    NewGameView(navigationPath: .constant(NavigationPath()))
}
