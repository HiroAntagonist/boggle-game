//
// ABOUTME: Root view of the application, displays the login screen.
// ABOUTME: Entry point for user authentication before accessing the game.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        LoginView()
    }
}

#Preview {
    ContentView()
}

// MARK: - Nebula Theme Colors
extension Color {
    // Deep space background
    static let nebulaBackground = Color(red: 0.05, green: 0.02, blue: 0.15) // #0D0526
    
    // Surface for cards/tiles
    static let nebulaSurface = Color(red: 0.15, green: 0.10, blue: 0.30) // #26194D
    
    // Primary action/highlight
    static let nebulaPrimary = Color(red: 0.54, green: 0.17, blue: 0.89) // #8A2BE2 (BlueViolet)
    
    // Secondary accent (Cyan)
    static let nebulaAccent = Color(red: 0.20, green: 0.90, blue: 1.0) // Cyan-ish
    
    // Success/Error
    static let nebulaSuccess = Color(red: 0.20, green: 0.90, blue: 0.40)
    static let nebulaError = Color(red: 1.0, green: 0.30, blue: 0.30)
    
    // Text colors
    static let nebulaTextPrimary = Color.white
    static let nebulaTextSecondary = Color.white.opacity(0.7)
}

// MARK: - View Modifiers
struct ComputedGlowModifier: ViewModifier {
    var color: Color
    var radius: CGFloat
    
    func body(content: Content) -> some View {
        content
            .shadow(color: color.opacity(0.5), radius: radius, x: 0, y: 0)
            .shadow(color: color.opacity(0.3), radius: radius * 0.6, x: 0, y: 0)
    }
}

struct NebulaBackgroundModifier: ViewModifier {
    func body(content: Content) -> some View {
        ZStack {
            // Base background
            Color.nebulaBackground.ignoresSafeArea()
            
            // Ambient gradient orbs
            GeometryReader { proxy in
                ZStack {
                    Circle()
                        .fill(Color.nebulaPrimary.opacity(0.15))
                        .blur(radius: 80)
                        .frame(width: 300, height: 300)
                        .position(x: proxy.size.width * 0.8, y: proxy.size.height * 0.1)
                    
                    Circle()
                        .fill(Color.nebulaAccent.opacity(0.1))
                        .blur(radius: 60)
                        .frame(width: 200, height: 200)
                        .position(x: proxy.size.width * 0.1, y: proxy.size.height * 0.9)
                }
            }
            .ignoresSafeArea()
            
            // Content
            content
        }
    }
}

// MARK: - Extensions
extension View {
    func nebulaGlow(color: Color = .nebulaAccent, radius: CGFloat = 10) -> some View {
        self.modifier(ComputedGlowModifier(color: color, radius: radius))
    }
    
    func withNebulaBackground() -> some View {
        self.modifier(NebulaBackgroundModifier())
    }
    
    func nebulaButtonStyle(color: Color = .nebulaPrimary) -> some View {
        self
            .font(.headline)
            .fontWeight(.bold)
            .foregroundStyle(.white)
            .padding(.vertical, 12)
            .padding(.horizontal, 24)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(color)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.white.opacity(0.2), lineWidth: 1)
                    )
            )
            .nebulaGlow(color: color, radius: 5)
    }
}
