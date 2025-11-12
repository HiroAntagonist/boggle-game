//
// ABOUTME: View for joining an existing game by entering a friendly code.
// ABOUTME: Validates and joins the game, then navigates to the waiting room.
//

import SwiftUI
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

    var body: some View {
        VStack(spacing: 25) {
                Text("Join Game")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text("Enter the game code")
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

                Button("Join") {
                    Task {
                        await joinGame()
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(isJoining || friendlyCode.count < 8)
                .font(.title3)

                if isJoining {
                    ProgressView("Joining game...")
                }

                Spacer()
            }
            .padding()
            .navigationDestination(isPresented: $navigateToWaitingRoom) {
                if let players = maxPlayers, let pid = playerId, let gid = gameId {
                    WaitingRoomView(navigationPath: $navigationPath, gameId: gid, playerId: pid, maxPlayers: players, friendlyCode: friendlyCode)
                }
            }
    }

    private func joinGame() async {
        isJoining = true
        errorMessage = nil

        do {
            // Join the game by friendly code
            let joinResponse = try await BoggleAPI.shared.joinGameByCode(friendlyCode: friendlyCode)
            playerId = joinResponse.playerId
            gameId = joinResponse.gameId

            // Fetch game state to get the actual max_players value
            if let gid = gameId {
                let gameState = try await BoggleAPI.shared.getGameState(gameId: gid)
                maxPlayers = gameState.maxPlayers
            } else {
                maxPlayers = 4 // Fallback if gameId is somehow nil
            }

            // Save active game for reconnection
            if let gid = gameId, let pid = playerId {
                BoggleAPI.shared.saveActiveGame(gameId: gid, playerId: pid)
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
}

#Preview {
    JoinGameView(navigationPath: .constant(NavigationPath()))
}
