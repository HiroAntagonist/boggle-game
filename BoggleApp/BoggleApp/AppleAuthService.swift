import Foundation
import AuthenticationServices
import CryptoKit
import UIKit
import Combine

// Helper class to manage Apple Sign-In authentication
class AppleAuthService: NSObject, ObservableObject {


    // Unhashed nonce (for request)
    private var currentNonce: String?

    // Completion handler to send the ID token back to the view
    var onLoginSuccess: ((String, String?) -> Void)?
    var onLoginFailure: ((Error) -> Void)?

    // Start the Apple Sign-In flow
    func startSignIn() {
        let request = ASAuthorizationAppleIDProvider().createRequest()
        request.requestedScopes = [.fullName, .email]

        // Generate nonce for security (prevent replay attacks)
        let nonce = randomNonceString()
        currentNonce = nonce
        request.nonce = sha256(nonce)

        let controller = ASAuthorizationController(authorizationRequests: [request])
        controller.delegate = self
        controller.presentationContextProvider = self
        controller.performRequests()
    }

    // MARK: - Helper Functions

    // Adapted from Apple's documentation
    private func randomNonceString(length: Int = 32) -> String {
        precondition(length > 0)
        var randomBytes = [UInt8](repeating: 0, count: length)
        let errorCode = SecRandomCopyBytes(kSecRandomDefault, randomBytes.count, &randomBytes)
        if errorCode != errSecSuccess {
            fatalError("Unable to generate nonce. SecRandomCopyBytes failed with OSStatus \(errorCode)")
        }

        let charset: [Character] = Array("0123456789ABCDEFGHIJKLMNOPQRSTUVXYZabcdefghijklmnopqrstuvwxyz-._")

        let nonce = randomBytes.map { byte in
            // Pick a random character from the set, wrapping around if needed
            charset[Int(byte) % charset.count]
        }

        return String(nonce)
    }

    // Adapted from Apple's documentation
    private func sha256(_ input: String) -> String {
        let inputData = input.data(using: .utf8)!
        let hashedData = SHA256.hash(data: inputData)
        let hashString = hashedData.compactMap {
            String(format: "%02x", $0)
        }.joined()

        return hashString
    }
}

// MARK: - ASAuthorizationControllerDelegate
extension AppleAuthService: ASAuthorizationControllerDelegate {

    func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {

            // Verify Nonce
            guard currentNonce != nil else {
                fatalError("Invalid state: A login callback was received, but no login request was sent.")
            }

            // Retrieve ID Token
            guard let appleIDToken = appleIDCredential.identityToken else {
                print("Unable to fetch identity token")
                onLoginFailure?(NSError(domain: "AppleAuth", code: -1, userInfo: [NSLocalizedDescriptionKey: "Unable to fetch identity token"]))
                return
            }

            guard let idTokenString = String(data: appleIDToken, encoding: .utf8) else {
                print("Unable to serialize token string from data: \(appleIDToken.debugDescription)")
                onLoginFailure?(NSError(domain: "AppleAuth", code: -1, userInfo: [NSLocalizedDescriptionKey: "Unable to serialize token string"]))
                return
            }

            // Success! Return ID Token
            // Note: We might also want to capture the name here if we want to send it to our backend manually
            // Apple only sends the name on the FIRST sign in, so we should grab it if available.
            // However, our backend relies primarily on the ID token.
            // If we needed to send the name, we could pass it back here.

            onLoginSuccess?(idTokenString, currentNonce)
        }
    }

    func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: Error) {
        print("Sign in with Apple failed: \(error.localizedDescription)")
        onLoginFailure?(error)
    }
}

// MARK: - ASAuthorizationControllerPresentationContextProviding
extension AppleAuthService: ASAuthorizationControllerPresentationContextProviding {
    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        // Find the active window scene
        guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
              let window = windowScene.windows.first else {
            return UIWindow()
        }
        return window
    }
}
