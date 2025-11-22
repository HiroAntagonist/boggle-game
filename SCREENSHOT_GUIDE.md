# App Store Screenshot Guide

## Quick Start

### Option 1: Automated Script (Recommended)

1. **Run the app in Xcode** on one of these simulators:
   - iPhone 15 Pro Max (for 6.7" screenshots)
   - iPhone 11 Pro Max (for 6.5" screenshots)
   - iPhone 8 Plus (for 5.5" screenshots)

2. **Run the screenshot script**:
   ```bash
   ./scripts/capture_screenshots.sh
   ```

3. **Follow the prompts**:
   - Select device
   - Navigate to each screen
   - Press ENTER to capture
   - Screenshots saved to `AppStoreScreenshots/`

### Option 2: Manual Screenshot Capture

1. **Run app in Xcode** on desired simulator
2. **Navigate to screen** you want to capture
3. **Press Cmd + S** (or File → New Screen Shot)
4. Screenshot saves to Desktop with correct dimensions

## Required Screenshots

You need **3-10 screenshots** for each device size. Here are the recommended screens:

### 1. Home Screen
- Shows "Create Game" and "Join Game" buttons
- Clean, inviting entry point

### 2. Create Game Options
- Board size selector (4×4 or 5×5)
- Time limit options
- Public/Private toggle
- Shows customization options

### 3. Game in Progress
- Letter grid clearly visible
- Active timer counting down
- Some words already found
- Shows core gameplay

### 4. Leaderboard
- Top players with gamer tags
- Scores and win counts
- Demonstrates competition aspect

### 5. Profile & Statistics
- User stats (games played, win rate, best score)
- Shows progression tracking

### 6. Public Games List
- Available games to join
- Game details (players, board size, time limit)
- Demonstrates multiplayer aspect

## Device Sizes Required

### Priority 1: 6.7" Display (REQUIRED)
- **Simulator**: iPhone 15 Pro Max
- **Resolution**: 1290 × 2796 pixels
- **Need**: At least 3 screenshots

### Priority 2: 6.5" Display (REQUIRED)
- **Simulator**: iPhone 11 Pro Max
- **Resolution**: 1242 × 2688 pixels
- **Need**: At least 3 screenshots

### Priority 3: 5.5" Display (Optional but Recommended)
- **Simulator**: iPhone 8 Plus
- **Resolution**: 1242 × 2208 pixels
- **Need**: 3-10 screenshots

## Tips for Great Screenshots

1. **Use real data**: Create actual games, join real matches, show real leaderboard
2. **Show variety**: Mix of screens shows all features
3. **Clean state**: No errors, full battery, good WiFi in status bar
4. **Landscape OK**: Game supports rotation, you can include landscape shots
5. **Order matters**: First screenshot is most important (users see it first)

## After Capturing

1. **Review screenshots** in `AppStoreScreenshots/` folder
2. **Verify dimensions** - script shows pixel size
3. **Rename if needed** - App Store Connect accepts any names
4. **Upload to App Store Connect** when setting up listing

## Troubleshooting

**Simulator not running?**
- Launch Xcode → Run app on desired device
- Then run the script

**Wrong dimensions?**
- Make sure you selected the correct simulator model
- Use Cmd + 1 in simulator for 100% scale
- Check: sips -g pixelWidth -g pixelHeight screenshot.png

**Screenshot looks blurry?**
- Simulator should be at 100% scale (Cmd + 1)
- Don't use "Fit Screen" mode

**Need different orientation?**
- Rotate simulator: Cmd + Left/Right Arrow
- Or Hardware → Rotate Left/Right
