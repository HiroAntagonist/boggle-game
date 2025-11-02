//
// ABOUTME: Login and registration view for user authentication.
// ABOUTME: Allows users to sign in or create new accounts to access the Boggle game.
//

import SwiftUI

struct LoginView: View {
    @State private var username = ""
    @State private var email = ""
    @State private var password = ""
    @State private var isRegistering = false
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var isLoggedIn = false

    var body: some View {
        if isLoggedIn {
            LobbyView()
        } else {
            loginForm
        }
    }

    private var loginForm: some View {
        VStack(spacing: 20) {
            Text("Boggle")
                .font(.largeTitle)
                .fontWeight(.bold)

            VStack(spacing: 15) {
                TextField("Username", text: $username)
                    .textFieldStyle(.roundedBorder)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()

                if isRegistering {
                    TextField("Email", text: $email)
                        .textFieldStyle(.roundedBorder)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .keyboardType(.emailAddress)
                }

                SecureField("Password", text: $password)
                    .textFieldStyle(.roundedBorder)
            }
            .padding(.horizontal)

            if let error = errorMessage {
                Text(error)
                    .foregroundStyle(.red)
                    .font(.caption)
            }

            Button(isRegistering ? "Register" : "Login") {
                Task {
                    await handleAuth()
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(isLoading || username.isEmpty || password.isEmpty || (isRegistering && email.isEmpty))

            Button(isRegistering ? "Already have an account? Login" : "Need an account? Register") {
                isRegistering.toggle()
                errorMessage = nil
            }
            .font(.caption)

            if isLoading {
                ProgressView()
            }
        }
        .padding()
    }

    private func handleAuth() async {
        isLoading = true
        errorMessage = nil

        // Client-side validation
        if isRegistering {
            if username.count < 3 {
                errorMessage = "Username must be at least 3 characters"
                isLoading = false
                return
            }
            if password.count < 8 {
                errorMessage = "Password must be at least 8 characters"
                isLoading = false
                return
            }
            if !email.contains("@") || !email.contains(".") {
                errorMessage = "Please enter a valid email address"
                isLoading = false
                return
            }
        }

        do {
            if isRegistering {
                try await BoggleAPI.shared.register(
                    username: username,
                    email: email,
                    password: password
                )
                // After registration, automatically login
                try await BoggleAPI.shared.login(
                    username: username,
                    password: password
                )
            } else {
                try await BoggleAPI.shared.login(
                    username: username,
                    password: password
                )
            }
            isLoggedIn = true
        } catch let error as APIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "An unexpected error occurred"
        }

        isLoading = false
    }
}

#Preview {
    LoginView()
}
