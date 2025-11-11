//
// ABOUTME: Secure storage service for JWT tokens using iOS Keychain.
// ABOUTME: Provides save, load, and delete operations for authentication tokens.
//

import Foundation
import Security

class KeychainService {
    static let shared = KeychainService()

    private let service = "com.boggle.auth"
    private let account = "accessToken"

    private init() {}

    /// Save access token to Keychain
    func saveToken(_ token: String) -> Bool {
        // Delete any existing token first
        deleteToken()

        guard let tokenData = token.data(using: .utf8) else {
            print("❌ Failed to convert token to data")
            return false
        }

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: tokenData,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock
        ]

        let status = SecItemAdd(query as CFDictionary, nil)

        if status == errSecSuccess {
            print("✅ Token saved to Keychain")
            return true
        } else {
            print("❌ Failed to save token to Keychain: \(status)")
            return false
        }
    }

    /// Load access token from Keychain
    func loadToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess,
              let tokenData = result as? Data,
              let token = String(data: tokenData, encoding: .utf8) else {
            if status != errSecItemNotFound {
                print("❌ Failed to load token from Keychain: \(status)")
            }
            return nil
        }

        print("✅ Token loaded from Keychain")
        return token
    }

    /// Delete access token from Keychain
    @discardableResult
    func deleteToken() -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]

        let status = SecItemDelete(query as CFDictionary)

        if status == errSecSuccess || status == errSecItemNotFound {
            print("✅ Token deleted from Keychain")
            return true
        } else {
            print("❌ Failed to delete token from Keychain: \(status)")
            return false
        }
    }

    /// Check if a token exists in Keychain
    func hasToken() -> Bool {
        return loadToken() != nil
    }
}
