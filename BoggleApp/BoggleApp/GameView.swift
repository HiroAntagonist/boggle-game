//
// ABOUTME: Main game view displaying the Boggle board and word input interface.
// ABOUTME: Handles tile selection, word building, and submission to the backend.
//

import SwiftUI
import Combine

struct GameView: View {
    @Binding var navigationPath: NavigationPath
    let gameId: String?
    let playerId: String?
    let initialBoard: [[String]]?
    let timeLimit: Int?
    let startedAt: String?

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
    @State private var timerCancellable: AnyCancellable?
    @State private var showExitConfirmation = false
    @State private var isDragging = false
    @State private var currentDragWord = ""
    @State private var lastDraggedTile: String? = nil  // Track last tile to avoid adding same letter multiple times in one position

    init(navigationPath: Binding<NavigationPath>, gameId: String? = nil, playerId: String? = nil, initialBoard: [[String]]? = nil, timeLimit: Int? = nil, startedAt: String? = nil) {
        self._navigationPath = navigationPath
        self.gameId = gameId
        self.playerId = playerId
        self.initialBoard = initialBoard
        self.timeLimit = timeLimit
        self.startedAt = startedAt
    }

    var body: some View {
        GeometryReader { geometry in
            let isLandscape = geometry.size.width > geometry.size.height

            ZStack {
                // Main content - different layouts for portrait vs landscape
                if isLandscape {
                    landscapeLayout(containerSize: geometry.size)
                } else {
                    portraitLayout(containerSize: geometry.size)
                }

                // Overlay: Centered title (both orientations)
                if !isLoading && errorMessage == nil {
                    VStack {
                        Text("Boggle")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .frame(maxWidth: .infinity)
                            .padding(.top)

                        Spacer()
                    }
                }

                // Exit button overlay (top-left corner, both orientations)
                if !isLoading && errorMessage == nil {
                    VStack {
                        HStack {
                            Button(action: {
                                showExitConfirmation = true
                            }) {
                                Image(systemName: "xmark.circle.fill")
                                    .font(.title2)
                                    .foregroundStyle(.red)
                            }
                            .padding(.leading)
                            .padding(.top)

                            Spacer()
                        }

                        Spacer()
                    }
                }
            }
            .task {
                await loadGame()
            }
            .navigationDestination(isPresented: $navigateToResults) {
                if let results = gameResults {
                    GameResultsView(navigationPath: $navigationPath, results: results)
                }
            }
            .navigationBarBackButtonHidden(true)
            .alert("Exit Game?", isPresented: $showExitConfirmation) {
                Button("Cancel", role: .cancel) { }
                Button("Exit", role: .destructive) {
                    navigationPath = NavigationPath()
                }
            } message: {
                Text("Are you sure you want to exit? Your progress will be lost.")
            }
            .onAppear {
                if isSmallDevice {
                    AppDelegate.orientationLock = .portrait
                    UIDevice.current.setValue(UIInterfaceOrientation.portrait.rawValue, forKey: "orientation")
                    UIViewController.attemptRotationToDeviceOrientation()
                }
            }
            .onDisappear {
                AppDelegate.orientationLock = .all
            }
        }
    }

