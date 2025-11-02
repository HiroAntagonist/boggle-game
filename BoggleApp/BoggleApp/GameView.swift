//
// ABOUTME: Main game view displaying the Boggle board and word input interface.
// ABOUTME: Handles tile selection, word building, and submission to the backend.
//

import SwiftUI

struct GameView: View {
    @State private var board: [[String]] = []
    @State private var selectedWord = ""
    @State private var gameId: String?
    @State private var playerId: String?
    @State private var isLoading = true
    @State private var errorMessage: String?

    var body: some View {
        VStack(spacing: 20) {
            // Title
            Text("Boggle")
                .font(.largeTitle)
                .fontWeight(.bold)

            if isLoading {
                ProgressView("Creating game...")
            } else if let error = errorMessage {
                Text("Error: \(error)")
                    .foregroundStyle(.red)
                Button("Try Again") {
                    Task {
                        await loadGame()
                    }
                }
            } else {
                // Board grid
                VStack(spacing: 8) {
                    ForEach(0..<board.count, id: \.self) { row in
                        HStack(spacing: 8) {
                            ForEach(0..<board[row].count, id: \.self) { col in
                                LetterTile(letter: board[row][col]) {
                                    selectedWord += board[row][col]
                                }
                            }
                        }
                    }
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 15)
                        .fill(.gray.opacity(0.1))
                )

                // Word display and controls
                VStack(spacing: 10) {
                    Text("Word: \(selectedWord)")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundStyle(selectedWord.isEmpty ? .gray : .blue)

                    HStack(spacing: 15) {
                        Button("Clear") {
                            selectedWord = ""
                        }
                        .buttonStyle(.bordered)
                        .disabled(selectedWord.isEmpty)

                        Button("Submit") {
                            // TODO: Submit via WebSocket
                            print("Submitting word: \(selectedWord)")
                            selectedWord = ""
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(selectedWord.isEmpty)
                    }
                }
            }
        }
        .padding()
        .task {
            await loadGame()
        }
    }

    private func loadGame() async {
        isLoading = true
        errorMessage = nil

        do {
            // Create a new game
            let game = try await BoggleAPI.shared.createGame()
            gameId = game.game_id
            board = game.board

            // Join the game
            let joinResponse = try await BoggleAPI.shared.joinGame(gameId: game.game_id)
            playerId = joinResponse.player_id

            // Start the game
            try await BoggleAPI.shared.startGame(gameId: game.game_id)

        } catch let error as APIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "An unexpected error occurred"
        }

        isLoading = false
    }
}

// Reusable letter tile component
struct LetterTile: View {
    let letter: String
    let onTap: () -> Void

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 10)
                .fill(.blue)
                .frame(width: 70, height: 70)

            Text(letter)
                .font(.title)
                .fontWeight(.bold)
                .foregroundStyle(.white)
        }
        .onTapGesture {
            onTap()
        }
    }
}

#Preview {
    GameView()
}
