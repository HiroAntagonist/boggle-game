//
// ABOUTME: Lobby view where players choose to create a new game or join an existing one.
// ABOUTME: Acts as the main menu after login, routing to game creation or game joining flows.
//

import SwiftUI

struct LobbyView: View {
    @Binding var isLoggedIn: Bool
    @State private var navigationPath = NavigationPath()
    @State private var userDisplayName: String?
    @State private var userEmail: String?

    var body: some View {
        NavigationStack(path: $navigationPath) {
            VStack(spacing: 30) {
                Text("Clauddle")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                // Display logged-in user info
                if let displayName = userDisplayName {
                    Text("Welcome, \(displayName)!")
                        .font(.title3)
                        .foregroundStyle(.secondary)
                } else if let email = userEmail {
                    Text("Logged in as \(email)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

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
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        handleSignOut()
                    } label: {
                        Label("Sign Out", systemImage: "rectangle.portrait.and.arrow.right")
                    }
                }
            }
            .onAppear {
                loadUserInfo()
            }
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

    private func loadUserInfo() {
        if let user = BoggleAPI.shared.getCurrentUser() {
            userEmail = user.email
            userDisplayName = user.displayName
            print("✅ Loaded user info: \(user.displayName ?? user.email)")
        }
    }

    private func handleSignOut() {
        BoggleAPI.shared.logout()
        isLoggedIn = false
    }
}

#Preview {
    LobbyView(isLoggedIn: .constant(true))
}
