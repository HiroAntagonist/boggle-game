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
            Form {
                Section {
                    TextField("Gamer Tag", text: $gamerTag)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                } header: {
                    Text("Gamer Tag")
                } footer: {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Your unique username for public games and leaderboards")
                        Text("3-20 characters, letters, numbers, and underscores only")
                            .font(.caption2)
                    }
                }

                if let error = errorMessage {
                    Section {
                        Text(error)
                            .foregroundStyle(.red)
                            .font(.caption)
                    }
                }
            }
            .navigationTitle("Edit Profile")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                    .disabled(isSaving)
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        saveProfile()
                    }
                    .disabled(isSaving || gamerTag.isEmpty)
                }
            }
            .overlay {
                if isSaving {
                    ZStack {
                        Color.black.opacity(0.4)
                            .ignoresSafeArea()

                        ProgressView()
                            .scaleEffect(1.5)
                            .padding()
                            .background(Color(.systemBackground))
                            .cornerRadius(10)
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
                let updatedUser = try await BoggleAPI.shared.updateProfile(
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
