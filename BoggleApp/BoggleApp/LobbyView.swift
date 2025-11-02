//
// ABOUTME: Lobby view where players choose to create a new game or join an existing one.
// ABOUTME: Acts as the main menu after login, routing to game creation or game joining flows.
//

import SwiftUI

struct LobbyView: View {
    @State private var showNewGame = false
    @State private var showJoinGame = false

    var body: some View {
        VStack(spacing: 30) {
            Text("Boggle")
                .font(.largeTitle)
                .fontWeight(.bold)

            Text("Ready to play?")
                .font(.title2)
                .foregroundStyle(.gray)

            VStack(spacing: 15) {
                Button("New Game") {
                    showNewGame = true
                }
                .buttonStyle(.borderedProminent)
                .font(.title3)
                .frame(width: 200)

                Button("Join Game") {
                    showJoinGame = true
                }
                .buttonStyle(.bordered)
                .font(.title3)
                .frame(width: 200)
            }
        }
        .padding()
        .sheet(isPresented: $showNewGame) {
            NewGameView()
        }
        .sheet(isPresented: $showJoinGame) {
            JoinGameView()
        }
    }
}

#Preview {
    LobbyView()
}
