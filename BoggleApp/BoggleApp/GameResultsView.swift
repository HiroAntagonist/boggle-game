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
            VStack(spacing: 15) {
                Text("Game Over!")
                    .font(.system(size: 40, weight: .black, design: .rounded))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.nebulaAccent, .nebulaPrimary],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .shadow(color: .nebulaPrimary.opacity(0.5), radius: 10, x: 0, y: 5)

                if let winner = results.winner {
                    HStack(spacing: 8) {
                        Text(winner)
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundStyle(Color.nebulaSuccess)
                        Text("Wins!")
                            .font(.title)
                            .foregroundStyle(.white)
                    }
                    .nebulaGlow(color: .nebulaSuccess, radius: 8)
                } else {
                    Text("It's a Tie!")
                        .font(.title)
                        .foregroundStyle(Color.nebulaAccent)
                }
            }
            .padding(.top, 30)
            .padding(.bottom, 20)

            // Player results - scrollable
            ScrollView {
                VStack(spacing: 16) {
                    ForEach(sortedResults, id: \.playerName) { playerResult in
                        NebulaPlayerResultCard(
                            result: playerResult,
                            isWinner: playerResult.playerName == results.winner
                        )
                    }
                }
                .padding(.horizontal)
                .padding(.bottom, 20)
            }

            // Button at bottom
            Button {
                // Clear active game state since game has ended
                JumbleAPI.shared.clearActiveGame()
                // Clear navigation path to return to lobby
                navigationPath = NavigationPath()
            } label: {
                HStack {
                    Image(systemName: "house.fill")
                    Text("Back to Lobby")
                }
                .frame(maxWidth: .infinity)
            }
            .nebulaButtonStyle(color: .nebulaPrimary)
            .padding(.vertical, 15)
            .padding(.horizontal)
        }
        .withNebulaBackground()
        .navigationBarBackButtonHidden(true)
    }
}

struct NebulaPlayerResultCard: View {
    let result: PlayerFinalResult
    let isWinner: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Player name and score header
            HStack {
                HStack(spacing: 8) {
                    if isWinner {
                        Image(systemName: "crown.fill")
                            .foregroundStyle(Color.yellow)
                    }
                    Text(result.playerName)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundStyle(isWinner ? Color.nebulaSuccess : .white)
                }

                Spacer()

                Text("\(result.totalScore) pts")
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundStyle(isWinner ? Color.nebulaSuccess : Color.nebulaAccent)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(
                        Capsule()
                            .fill(isWinner ? Color.nebulaSuccess.opacity(0.2) : Color.nebulaAccent.opacity(0.2))
                    )
            }

            // Words list
            if !result.words.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    ForEach(result.words, id: \.word) { wordResult in
                        HStack {
                            Text(wordResult.word)
                                .font(.body)
                                .strikethrough(!wordResult.valid, color: Color.nebulaError)
                                .foregroundStyle(wordResult.valid ? .white : Color.nebulaTextSecondary)

                            Spacer()

                            if wordResult.valid {
                                Text("+\(wordResult.score)")
                                    .font(.caption)
                                    .fontWeight(.semibold)
                                    .foregroundStyle(Color.nebulaAccent)
                            } else {
                                Text("0")
                                    .font(.caption)
                                    .foregroundStyle(Color.nebulaTextSecondary)
                            }
                        }
                    }
                }
                .padding(.top, 4)
            } else {
                Text("No words found")
                    .font(.caption)
                    .foregroundStyle(Color.nebulaTextSecondary)
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.nebulaSurface.opacity(isWinner ? 0.7 : 0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(isWinner ? Color.nebulaSuccess.opacity(0.5) : Color.white.opacity(0.1), lineWidth: isWinner ? 2 : 1)
                )
        )
        .nebulaGlow(color: isWinner ? .nebulaSuccess : .clear, radius: isWinner ? 5 : 0)
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
