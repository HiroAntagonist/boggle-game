#!/usr/bin/env swift

import AppKit
import Foundation

// Create a 1024x1024 app icon for Jumble
func generateIcon() {
    let size = CGSize(width: 1024, height: 1024)
    let image = NSImage(size: size)

    image.lockFocus()

    guard let context = NSGraphicsContext.current?.cgContext else {
        print("Failed to get graphics context")
        return
    }

    // Background - purple gradient
    let purple1 = NSColor(red: 0.545, green: 0.361, blue: 0.965, alpha: 1.0) // #8B5CF6
    let purple2 = NSColor(red: 0.459, green: 0.271, blue: 0.875, alpha: 1.0) // Darker purple

    let gradient = NSGradient(colors: [purple1, purple2])
    gradient?.draw(in: NSRect(origin: .zero, size: size), angle: 135)

    // Draw 4 letter tiles in a 2x2 grid pattern
    let tileSize: CGFloat = 200
    let spacing: CGFloat = 40
    let totalWidth = (tileSize * 2) + spacing
    let startX = (size.width - totalWidth) / 2
    let startY = (size.height - totalWidth) / 2

    let letters = ["J", "M", "B", "L"]
    let positions = [
        (0, 0), (1, 0),  // Top row
        (0, 1), (1, 1)   // Bottom row
    ]

    for (index, pos) in positions.enumerated() {
        let x = startX + CGFloat(pos.0) * (tileSize + spacing)
        let y = startY + CGFloat(pos.1) * (tileSize + spacing)

        // Draw tile background (lighter purple/white)
        let tileRect = NSRect(x: x, y: y, width: tileSize, height: tileSize)
        let tilePath = NSBezierPath(roundedRect: tileRect, xRadius: 20, yRadius: 20)

        NSColor.white.withAlphaComponent(0.95).setFill()
        tilePath.fill()

        // Add subtle shadow/border
        NSColor.white.withAlphaComponent(0.3).setStroke()
        tilePath.lineWidth = 4
        tilePath.stroke()

        // Draw letter
        let letter = letters[index]
        let paragraphStyle = NSMutableParagraphStyle()
        paragraphStyle.alignment = .center

        let attrs: [NSAttributedString.Key: Any] = [
            .font: NSFont.systemFont(ofSize: 120, weight: .bold),
            .foregroundColor: NSColor(red: 0.545, green: 0.361, blue: 0.965, alpha: 1.0),
            .paragraphStyle: paragraphStyle
        ]

        let textRect = NSRect(x: x, y: y + (tileSize - 120) / 2 - 10, width: tileSize, height: 120)
        letter.draw(in: textRect, withAttributes: attrs)
    }

    image.unlockFocus()

    // Save as PNG
    guard let tiffData = image.tiffRepresentation,
          let bitmapImage = NSBitmapImageRep(data: tiffData),
          let pngData = bitmapImage.representation(using: .png, properties: [:]) else {
        print("Failed to create PNG data")
        return
    }

    let outputPath = "/Users/ar/dev/boggle/AppIcon.png"
    do {
        try pngData.write(to: URL(fileURLWithPath: outputPath))
        print("✅ Icon generated successfully at: \(outputPath)")
        print("📱 Size: 1024x1024 (ready for App Store)")
    } catch {
        print("❌ Failed to save icon: \(error)")
    }
}

generateIcon()
