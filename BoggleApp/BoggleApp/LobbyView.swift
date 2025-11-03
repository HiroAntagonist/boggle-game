//
// ABOUTME: Lobby view where players choose to create a new game or join an existing one.
// ABOUTME: Acts as the main menu after login, routing to game creation or game joining flows.
//

import SwiftUI

struct LobbyView: View {
    @State private var navigationPath = NavigationPath()

    var body: some View {
        NavigationStack(path: $navigationPath) {
            VStack(spacing: 30) {
                Text("Boggle")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text("Ready to play?")
                    .font(.title2)
                    .foregroundStyle(.gray)

                VStack(spacing: 15) {
                    NavigationLink(value: "newGame") {
                        Text("New Game")
                            .frame(width: 200)
                    }
                    .buttonStyle(.borderedProminent)
                    .font(.title3)

                    NavigationLink(value: "joinGame") {
                        Text("Join Game")
                            .frame(width: 200)
                    }
                    .buttonStyle(.bordered)
                    .font(.title3)
                }
            }
            .padding()
            .navigationDestination(for: String.self) { destination in
                switch destination {
                case "newGame":
                    NewGameView(navigationPath: $navigationPath)
                case "joinGame":
                    JoinGameView(navigationPath: $navigationPath)
                default:
                    EmptyView()
                }
            }
        }
    }
}

#Preview {
    LobbyView()
}
