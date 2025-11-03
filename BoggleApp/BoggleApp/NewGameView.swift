//
// ABOUTME: View for creating a new game with customizable settings.
// ABOUTME: Allows configuration of board size, time limit, and maximum players before game creation.
//

import SwiftUI

struct NewGameView: View {
    @Binding var navigationPath: NavigationPath
    @State private var boardSize = 4
    @State private var timeLimit = 180
    @State private var maxPlayers = 2
    @State private var isCreating = false
    @State private var errorMessage: String?
    @State private var navigateToWaitingRoom = false
    @State private var createdGameId: String?
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
                    Section("Game Settings") {
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
                    }
                }
                .frame(height: 250)

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
                .disabled(isCreating)
                .font(.title3)

                if isCreating {
                    ProgressView("Creating game...")
                }
            }
            .padding()
            .navigationDestination(isPresented: $navigateToWaitingRoom) {
                if let gameId = createdGameId, let pid = playerId {
                    WaitingRoomView(navigationPath: $navigationPath, gameId: gameId, playerId: pid, maxPlayers: maxPlayers)
                }
            }
    }

    private func createGame() async {
        isCreating = true
        errorMessage = nil

        do {
            let game = try await BoggleAPI.shared.createGame(
                boardSize: boardSize,
                timeLimitSeconds: timeLimit,
                maxPlayers: maxPlayers
            )
            createdGameId = game.game_id

            // Join the game
            let joinResponse = try await BoggleAPI.shared.joinGame(gameId: game.game_id)
            playerId = joinResponse.player_id

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
