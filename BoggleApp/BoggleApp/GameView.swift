//
// ABOUTME: Main game view displaying the Boggle board and word input interface.
// ABOUTME: Handles tile selection, word building, and submission to the backend.
//

import SwiftUI
import Combine

struct GameView: View {
    let gameId: String?
    let playerId: String?
    let initialBoard: [[String]]?

    @State private var board: [[String]] = []
    @State private var selectedWord = ""
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var webSocketManager: WebSocketManager?
    @State private var feedbackMessage: String?
    @State private var submittedWords: [String] = []
    @State private var lastResult: WordResultMessage?
    @State private var isSubmitting = false
    @State private var submittingWord = ""
    @State private var timeRemaining: Int?
    @State private var playerCount: Int = 0
    @State private var gameResults: GameEndedMessage?
    @State private var navigateToResults = false
    @State private var connectionStatus: ConnectionStatus = .disconnected

    init(gameId: String? = nil, playerId: String? = nil, initialBoard: [[String]]? = nil) {
        self.gameId = gameId
        self.playerId = playerId
        self.initialBoard = initialBoard
    }

    var body: some View {
        VStack(spacing: 20) {
            // Title and game info
            VStack(spacing: 8) {
                Text("Boggle")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                // Timer, player count, and connection status
                if !isLoading {
                    HStack(spacing: 20) {
                        // Connection status indicator
                        connectionStatusView

                        if let time = timeRemaining {
                            Label("\(formatTime(time))", systemImage: "clock")
                                .font(.headline)
                                .foregroundStyle(time < 30 ? .red : .blue)
                        }

                        if playerCount > 0 {
                            Label("\(playerCount) players", systemImage: "person.2")
                                .font(.headline)
                                .foregroundStyle(.gray)
                        }
                    }
                }
            }

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
                // Board grid with rotation button
                ZStack(alignment: .topTrailing) {
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

                    // Rotate button
                    Button(action: {
                        rotateBoard()
                    }) {
                        Image(systemName: "rotate.right")
                            .font(.title3)
                            .foregroundStyle(.blue)
                            .padding(8)
                            .background(Circle().fill(.white))
                            .shadow(radius: 2)
                    }
                    .padding(8)
                }

                // Word display and controls
                VStack(spacing: 10) {
                    Text("Word: \(isSubmitting ? submittingWord + "..." : selectedWord)")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundStyle((isSubmitting || !selectedWord.isEmpty) ? .blue : .gray)

                    // Feedback message (fixed height to prevent jumping)
                    Text(feedbackMessage ?? " ")
                        .font(.caption)
                        .foregroundStyle(feedbackMessage?.contains("✅") == true ? .green : .red)
                        .frame(height: 20)

                    HStack(spacing: 15) {
                        Button("Clear") {
                            selectedWord = ""
                            feedbackMessage = nil
                        }
                        .buttonStyle(.bordered)
                        .disabled(selectedWord.isEmpty)

                        Button("Submit") {
                            submitWord()
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(selectedWord.isEmpty || selectedWord.count < 3)
                    }

                    // Submitted words list
                    if !submittedWords.isEmpty {
                        VStack(alignment: .leading, spacing: 5) {
                            Text("Your words:")
                                .font(.caption)
                                .foregroundStyle(.gray)
                            ScrollView {
                                VStack(alignment: .leading, spacing: 3) {
                                    ForEach(submittedWords, id: \.self) { word in
                                        Text(word)
                                            .font(.caption)
                                    }
                                }
                            }
                            .frame(maxHeight: 100)
                        }
                    }
                }
            }
        }
        .padding()
        .task {
            await loadGame()
        }
        .navigationDestination(isPresented: $navigateToResults) {
            if let results = gameResults {
                GameResultsView(results: results)
            }
        }
    }

