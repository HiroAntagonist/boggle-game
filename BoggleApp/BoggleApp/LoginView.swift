//
// ABOUTME: Login and registration view for user authentication.
// ABOUTME: Allows users to sign in or create new accounts to access the Boggle game.
//

import SwiftUI
import AuthenticationServices

struct LoginView: View {
    @State private var displayName = ""
    @State private var email = ""
    @State private var password = ""
    @State private var isRegistering = false
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var isLoggedIn = false

    var body: some View {
        Group {
            if isLoggedIn {
                LobbyView(isLoggedIn: $isLoggedIn)
            } else {
                loginForm
                    .withNebulaBackground()
                    .preferredColorScheme(.dark)
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: .forceLogout)) { _ in
            // Server returned 401 - user no longer exists in database
            isLoggedIn = false
            errorMessage = "Session expired. Please log in again."
            print("⚠️ Force logout triggered - user returned to login screen")
        }
    }

    private var loginForm: some View {
        VStack(spacing: 25) {
            Text("Jumble")
                .font(.system(size: 48, weight: .black, design: .rounded))
                .foregroundStyle(
                    LinearGradient(
                        colors: [.nebulaAccent, .nebulaPrimary],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .shadow(color: .nebulaPrimary.opacity(0.5), radius: 10, x: 0, y: 5)
                .padding(.bottom, 20)

            // Google Sign In Button
            Button(action: {
                Task {
                    await handleGoogleSignIn()
                }
            }) {
                HStack {
                    Image(systemName: "g.circle.fill") // Simplified Google Icon
                        .resizable()
                        .frame(width: 20, height: 20)
                    Text("Sign in with Google")
                        .font(.headline)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.white)
                .foregroundColor(.black)
                .cornerRadius(10)
            }
            .padding(.horizontal)
            .disabled(isLoading) // Disable if loading

            // Apple Sign In Button
            SignInWithAppleButton(
                onRequest: { request in
                    // Handled by AppleAuthService in ViewModel usually, but here we can just configure scope
                    request.requestedScopes = [.fullName, .email]
                },
                onCompletion: { result in
                    Task {
                        await handleAppleLogin(result: result)
                    }
                }
            )
            .signInWithAppleButtonStyle(.black) // Match system style
            .frame(maxWidth: .infinity) // Match other buttons approx
            .frame(height: 50)
            .cornerRadius(10)
            .padding(.horizontal)
            .disabled(isLoading) // Disable if loading

            // OR divider
            HStack {
                Rectangle()
                    .frame(height: 1)
                    .foregroundStyle(Color.white.opacity(0.2))
                Text("OR")
                    .font(.caption)
                    .foregroundStyle(Color.white.opacity(0.6))
                Rectangle()
                    .frame(height: 1)
                    .foregroundStyle(Color.white.opacity(0.2))
            }
            .padding(.vertical, 10)

            VStack(spacing: 15) {
                TextField("Email", text: $email)
                    .textFieldStyle(.plain)
                    .padding()
                    .background(Color.nebulaSurface.opacity(0.6))
                    .cornerRadius(12)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.white.opacity(0.2), lineWidth: 1)
                    )
                    .foregroundStyle(.white)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .keyboardType(.emailAddress)

                SecureField("Password", text: $password)
                    .textFieldStyle(.plain)
                    .padding()
                    .background(Color.nebulaSurface.opacity(0.6))
                    .cornerRadius(12)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.white.opacity(0.2), lineWidth: 1)
                    )
                    .foregroundStyle(.white)

                if isRegistering {
                    TextField("Display Name (optional)", text: $displayName)
                        .textFieldStyle(.plain)
                        .padding()
                        .background(Color.nebulaSurface.opacity(0.6))
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                        )
                        .foregroundStyle(.white)
                        .autocorrectionDisabled()
                }
            }
            .padding(.horizontal)

            if let error = errorMessage {
                Text(error)
                    .foregroundStyle(Color.nebulaError)
                    .font(.caption)
                    .padding(8)
                    .background(Color.nebulaError.opacity(0.1))
                    .cornerRadius(8)
            }

            Button(isRegistering ? "Register" : "Login") {
                Task {
                    await handleAuth()
                }
            }
            .nebulaButtonStyle(color: .nebulaPrimary)
            .disabled(isLoading || email.isEmpty || password.isEmpty)

            Button(isRegistering ? "Already have an account? Login" : "Need an account? Register") {
                withAnimation {
                    isRegistering.toggle()
                    errorMessage = nil
                }
            }
            .font(.caption)
            .foregroundStyle(Color.nebulaAccent)

            if isLoading {
                ProgressView()
                    .tint(.nebulaAccent)
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 24)
                .fill(Color.nebulaSurface.opacity(0.5))
                .shadow(color: .black.opacity(0.3), radius: 20, x: 0, y: 10)
        )
        .padding()
        .onAppear {
            // Auto-authenticate if token exists in Keychain
            if JumbleAPI.shared.isAuthenticated {
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
                try await JumbleAPI.shared.register(
                    email: email,
                    password: password,
                    displayName: displayName.isEmpty ? nil : displayName
                )
                // After registration, automatically login
                try await JumbleAPI.shared.login(
                    email: email,
                    password: password
                )
            } else {
                try await JumbleAPI.shared.login(
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
            try await JumbleAPI.shared.loginWithGoogle(idToken: idToken)

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

    private func handleAppleLogin(result: Result<ASAuthorization, Error>) async {
        isLoading = true
        errorMessage = nil

        do {
            switch result {
            case .success(let authorization):
                if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
                    guard let appleIDToken = appleIDCredential.identityToken,
                          let idTokenString = String(data: appleIDToken, encoding: .utf8) else {
                        throw APIError.loginFailed
                    }

                    // We can also get the user's name here if needed: appleIDCredential.fullName
                    // But for now, we just pass the ID token
                    try await JumbleAPI.shared.loginWithApple(idToken: idTokenString)
                    isLoggedIn = true
                }
            case .failure(let error):
                print("Apple Sign in failed: \(error.localizedDescription)")
                // Don't show error for user cancellation
                if (error as NSError).code != ASAuthorizationError.canceled.rawValue {
                   throw error
                }
            }
        } catch {
            errorMessage = "Apple Sign-In failed: \(error.localizedDescription)"
        }

        isLoading = false
    }
}

#Preview {
    LoginView()
}
