//
// ABOUTME: View for joining an existing game by entering a game ID.
// ABOUTME: Validates and joins the game, then navigates to the waiting room.
//

import SwiftUI

struct JoinGameView: View {
    @Binding var navigationPath: NavigationPath
    @State private var gameId = ""
    @State private var isJoining = false
    @State private var errorMessage: String?
    @State private var navigateToWaitingRoom = false
    @State private var maxPlayers: Int?
    @State private var playerId: String?

    var body: some View {
        VStack(spacing: 25) {
                Text("Join Game")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text("Enter the game ID to join")
                    .font(.subheadline)
                    .foregroundStyle(.gray)

                TextField("Game ID", text: $gameId)
                    .textFieldStyle(.roundedBorder)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .padding(.horizontal)

                if let error = errorMessage {
                    Text(error)
                        .foregroundStyle(.red)
                        .font(.caption)
                }

                Button("Join") {
                    Task {
                        await joinGame()
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(isJoining || gameId.isEmpty)
                .font(.title3)

                if isJoining {
                    ProgressView("Joining game...")
                }

                Spacer()
            }
            .padding()
            .navigationDestination(isPresented: $navigateToWaitingRoom) {
                if let players = maxPlayers, let pid = playerId {
                    WaitingRoomView(navigationPath: $navigationPath, gameId: gameId, playerId: pid, maxPlayers: players)
                }
            }
    }

    private func joinGame() async {
        isJoining = true
        errorMessage = nil

        do {
            // First get the game state to know max_players
            let gameState = try await BoggleAPI.shared.getGameState(gameId: gameId)

            // Join the game
            let joinResponse = try await BoggleAPI.shared.joinGame(gameId: gameId)
            playerId = joinResponse.player_id

            // Store max_players (we'll need to add this to GameResponse model)
            maxPlayers = 4 // Default for now, TODO: get from gameState

            // Navigate to waiting room
            navigateToWaitingRoom = true

        } catch let error as APIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "An unexpected error occurred"
        }

        isJoining = false
    }
}

#Preview {
    JoinGameView(navigationPath: .constant(NavigationPath()))
}