    private func loadGame() async {
        // If game data is provided (coming from waiting room), use it
        if let gid = gameId, let pid = playerId, let initBoard = initialBoard {
            board = initBoard

            // Connect WebSocket
            let wsManager = WebSocketManager(gameId: gid, playerId: pid)
            wsManager.onWordResult = { result in
                self.handleWordResult(result)
            }
            wsManager.onGameState = { state in
                self.timeRemaining = state.time_remaining
                self.playerCount = state.player_count
            }
            wsManager.onGameEnded = { endMessage in
                self.gameResults = endMessage
                self.navigateToResults = true
            }
            wsManager.connect()
            webSocketManager = wsManager

            // Observe connection status changes
            Task {
                for await status in wsManager.$connectionStatus.values {
                    await MainActor.run {
                        self.connectionStatus = status
                    }
                }
            }

            isLoading = false
            return
        }

        // Otherwise, create a new game (legacy single-player flow)
        isLoading = true
        errorMessage = nil

        do {
            // Create a new game
            let game = try await BoggleAPI.shared.createGame()
            board = game.board

            // Join the game
            let joinResponse = try await BoggleAPI.shared.joinGame(gameId: game.game_id)

            // Start the game
            try await BoggleAPI.shared.startGame(gameId: game.game_id)

            // Connect WebSocket
            let wsManager = WebSocketManager(gameId: game.game_id, playerId: joinResponse.player_id)
            wsManager.onWordResult = { result in
                self.handleWordResult(result)
            }
            wsManager.onGameState = { state in
                self.timeRemaining = state.time_remaining
                self.playerCount = state.player_count
            }
            wsManager.onGameEnded = { endMessage in
                self.gameResults = endMessage
                self.navigateToResults = true
            }
            wsManager.connect()
            webSocketManager = wsManager

            // Observe connection status changes
            Task {
                for await status in wsManager.$connectionStatus.values {
                    await MainActor.run {
                        self.connectionStatus = status
                    }
                }
            }

        } catch let error as APIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "An unexpected error occurred"
        }

        isLoading = false
    }

    private func rotateBoard() {
        guard !board.isEmpty else { return }

        let n = board.count
        var rotated = Array(repeating: Array(repeating: "", count: n), count: n)

        // Rotate 90 degrees clockwise: new[col][n-1-row] = old[row][col]
        for row in 0..<n {
            for col in 0..<n {
                rotated[col][n - 1 - row] = board[row][col]
            }
        }

        board = rotated
    }

    private func submitWord() {
        guard !selectedWord.isEmpty else { return }

        // Set submitting state
        isSubmitting = true
        submittingWord = selectedWord

        // Submit via WebSocket
        webSocketManager?.submitWord(selectedWord)

        // Clear the selected word
        selectedWord = ""
    }

    private func handleWordResult(_ result: WordResultMessage) {
        // Clear submitting state
        isSubmitting = false

        let newFeedback: String
        if result.valid {
            newFeedback = "✅ \(result.message)"
            submittedWords.append(result.word)
        } else {
            newFeedback = "❌ \(result.message)"
        }

        feedbackMessage = newFeedback

        // Clear feedback after 3 seconds
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            // Only clear if the message hasn't changed
            if self.feedbackMessage == newFeedback {
                self.feedbackMessage = nil
            }
        }
    }

    private func formatTime(_ seconds: Int) -> String {
        let mins = seconds / 60
        let secs = seconds % 60
        return String(format: "%d:%02d", mins, secs)
    }

    private var connectionStatusView: some View {
        Group {
            switch connectionStatus {
            case .connected:
                Label("Connected", systemImage: "wifi")
                    .font(.caption)
                    .foregroundStyle(.green)
            case .connecting:
                Label("Connecting", systemImage: "wifi.exclamationmark")
                    .font(.caption)
                    .foregroundStyle(.orange)
            case .reconnecting:
                Label("Reconnecting", systemImage: "wifi.slash")
                    .font(.caption)
                    .foregroundStyle(.orange)
            case .disconnected:
                Label("Disconnected", systemImage: "wifi.slash")
                    .font(.caption)
                    .foregroundStyle(.red)
            }
        }
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
