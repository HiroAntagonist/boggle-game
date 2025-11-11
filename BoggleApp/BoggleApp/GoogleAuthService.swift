//
// ABOUTME: Service for handling Google Sign-In authentication flow.
// ABOUTME: Manages Google OAuth, retrieves ID tokens, and communicates with backend.
//

import Foundation
import GoogleSignIn

class GoogleAuthService {
    static let shared = GoogleAuthService()

    private init() {}

    /// Sign in with Google and return the ID token
    func signIn() async throws -> String {
        guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
              let rootViewController = windowScene.windows.first?.rootViewController else {
            throw GoogleAuthError.noViewController
        }

        let config = GIDConfiguration(clientID: GoogleSignInConfig.clientID)
        GIDSignIn.sharedInstance.configuration = config

        let result = try await GIDSignIn.sharedInstance.signIn(withPresenting: rootViewController)

        guard let idToken = result.user.idToken?.tokenString else {
            throw GoogleAuthError.noIDToken
        }

        return idToken
    }

    /// Sign out from Google
    func signOut() {
        GIDSignIn.sharedInstance.signOut()
    }
}

enum GoogleAuthError: Error, LocalizedError {
    case noViewController
    case noIDToken
    case signInFailed

    var errorDescription: String? {
        switch self {
        case .noViewController:
            return "Could not find view controller for Google Sign-In"
        case .noIDToken:
            return "Failed to get ID token from Google"
        case .signInFailed:
            return "Google Sign-In failed"
        }
    }
}