    // Portrait layout - vertical stack with percentage-based sizing
    private func portraitLayout(containerSize: CGSize) -> some View {
        let topHeight = containerSize.height * 0.20
        let boardHeight = containerSize.height * 0.40
        let controlsHeight = containerSize.height * 0.40

        let spacing: CGFloat = 8
        let padding: CGFloat = 16

        // Calculate tile size to fit in 40% board area
        let availableBoardHeight = boardHeight - padding * 2
        let tileSize = (availableBoardHeight - CGFloat(board.count - 1) * spacing) / CGFloat(board.count)
        // Cap at reasonable sizes
        let finalTileSize = min(max(tileSize, 40), 70)

        return VStack(spacing: 0) {
            // Top 20%: Title, exit button, connection status, timer
            VStack(spacing: 10) {
                Spacer()
                    .frame(height: 50)

                // Timer, player count, and connection status
                if !isLoading {
                    HStack(spacing: 20) {
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
            .frame(height: topHeight)

            // Middle 40%: Board grid (centered)
            if isLoading {
                VStack {
                    Spacer()
                    ProgressView("Creating game...")
                    Spacer()
                }
                .frame(height: boardHeight)
            } else if let error = errorMessage {
                VStack {
                    Spacer()
                    Text("Error: \(error)")
                        .foregroundStyle(.red)
                    Button("Try Again") {
                        Task {
                            await loadGame()
                        }
                    }
                    Spacer()
                }
                .frame(height: boardHeight)
            } else {
                HStack {
                    Spacer()

                    ZStack(alignment: .topTrailing) {
                        // Background with board
                        GeometryReader { geometry in
                            VStack(spacing: spacing) {
                                ForEach(0..<board.count, id: \.self) { row in
                                    HStack(spacing: spacing) {
                                        ForEach(0..<board[row].count, id: \.self) { col in
                                            LetterTile(letter: board[row][col], size: finalTileSize) {
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
                            .gesture(
                                DragGesture(minimumDistance: 0)
                                    .onChanged { value in
                                        handleDrag(at: value.location, in: geometry.size)
                                    }
                                    .onEnded { _ in
                                        endDrag()
                                    }
                            )
                        }

                        // Rotate button - anchored to grey background corner
                        Button(action: {
                            rotateBoard()
                        }) {
                            Image(systemName: "rotate.right")
                                .font(.caption)
                                .fontWeight(.semibold)
                                .foregroundStyle(.blue)
                                .padding(6)
                                .background(
                                    Circle()
                                        .fill(.white.opacity(0.95))
                                        .shadow(color: .black.opacity(0.15), radius: 3, x: 0, y: 1)
                                )
                        }
                        .offset(x: -6, y: 6)
                    }
                    .frame(width: CGFloat(board.count) * finalTileSize + CGFloat(board.count - 1) * spacing + padding * 2)

                    Spacer()
                }
                .frame(height: boardHeight)
            }

            // Bottom 40%: Word controls and submitted words
            VStack(spacing: 10) {
                if !isLoading && errorMessage == nil {
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

                        Button(action: {
                            if !selectedWord.isEmpty {
                                selectedWord.removeLast()
                                feedbackMessage = nil
                            }
                        }) {
                            Image(systemName: "delete.left")
                        }
                        .buttonStyle(.bordered)
                        .disabled(selectedWord.isEmpty)

                        Button("Submit") {
                            submitWord()
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(selectedWord.isEmpty || selectedWord.count < 3)
                    }

                    // Submitted words list (3 columns on small devices, 2 on larger)
                    if !submittedWords.isEmpty {
                        let recentWords = Array(submittedWords.suffix(30).reversed())
                        let columnCount = isSmallDevice ? 3 : 2
                        let columns = Array(repeating: GridItem(.flexible()), count: columnCount)

                        VStack(alignment: .leading, spacing: 5) {
                            Text("Your words:")
                                .font(.caption)
                                .foregroundStyle(.gray)
                            ScrollView {
                                LazyVGrid(columns: columns, alignment: .leading, spacing: 3) {
                                    ForEach(recentWords, id: \.self) { word in
                                        Text(word)
                                            .font(.caption)
                                            .lineLimit(1)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            .frame(height: controlsHeight)
            .padding(.horizontal)
        }
    }

    // Landscape layout - side-by-side (board on left, controls on right)
    private func landscapeLayout(containerSize: CGSize) -> some View {
        let tileSize = calculateTileSize(containerHeight: containerSize.height, boardSize: board.count, isLandscape: true)
        let spacing: CGFloat = 8
        let boardHeight = CGFloat(board.count) * tileSize + CGFloat(board.count - 1) * spacing + 16

        return HStack(spacing: 20) {
            // Left side: Board
            VStack {
                // Spacer for overlay (title + exit button)
                Spacer()
                    .frame(height: 50)

                // Timer, player count, and connection status
                if !isLoading {
                    HStack(spacing: 20) {
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
                    GeometryReader { geometry in
                        ZStack(alignment: .topTrailing) {
                            // Background with board
                            VStack(spacing: spacing) {
                                ForEach(0..<board.count, id: \.self) { row in
                                    HStack(spacing: spacing) {
                                        ForEach(0..<board[row].count, id: \.self) { col in
                                            LetterTile(letter: board[row][col], size: tileSize) {
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
                            .gesture(
                                DragGesture(minimumDistance: 0)
                                    .onChanged { value in
                                        handleDrag(at: value.location, in: geometry.size)
                                    }
                                    .onEnded { _ in
                                        endDrag()
                                    }
                            )

                            // Rotate button - anchored to grey background corner
                            Button(action: {
                                rotateBoard()
                            }) {
                                Image(systemName: "rotate.right")
                                    .font(.caption)
                                    .fontWeight(.semibold)
                                    .foregroundStyle(.blue)
                                    .padding(6)
                                    .background(
                                        Circle()
                                            .fill(.white.opacity(0.95))
                                            .shadow(color: .black.opacity(0.15), radius: 3, x: 0, y: 1)
                                    )
                            }
                            .offset(x: -6, y: 6)
                        }
                    }
                    .frame(height: boardHeight)
                }

                Spacer()
            }
            .frame(maxWidth: .infinity)

            // Right side: Word controls and submitted words
            VStack(spacing: 20) {
                // Spacer for overlay
                Spacer()
                    .frame(height: 50)

                if !isLoading && errorMessage == nil {
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

                            Button(action: {
                                if !selectedWord.isEmpty {
                                    selectedWord.removeLast()
                                    feedbackMessage = nil
                                }
                            }) {
                                Image(systemName: "delete.left")
                            }
                            .buttonStyle(.bordered)
                            .disabled(selectedWord.isEmpty)

                            Button("Submit") {
                                submitWord()
                            }
                            .buttonStyle(.borderedProminent)
                            .disabled(selectedWord.isEmpty || selectedWord.count < 3)
                        }

                        // Submitted words list (3 columns in landscape)
                        if !submittedWords.isEmpty {
                            let recentWords = Array(submittedWords.suffix(30).reversed())
                            let columns = [GridItem(.flexible()), GridItem(.flexible()), GridItem(.flexible())]

                            VStack(alignment: .leading, spacing: 5) {
                                Text("Your words:")
                                    .font(.caption)
                                    .foregroundStyle(.gray)
                                ScrollView {
                                    LazyVGrid(columns: columns, alignment: .leading, spacing: 3) {
                                        ForEach(recentWords, id: \.self) { word in
                                            Text(word)
                                                .font(.caption)
                                                .lineLimit(1)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Spacer()
            }
            .frame(maxWidth: .infinity)
        }
        .padding()
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
                self.stopCountdownTimer()
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

            // Start countdown timer if time limit and started_at provided
            if let limit = timeLimit, let started = startedAt {
                print("🕐 Starting countdown timer: timeLimit=\(limit), startedAt=\(started)")
                startCountdownTimer(from: limit, startedAt: started)
            } else {
                print("⚠️ No timer started: timeLimit=\(String(describing: timeLimit)), startedAt=\(String(describing: startedAt))")
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
                self.stopCountdownTimer()
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

    private func startCountdownTimer(from timeLimit: Int, startedAt: String) {
        // Cancel any existing timer
        timerCancellable?.cancel()

        // Parse started_at timestamp (Python's isoformat() includes microseconds)
        // Try ISO8601 with fractional seconds first
        let iso8601Formatter = ISO8601DateFormatter()
        iso8601Formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]

        // Fallback to DateFormatter if ISO8601 fails
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
        dateFormatter.timeZone = TimeZone(identifier: "UTC")

        guard let startTime = iso8601Formatter.date(from: startedAt) ?? dateFormatter.date(from: startedAt) else {
            print("❌ Failed to parse started_at: \(startedAt)")
            return
        }

        // Calculate initial remaining time
        let endTime = startTime.addingTimeInterval(TimeInterval(timeLimit))
        let remaining = max(0, Int(endTime.timeIntervalSinceNow))
        print("🕐 Timer calculated: remaining=\(remaining)s, endTime=\(endTime), now=\(Date())")
        timeRemaining = remaining

        // Create a timer that fires every second and recalculates from server time
        timerCancellable = Timer.publish(every: 1.0, on: .main, in: .common)
            .autoconnect()
            .sink { _ in
                let newRemaining = max(0, Int(endTime.timeIntervalSinceNow))
                self.timeRemaining = newRemaining
            }
    }

    private func stopCountdownTimer() {
        timerCancellable?.cancel()
        timerCancellable = nil
    }

    private func handleDrag(at location: CGPoint, in size: CGSize) {
        guard !board.isEmpty else { return }

        // Start drag if not already dragging
        if !isDragging {
            isDragging = true
            currentDragWord = ""
            lastDraggedTile = nil
        }

        // Calculate which tile the drag is over
        // Account for padding (16px total: 8px on each side)
        let adjustedX = location.x - 8
        let adjustedY = location.y - 8

        // Calculate tile size including spacing
        let boardSize = board.count
        let tileSize: CGFloat = 70
        let spacing: CGFloat = 8
        let tileWithSpacing = tileSize + spacing

        let col = Int(adjustedX / tileWithSpacing)
        let row = Int(adjustedY / tileWithSpacing)

        // Check if within bounds
        guard row >= 0 && row < boardSize && col >= 0 && col < boardSize else { return }

        let tileKey = "\(row)-\(col)"

        // Only add letter if we've moved to a different tile
        if lastDraggedTile != tileKey {
            currentDragWord += board[row][col]
            lastDraggedTile = tileKey
        }
    }

    private func endDrag() {
        isDragging = false
        // Transfer the drag word to selected word
        if !currentDragWord.isEmpty {
            selectedWord = currentDragWord
        }
        currentDragWord = ""
        lastDraggedTile = nil
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

    private var isSmallDevice: Bool {
        UIScreen.main.bounds.width <= 375
    }

    private func calculateTileSize(containerHeight: CGFloat, boardSize: Int, isLandscape: Bool) -> CGFloat {
        let spacing: CGFloat = 8
        let padding: CGFloat = 16
        let timerHeight: CGFloat = 50
        let spacerHeight: CGFloat = 50

        // In landscape, word controls and list are beside the board (not below)
        // In portrait, they're stacked below the board
        let wordControlsHeight: CGFloat = isLandscape ? 0 : 150  // Word display + buttons + feedback
        let wordsListHeight: CGFloat = isLandscape ? 0 : 100     // Submitted words list space

        // Available height after UI elements
        let availableHeight = containerHeight - timerHeight - spacerHeight - wordControlsHeight - wordsListHeight - padding

        // Calculate max tile size that fits
        // Formula: availableHeight = boardSize * tileSize + (boardSize - 1) * spacing
        let maxTileSize = (availableHeight - CGFloat(boardSize - 1) * spacing) / CGFloat(boardSize)

        // Cap at 70px maximum to avoid oversized tiles on large screens
        return min(maxTileSize, 70)
    }
}

// Reusable letter tile component
struct LetterTile: View {
    let letter: String
    let size: CGFloat
    let onTap: () -> Void

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 10)
                .fill(.blue)
                .frame(width: size, height: size)

            Text(letter)
                .font(.system(size: size * 0.4))
                .fontWeight(.bold)
                .foregroundStyle(.white)
        }
        .onTapGesture {
            onTap()
        }
    }
}

#Preview {
    GameView(navigationPath: .constant(NavigationPath()))
}
