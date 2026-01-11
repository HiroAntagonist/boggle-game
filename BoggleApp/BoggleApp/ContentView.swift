//
// ABOUTME: Root view of the application, displays the login screen.
// ABOUTME: Entry point for user authentication before accessing the game.
//

import SwiftUI

struct ContentView: View {
    @AppStorage("hasSeenOnboarding") var hasSeenOnboarding: Bool = false

    var body: some View {
        Group {
            if !hasSeenOnboarding {
                OnboardingView(isPresented: $hasSeenOnboarding)
            } else {
                LoginView()
            }
        }
    }
}

#Preview {
    ContentView()
}

// MARK: - Onboarding View
struct OnboardingView: View {
    @Binding var isPresented: Bool
    @State private var currentPage = 0
    
    let pages: [OnboardingPage] = [
        OnboardingPage(
            title: "Welcome to Jumble",
            description: "The galaxy's favorite word game. Challenge your mind and compete with others.",
            systemImage: "star.fill"
        ),
        OnboardingPage(
            title: "Connect Tiles",
            description: "Swipe to connect adjacent letters horizontally, vertically, or diagonally to form words.",
            systemImage: "hand.draw.fill"
        ),
        OnboardingPage(
            title: "Score Points",
            description: "Find as many words as possible before time runs out. Longer words earn you more points!",
            systemImage: "flag.checkered"
        ),
        OnboardingPage(
            title: "Play Together",
            description: "Create private lobbies to play with friends or join public games to compete globally.",
            systemImage: "person.3.fill"
        )
    ]
    
    var body: some View {
        ZStack {
            TabView(selection: $currentPage) {
                ForEach(0..<pages.count, id: \.self) { index in
                    OnboardingPageView(page: pages[index])
                        .tag(index)
                }
            }
            .tabViewStyle(.page(indexDisplayMode: .always))
            .indexViewStyle(.page(backgroundDisplayMode: .always))
            
            // "Next" / "Get Started" Button Overlay
            VStack {
                Spacer()
                
                Button(action: {
                    withAnimation {
                        if currentPage < pages.count - 1 {
                            currentPage += 1
                        } else {
                            // Helper to set the binding found in ContentView
                            // But usually we set AppStorage directly.
                            // Since we passed binding, let's toggle it.
                            // But wait, the previous code used AppStorage directly.
                            // Let's rely on the binding passing true to the state which updates AppStorage?
                            // No, AppStorage is the source of truth in ContentView.
                            // Let's just update the binding.
                            isPresented = true
                        }
                    }
                }) {
                    Text(currentPage < pages.count - 1 ? "Next" : "Get Started")
                        .font(.headline)
                        .fontWeight(.bold)
                        .frame(maxWidth: .infinity)
                        .padding()
                }
                .nebulaButtonStyle(color: .nebulaAccent)
                .padding(.horizontal, 40)
                .padding(.bottom, 50)
            }
        }
        .withNebulaBackground()
        .transition(.opacity)
    }
}

struct OnboardingPage {
    let title: String
    let description: String
    let systemImage: String
}

struct OnboardingPageView: View {
    let page: OnboardingPage
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            // Icon
            Image(systemName: page.systemImage)
                .font(.system(size: 80))
                .foregroundStyle(
                    LinearGradient(
                        colors: [.nebulaAccent, .nebulaPrimary],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .shadow(color: .nebulaAccent.opacity(0.5), radius: 20, x: 0, y: 0)
                .padding(40)
                .background(
                    Circle()
                        .fill(Color.nebulaSurface)
                        .overlay(
                            Circle()
                                .stroke(Color.white.opacity(0.1), lineWidth: 1)
                        )
                        .shadow(color: .black.opacity(0.3), radius: 10, x: 0, y: 5)
                )
            
            // Text Content
            VStack(spacing: 16) {
                Text(page.title)
                    .font(.system(size: 32, weight: .bold, design: .rounded))
                    .foregroundStyle(.white)
                    .multilineTextAlignment(.center)
                
                Text(page.description)
                    .font(.body)
                    .foregroundStyle(Color.nebulaTextSecondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 30)
            }
            
            Spacer()
            Spacer() // Push content up slightly to make room for button
        }
    }
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
