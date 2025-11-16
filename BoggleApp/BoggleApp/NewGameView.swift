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
        VStack(spacing: 25) {
                Text("New Game")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Form {
                    Section {
                        Picker("Board Size", selection: $boardSize) {
                            ForEach(boardSizes, id: \.self) { size in
                                Text("\(size)×\(size)").tag(size)
                            }
                        }

                        Picker("Time Limit", selection: $timeLimit) {
                            ForEach(timeLimits, id: \.self) { seconds in
                                Text("\(seconds / 60) min").tag(seconds)
                            }
                        }

                        Picker("Max Players", selection: $maxPlayers) {
                            ForEach(playerCounts, id: \.self) { count in
                                Text("\(count) players").tag(count)
                            }
                        }

                        Toggle("Make Public", isOn: $isPublic)
                            .tint(.purple)
                            .onChange(of: isPublic) { oldValue, newValue in
                                if newValue && userGamerTag == nil {
                                    isPublic = false
                                    showGamerTagAlert = true
                                }
                            }
                    } header: {
                        Text("Game Settings")
                    } footer: {
                        if isPublic {
                            Text("Public games are discoverable by all players and appear on the leaderboard")
                                .font(.caption)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                }

                if let error = errorMessage {
                    Text(error)
                        .foregroundStyle(.red)
                        .font(.caption)
                }

                Button("Create Game") {
                    Task {
                        await createGame()
                    }
                }
                .buttonStyle(.borderedProminent)
                .tint(.purple)
                .disabled(isCreating)
                .font(.title3)

                if isCreating {
                    ProgressView("Creating game...")
                }
            }
            .padding()
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
