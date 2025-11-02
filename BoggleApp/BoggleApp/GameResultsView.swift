//
// ABOUTME: Game results screen showing final scores and words for all players.
// ABOUTME: Displays winner, player scores, and lists each player's words with strike-through for duplicates.
//

import SwiftUI

struct GameResultsView: View {
    let results: GameEndedMessage

    private var sortedResults: [PlayerFinalResult] {
        results.results.sorted { $0.total_score > $1.total_score }
    }

    var body: some View {
        VStack(spacing: 25) {
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

            // Player results
            ScrollView {
                VStack(spacing: 20) {
                    ForEach(sortedResults, id: \.player_name) { playerResult in
                        PlayerResultCard(
                            result: playerResult,
                            isWinner: playerResult.player_name == results.winner
                        )
                    }
                }
                .padding(.horizontal)
            }

            Button("Back to Lobby") {
                // TODO: Navigate back to lobby
            }
            .buttonStyle(.borderedProminent)
            .font(.title3)
        }
        .padding()
    }
}

struct PlayerResultCard: View {
    let result: PlayerFinalResult
    let isWinner: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Player name and score header
            HStack {
                Text(result.player_name)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundStyle(isWinner ? .green : .primary)

                Spacer()

                Text("\(result.total_score) pts")
                    .font(.title3)
                    .fontWeight(.semibold)
                    .foregroundStyle(isWinner ? .green : .blue)
            }

            // Words list
            if !result.words.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    ForEach(result.words, id: \.word) { wordResult in
                        HStack {
                            Text(wordResult.word)
                                .font(.body)
                                .strikethrough(!wordResult.valid, color: .red)
                                .foregroundStyle(wordResult.valid ? .primary : .gray)

                            Spacer()

                            Text("\(wordResult.score) pts")
                                .font(.caption)
                                .foregroundStyle(wordResult.valid ? .blue : .gray)
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
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(isWinner ? Color.green.opacity(0.1) : Color.gray.opacity(0.1))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(isWinner ? Color.green : Color.clear, lineWidth: 2)
        )
    }
}

#Preview {
    let sampleResults = GameEndedMessage(
        type: "game_ended",
        winner: "alice",
        results: [
            PlayerFinalResult(
                player_name: "alice",
                words: [
                    PlayerWordResult(word: "CAT", score: 1, valid: true),
                    PlayerWordResult(word: "DOG", score: 1, valid: true),
                    PlayerWordResult(word: "HOUSE", score: 3, valid: true)
                ],
                total_score: 5
            ),
            PlayerFinalResult(
                player_name: "bob",
                words: [
                    PlayerWordResult(word: "CAT", score: 0, valid: false),
                    PlayerWordResult(word: "FISH", score: 2, valid: true)
                ],
                total_score: 2
            )
        ]
    )

    return GameResultsView(results: sampleResults)
}
