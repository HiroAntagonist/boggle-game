//
// ABOUTME: Profile editing view for updating user's gamer tag.
// ABOUTME: Provides a form to set or change the unique gamer tag used in public games.
//

import SwiftUI
import OpenAPIClient

struct ProfileEditView: View {
    @Environment(\.dismiss) var dismiss
    let currentGamerTag: String?
    let onSave: (UserResponse) -> Void

    @State private var gamerTag: String
    @State private var isSaving = false
    @State private var errorMessage: String?

    init(currentGamerTag: String?, onSave: @escaping (UserResponse) -> Void) {
        self.currentGamerTag = currentGamerTag
        self.onSave = onSave
        _gamerTag = State(initialValue: currentGamerTag ?? "")
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 25) {
                Spacer()
                    .frame(height: 20)

                Text("Edit Profile")
                    .font(.system(size: 32, weight: .black, design: .rounded))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.nebulaAccent, .nebulaPrimary],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .shadow(color: .nebulaPrimary.opacity(0.5), radius: 10, x: 0, y: 5)

                // Gamer tag input card
                VStack(alignment: .leading, spacing: 15) {
                    Text("Gamer Tag")
                        .font(.headline)
                        .foregroundStyle(.white)

                    TextField("Enter your gamer tag", text: $gamerTag)
                        .textFieldStyle(.plain)
                        .font(.system(size: 20, weight: .semibold))
                        .padding()
                        .background(Color.nebulaSurface.opacity(0.6))
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.nebulaAccent.opacity(0.5), lineWidth: 1)
                        )
                        .foregroundStyle(.white)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()

                    VStack(alignment: .leading, spacing: 6) {
                        Text("Your unique username for public games and leaderboards")
                            .font(.caption)
                            .foregroundStyle(Color.nebulaTextSecondary)

                        Text("3-20 characters, letters, numbers, and underscores only")
                            .font(.caption2)
                            .foregroundStyle(Color.nebulaTextSecondary.opacity(0.7))
                    }
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(Color.nebulaSurface.opacity(0.5))
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(Color.white.opacity(0.1), lineWidth: 1)
                        )
                )

                if let error = errorMessage {
                    Text(error)
                        .foregroundStyle(Color.nebulaError)
                        .font(.caption)
                        .padding(10)
                        .background(Color.nebulaError.opacity(0.1))
                        .cornerRadius(8)
                }

                Spacer()

                // Action buttons
                VStack(spacing: 12) {
                    Button {
                        saveProfile()
                    } label: {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                            Text("Save")
                        }
                        .frame(maxWidth: .infinity)
                    }
                    .nebulaButtonStyle(color: .nebulaPrimary)
                    .disabled(isSaving || gamerTag.isEmpty)

                    Button {
                        dismiss()
                    } label: {
                        Text("Cancel")
                            .foregroundStyle(Color.nebulaTextSecondary)
                    }
                    .disabled(isSaving)
                }
                .padding(.bottom, 20)
            }
            .padding()
            .withNebulaBackground()
            .overlay {
                if isSaving {
                    ZStack {
                        Color.black.opacity(0.5)
                            .ignoresSafeArea()

                        VStack(spacing: 15) {
                            ProgressView()
                                .tint(.nebulaAccent)
                                .scaleEffect(1.5)

                            Text("Saving...")
                                .foregroundStyle(.white)
                        }
                        .padding(30)
                        .background(
                            RoundedRectangle(cornerRadius: 16)
                                .fill(Color.nebulaSurface)
                        )
                    }
                }
            }
        }
    }

    private func saveProfile() {
        Task {
            isSaving = true
            errorMessage = nil

            do {
                let updatedUser = try await JumbleAPI.shared.updateProfile(
                    gamerTag: gamerTag.isEmpty ? nil : gamerTag
                )

                onSave(updatedUser)
                dismiss()
            } catch {
                errorMessage = error.localizedDescription
                isSaving = false
            }
        }
    }
}

#Preview {
    ProfileEditView(currentGamerTag: "player123") { _ in }
}
