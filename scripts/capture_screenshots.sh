#!/bin/bash

# Script to capture App Store screenshots using iOS Simulator
# This automates the process of taking screenshots on different device sizes

set -e

echo "📸 App Store Screenshot Capture Script"
echo "======================================"
echo ""

# Create output directory
SCREENSHOT_DIR="./AppStoreScreenshots"
mkdir -p "$SCREENSHOT_DIR"

# Device configurations
# Format: "Device Name|Screenshot Folder"
DEVICES=(
    "iPhone 15 Pro Max|6.7-inch"
    "iPhone 11 Pro Max|6.5-inch"
    "iPhone 8 Plus|5.5-inch"
)

echo "Available simulators:"
xcrun simctl list devices available | grep iPhone

echo ""
echo "This script will help you capture screenshots."
echo "Screenshots will be saved to: $SCREENSHOT_DIR"
echo ""

# Function to wait for user input
wait_for_screenshot() {
    local device_name=$1
    local screen_name=$2
    local output_dir=$3

    echo ""
    echo "📱 Device: $device_name"
    echo "🖼️  Screen: $screen_name"
    echo ""
    echo "Instructions:"
    echo "1. Navigate to the '$screen_name' screen in the simulator"
    echo "2. Press ENTER when ready to capture"
    echo "3. The screenshot will be saved automatically"
    echo ""
    read -p "Press ENTER when ready to capture '$screen_name'..."

    # Capture screenshot
    output_file="$output_dir/${screen_name// /_}.png"
    xcrun simctl io booted screenshot "$output_file"

    if [ -f "$output_file" ]; then
        echo "✅ Screenshot saved: $output_file"

        # Get image dimensions
        if command -v sips &> /dev/null; then
            dimensions=$(sips -g pixelWidth -g pixelHeight "$output_file" | grep -E "pixelWidth|pixelHeight" | awk '{print $2}' | paste -sd "x" -)
            echo "   Dimensions: $dimensions"
        fi
    else
        echo "❌ Failed to capture screenshot"
    fi
}

# Screens to capture
SCREENS=(
    "01_Home"
    "02_Create_Game"
    "03_Game_In_Progress"
    "04_Leaderboard"
    "05_Profile_Stats"
    "06_Public_Games"
)

echo "Recommended screenshots to capture:"
for i in "${!SCREENS[@]}"; do
    screen="${SCREENS[$i]}"
    screen_display="${screen#*_}"  # Remove number prefix
    screen_display="${screen_display//_/ }"  # Replace underscores with spaces
    echo "  $((i+1)). $screen_display"
done
echo ""

# Ask user which device to use
echo "Select device for screenshot capture:"
for i in "${!DEVICES[@]}"; do
    device="${DEVICES[$i]}"
    device_name="${device%%|*}"
    echo "  $((i+1)). $device_name"
done
echo ""
read -p "Enter device number (1-${#DEVICES[@]}): " device_choice

# Validate choice
if ! [[ "$device_choice" =~ ^[0-9]+$ ]] || [ "$device_choice" -lt 1 ] || [ "$device_choice" -gt "${#DEVICES[@]}" ]; then
    echo "❌ Invalid choice"
    exit 1
fi

# Get selected device
selected_device="${DEVICES[$((device_choice-1))]}"
device_name="${selected_device%%|*}"
folder_name="${selected_device##*|}"

echo ""
echo "Selected: $device_name"
echo ""

# Create device-specific output directory
output_dir="$SCREENSHOT_DIR/$folder_name"
mkdir -p "$output_dir"

# Check if simulator is running
if ! xcrun simctl list devices | grep -q "Booted"; then
    echo "⚠️  No simulator is currently running!"
    echo "Please start the app in Xcode on: $device_name"
    echo "Then run this script again."
    exit 1
fi

echo "📸 Starting screenshot capture for $device_name"
echo "Screenshots will be saved to: $output_dir"
echo ""

# Capture each screen
for screen in "${SCREENS[@]}"; do
    screen_display="${screen#*_}"
    screen_display="${screen_display//_/ }"
    wait_for_screenshot "$device_name" "$screen_display" "$output_dir"
done

echo ""
echo "✅ Screenshot capture complete!"
echo "📁 Screenshots saved to: $output_dir"
echo ""
echo "Next steps:"
echo "1. Review screenshots in $output_dir"
echo "2. Run this script again for other device sizes"
echo "3. Use these screenshots when setting up App Store Connect"
