//
// ABOUTME: Login and registration view for user authentication.
// ABOUTME: Allows users to sign in or create new accounts to access the Boggle game.
//

import SwiftUI

struct LoginView: View {
    @State private var displayName = ""
    @State private var email = ""
    @State private var password = ""
    @State private var isRegistering = false
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var isLoggedIn = false

    var body: some View {
        if isLoggedIn {
            LobbyView(isLoggedIn: $isLoggedIn)
        } else {
            loginForm
        }
    }

    private var loginForm: some View {
        VStack(spacing: 20) {
            Text("Clauddle")
                .font(.largeTitle)
                .fontWeight(.bold)

            VStack(spacing: 15) {
                TextField("Email", text: $email)
                    .textFieldStyle(.roundedBorder)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .keyboardType(.emailAddress)

                SecureField("Password", text: $password)
                    .textFieldStyle(.roundedBorder)

                if isRegistering {
                    TextField("Display Name (optional)", text: $displayName)
                        .textFieldStyle(.roundedBorder)
                        .autocorrectionDisabled()
                }
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
            .disabled(isLoading || email.isEmpty || password.isEmpty)

            Button(isRegistering ? "Already have an account? Login" : "Need an account? Register") {
                isRegistering.toggle()
                errorMessage = nil
            }
            .font(.caption)

            // OR divider
            HStack {
                Rectangle()
                    .frame(height: 1)
                    .foregroundStyle(.gray.opacity(0.3))
                Text("OR")
                    .font(.caption)
                    .foregroundStyle(.gray)
                Rectangle()
                    .frame(height: 1)
                    .foregroundStyle(.gray.opacity(0.3))
            }
            .padding(.vertical, 10)

            // Google Sign-In button
            Button {
                Task {
                    await handleGoogleSignIn()
                }
            } label: {
                HStack {
                    Image(systemName: "g.circle.fill")
                    Text("Sign in with Google")
                }
                .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .disabled(isLoading)

            if isLoading {
                ProgressView()
            }
        }
        .padding()
        .onAppear {
            // Auto-authenticate if token exists in Keychain
            if BoggleAPI.shared.isAuthenticated {
                print("✅ Auto-authenticating with saved token")
                isLoggedIn = true
            }
        }
    }

    private func handleAuth() async {
        isLoading = true
        errorMessage = nil

        // Client-side validation
        if isRegistering {
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
                    email: email,
                    password: password,
                    displayName: displayName.isEmpty ? nil : displayName
                )
                // After registration, automatically login
                try await BoggleAPI.shared.login(
                    email: email,
                    password: password
                )
            } else {
                try await BoggleAPI.shared.login(
                    email: email,
                    password: password
                )
            }
            isLoggedIn = true
        } catch let error as APIError {
            // Handle backend API errors
            errorMessage = error.errorDescription
        } catch let urlError as URLError {
            // Handle network errors
            switch urlError.code {
            case .notConnectedToInternet:
                errorMessage = "No internet connection. Please check your network and try again"
            case .timedOut:
                errorMessage = "Request timed out. Please try again"
            case .cannotFindHost, .cannotConnectToHost:
                errorMessage = "Cannot reach server. Please try again later"
            default:
                errorMessage = "Network error: \(urlError.localizedDescription)"
            }
        } catch {
            // Catch-all for unexpected errors
            errorMessage = "An unexpected error occurred: \(error.localizedDescription)"
        }

        isLoading = false
    }

    private func handleGoogleSignIn() async {
        isLoading = true
        errorMessage = nil

        do {
            // Get ID token from Google
            let idToken = try await GoogleAuthService.shared.signIn()

            // Send ID token to backend
            try await BoggleAPI.shared.loginWithGoogle(idToken: idToken)

            isLoggedIn = true
        } catch let error as GoogleAuthError {
            // Handle Google Sign-In specific errors
            errorMessage = "Google Sign-In Error: \(error.errorDescription ?? "Unknown error")"
        } catch let error as APIError {
            // Handle backend API errors
            errorMessage = "Authentication Error: \(error.errorDescription ?? "Unknown error")"
        } catch let urlError as URLError {
            // Handle network errors
            switch urlError.code {
            case .notConnectedToInternet:
                errorMessage = "No internet connection. Please check your network and try again"
            case .timedOut:
                errorMessage = "Request timed out. Please try again"
            case .cannotFindHost, .cannotConnectToHost:
                errorMessage = "Cannot reach server. Please try again later"
            default:
                errorMessage = "Network error: \(urlError.localizedDescription)"
            }
        } catch {
            // Catch-all for unexpected errors
            errorMessage = "Google Sign-In failed: \(error.localizedDescription)"
        }

        isLoading = false
    }
}

#Preview {
    LoginView()
}
