//
// ABOUTME: Game results screen showing final scores and words for all players.
// ABOUTME: Displays winner, player scores, and lists each player's words with strike-through for duplicates.
//

import SwiftUI

struct GameResultsView: View {
    @Binding var navigationPath: NavigationPath
    let results: GameEndedMessage

    private var sortedResults: [PlayerFinalResult] {
        results.results.sorted { $0.totalScore > $1.totalScore }
    }

    var body: some View {
        VStack(spacing: 0) {
            // Winner announcement
            VStack(spacing: 10) {
                Text("Game Over!")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                if let winner = results.winner {
                    Text("\(winner) Wins! 🎉")
                        .font(.title)
                        .foregroundStyle(.green)
                } else {
                    Text("It's a Tie!")
                        .font(.title)
                        .foregroundStyle(.orange)
                }
            }
            .padding(.top, 20)
            .padding(.bottom, 15)

            // Player results - scrollable
            ScrollView {
                VStack(spacing: 20) {
                    ForEach(sortedResults, id: \.playerName) { playerResult in
                        PlayerResultCard(
                            result: playerResult,
                            isWinner: playerResult.playerName == results.winner
                        )
                    }
                }
                .padding(.horizontal)
                .padding(.bottom, 20)
            }

            // Button at bottom
            Button("Back to Lobby") {
                // Clear active game state since game has ended
                BoggleAPI.shared.clearActiveGame()
                // Clear navigation path to return to lobby
                navigationPath = NavigationPath()
            }
            .buttonStyle(.borderedProminent)
            .font(.title3)
            .padding(.vertical, 15)
            .padding(.horizontal)
        }
        .navigationBarBackButtonHidden(true)
    }
}

struct PlayerResultCard: View {
    let result: PlayerFinalResult
    let isWinner: Bool

    private var backgroundColor: Color {
        isWinner ? Color.green.opacity(0.1) : Color.gray.opacity(0.1)
    }

    private var borderColor: Color {
        isWinner ? .green : .clear
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Player name and score header
            HStack {
                Text(result.playerName)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundStyle(isWinner ? .green : .primary)

                Spacer()

                Text("\(result.totalScore) pts")
                    .font(.title3)
                    .fontWeight(.semibold)
                    .foregroundStyle(isWinner ? .green : .purple)
            }

            // Words list
            if !result.words.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    ForEach(result.words, id: \.word) { wordResult in
                        HStack {
                            Text(wordResult.word)
                                .font(.body)
                                .strikethrough(!wordResult.valid, color: .red)
                                .foregroundStyle(wordResult.valid ? Color.primary : Color.gray)

                            Spacer()

                            Text("\(wordResult.score) pts")
                                .font(.caption)
                                .foregroundStyle(wordResult.valid ? Color.purple : Color.gray)
                        }
                    }
                }
                .padding(.top, 4)
            } else {
                Text("No words found")
                    .font(.caption)
                    .foregroundStyle(.gray)
            }
        }
        .padding()
        .background(RoundedRectangle(cornerRadius: 12).fill(backgroundColor))
        .overlay(RoundedRectangle(cornerRadius: 12).stroke(borderColor, lineWidth: 2))
    }
}

#Preview {
    let sampleResults = GameEndedMessage(
        type: "game_ended",
        winner: "alice",
        results: [
            PlayerFinalResult(
                playerName: "alice",
                words: [
                    PlayerWordResult(word: "CAT", score: 1, valid: true),
                    PlayerWordResult(word: "DOG", score: 1, valid: true),
                    PlayerWordResult(word: "HOUSE", score: 3, valid: true)
                ],
                totalScore: 5
            ),
            PlayerFinalResult(
                playerName: "bob",
                words: [
                    PlayerWordResult(word: "CAT", score: 0, valid: false),
                    PlayerWordResult(word: "FISH", score: 2, valid: true)
                ],
                totalScore: 2
            )
        ]
    )

    return GameResultsView(navigationPath: .constant(NavigationPath()), results: sampleResults)
}
