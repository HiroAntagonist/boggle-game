# TestFlight Distribution Guide for Clauddle

Complete guide for distributing your Boggle iOS app (Clauddle) to friends and family via TestFlight.

**Last Updated**: November 12, 2025

---

## Overview

**App Details**:
- **App Name**: Clauddle
- **Bundle ID**: `com.drishtilabs.Clauddle`
- **Version**: 1.0 (Build 1)
- **Xcode Project**: `/Users/ar/dev/boggle/BoggleApp/BoggleApp.xcodeproj`

**What is TestFlight?**
- Apple's official beta testing platform
- Allows up to 100 external testers
- No App Store review required for beta testing
- Testers install via simple link or email invite
- Perfect for sharing with non-technical users

---

## Prerequisites

### 1. Apple Developer Account ($99/year)
- Status: ⏳ **Pending** (can take up to 48 hours)
- Sign up at: [developer.apple.com](https://developer.apple.com)
- Once approved, you'll receive email confirmation

### 2. Xcode (Already Installed ✅)
- Installed at: `/Applications/Xcode.app`
- Make sure you're signed in with your Apple ID

### 3. Code Signing (Already Configured ✅)
- Your app uses automatic code signing
- No manual certificate management needed

---

## Step-by-Step Instructions

### Step 1: Sign into Xcode with Developer Account

**When to do this**: After your Apple Developer membership is approved

1. Open **Xcode**
2. Go to **Xcode → Settings → Accounts** (or Xcode → Preferences → Accounts)
3. Verify your Apple ID is listed
   - If not listed, click **"+"** and sign in
4. Select your account and verify **"Role"** shows **"Agent"** or **"Admin"**
5. Click **"Download Manual Profiles"** to sync certificates

---

### Step 2: Create App Store Connect Listing

**When to do this**: One-time setup before first upload

1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. Sign in with your Apple ID
3. Click **"My Apps"** → **"+"** (plus icon) → **"New App"**
4. Fill in the form:
   - **Platforms**: ✅ iOS
   - **Name**: `Clauddle` (or your preferred public name)
   - **Primary Language**: English
   - **Bundle ID**: Select `com.drishtilabs.Clauddle` from dropdown
     - ⚠️ If bundle ID doesn't appear, wait a few hours after developer account approval
   - **SKU**: `clauddle-2025` (any unique identifier)
   - **User Access**: Full Access
5. Click **"Create"**

---

### Step 3: Archive Your App

**When to do this**: Every time you want to upload a new build

1. Open Xcode project: `/Users/ar/dev/boggle/BoggleApp/BoggleApp.xcodeproj`
2. In the top toolbar, select build destination:
   - Click the device dropdown (left of Run button)
   - Select **"Any iOS Device (arm64)"**
   - ⚠️ Must select "Any iOS Device", NOT a simulator
3. Go to **Product → Archive**
   - This compiles your app for distribution
   - Takes 1-2 minutes
   - If errors occur, see "Troubleshooting" section below
4. When complete, the **Organizer** window opens automatically
   - Shows all your archived builds

---

### Step 4: Upload to App Store Connect

**When to do this**: After archiving (continues from Step 3)

1. In the **Organizer** window:
   - Your latest archive should be selected
   - Shows: "Clauddle 1.0 (1)" with today's date
2. Click **"Distribute App"** button
3. Select distribution method: **"App Store Connect"**
4. Select destination: **"Upload"** (not Export)
5. Configure distribution options (leave defaults checked):
   - ✅ **App Thinning**: None
   - ✅ **Rebuild from Bitcode**: YES (if available)
   - ✅ **Strip Swift symbols**: YES
   - ✅ **Upload your app's symbols**: YES
   - ✅ **Manage Version and Build Number**: YES
6. Select signing option: **"Automatically manage signing"**
   - Xcode will handle certificates and profiles
7. Review app summary and click **"Upload"**
8. Wait 2-5 minutes for upload to complete
   - Progress bar shows upload status
   - Success message: "Upload Successful"

---

### Step 5: Wait for Build Processing

**When to do this**: After successful upload

1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. Select your **Clauddle** app
3. Click **"TestFlight"** tab (top navigation)
4. Wait for your build to appear
   - **Processing**: 5-10 minutes (Apple is processing your upload)
   - **Waiting for Review**: Compliance review (only for first build)
   - **Ready to Submit**: You need to complete compliance questions
   - **Ready to Test**: Build is ready for testers!

---

### Step 6: Complete Export Compliance (One-time)

**When to do this**: When build status shows "Ready to Submit"

1. In TestFlight tab, click on your build version
2. Click **"Provide Export Compliance Information"**
3. Answer the questions:
   - **"Is your app designed to use cryptography or does it contain or incorporate cryptography?"**
     - Answer: **NO** (standard iOS encryption doesn't count)
     - Unless you added custom encryption beyond Google OAuth
4. Click **"Start Internal Testing"**
5. Build status changes to **"Ready to Test"**

---

### Step 7: Add Testers

**When to do this**: After build is "Ready to Test"

You have two options:

#### Option A: Internal Testing (Faster, Private)

**Best for**: Close friends and family

1. In TestFlight tab, click **"Internal Testing"** (left sidebar)
2. Click **"+"** → **"Create Group"**
3. Name your group: `Friends & Family`
4. Add testers by email:
   - Click **"+"** next to Testers
   - Enter email addresses (must have Apple ID)
   - Click **"Add"**
5. Enable automatic builds:
   - Check **"Enable Automatic Distribution"**
   - New builds auto-notify testers
6. Click **"Add Build"** and select your build

**Pros**:
- No review delay
- Up to 100 internal testers
- Instant access

**Cons**:
- Must manually add each email
- Testers must have Apple ID

---

#### Option B: External Testing (Public Link)

**Best for**: Anyone, easier for non-technical users

1. In TestFlight tab, click **"External Testing"** (left sidebar)
2. Click **"+"** → **"Create Group"**
3. Name your group: `Public Beta`
4. Add your build:
   - Click **"Add Build"**
   - Select your version
   - Fill in **"What to Test"** (e.g., "First beta version of Clauddle Boggle game")
5. Enable public link:
   - Check **"Enable Public Link"**
   - Click **"Enable"**
   - Copy the public link (looks like: `https://testflight.apple.com/join/XXXXXXXX`)
6. Submit for review (only first time):
   - Click **"Submit for Review"**
   - Usually approved within 24 hours

**Pros**:
- Anyone can install via link
- No email collection needed
- Up to 10,000 external testers

**Cons**:
- First build requires Apple review (24-48 hours)
- Subsequent builds auto-approved if no major changes

---

### Step 8: Share with Testers

**When to do this**: After testers are added

#### For Internal Testers:
Testers receive email invite automatically. Send them these instructions:

```
Hi! I'd love for you to test my Boggle game (Clauddle).

1. Check your email for TestFlight invite
2. Install "TestFlight" app from App Store (if you don't have it)
3. Open the invite email on your iPhone/iPad
4. Tap "View in TestFlight"
5. Tap "Install"
6. Open Clauddle and start playing!

Let me know if you find any bugs or have feedback!
```

#### For External Testers (Public Link):
Send them this message with your public link:

```
Hi! I'd love for you to test my Boggle game (Clauddle).

1. Install "TestFlight" app from App Store: https://apps.apple.com/app/testflight/id899247664
2. Click this link on your iPhone/iPad: [YOUR_PUBLIC_LINK_HERE]
3. Tap "Install" in TestFlight
4. Open Clauddle and start playing!

Let me know what you think!
```

---

## Updating Your App

**When you fix bugs or add features:**

### Step 1: Increment Build Number

1. Open Xcode project
2. Select project navigator (top left)
3. Select **BoggleApp** target
4. Go to **General** tab
5. Update version numbers:
   - **Version**: Keep as `1.0` (for minor updates)
   - **Build**: Increment (1 → 2 → 3, etc.)
   - For major updates, change Version (1.0 → 1.1 → 2.0)

### Step 2: Archive and Upload (Same as Steps 3-4)

1. **Product → Archive**
2. **Distribute → Upload to App Store Connect**

### Step 3: Notify Testers (Automatic)

- If you enabled **"Enable Automatic Distribution"**, testers get notified automatically
- TestFlight shows **"Update Available"** in app
- Testers tap **"Update"** to install new version
- Processing takes 5-10 minutes after upload

---

## Troubleshooting

### Archive Button is Grayed Out

**Problem**: Can't click "Product → Archive"

**Solution**:
- Make sure you selected **"Any iOS Device"** in build destination
- NOT a simulator (e.g., "iPhone 15 Pro")
- NOT a physical device (e.g., "Amritansh's iPhone")

---

### Build Failed: Signing Error

**Problem**: "No signing certificate found" or "Provisioning profile error"

**Solution 1**: Refresh signing
1. Select project in Xcode
2. Go to **Signing & Capabilities** tab
3. Uncheck then re-check **"Automatically manage signing"**
4. Wait for Xcode to download profiles

**Solution 2**: Check developer account
1. **Xcode → Settings → Accounts**
2. Select your account
3. Click **"Download Manual Profiles"**
4. Try archiving again

---

### Bundle ID Not Available in App Store Connect

**Problem**: Can't find `com.drishtilabs.Clauddle` when creating app

**Solution**:
- Wait 2-4 hours after developer account is approved
- Bundle IDs sync automatically but may take time
- Alternatively, register bundle ID manually:
  1. Go to [Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources)
  2. Click **Identifiers** → **"+"**
  3. Select **App IDs** → Continue
  4. Enter Bundle ID: `com.drishtilabs.Clauddle`
  5. Click **Register**

---

### Build Stuck in "Processing"

**Problem**: Build shows "Processing" for more than 30 minutes

**Solution**:
- This is normal for first upload (can take up to 1 hour)
- Refresh the page every 10 minutes
- If still stuck after 2 hours, contact Apple Support

---

### Export Compliance Confusion

**Problem**: Not sure how to answer encryption questions

**Answer these**:
- **Q: "Is your app designed to use cryptography?"**
  - A: **NO** (Google OAuth uses standard iOS encryption)
- **Q: "Does your app contain encryption?"**
  - A: **NO** (unless you added custom encryption)

---

## Quick Reference Commands

### Check Current Version and Build Number
```bash
cd /Users/ar/dev/boggle/BoggleApp
xcodebuild -showBuildSettings -project BoggleApp.xcodeproj 2>/dev/null | grep -E "MARKETING_VERSION|CURRENT_PROJECT_VERSION"
```

Expected output:
```
MARKETING_VERSION = 1.0
CURRENT_PROJECT_VERSION = 1
```

### Build from Command Line (Optional)
```bash
cd /Users/ar/dev/boggle/BoggleApp
xcodebuild -project BoggleApp.xcodeproj -scheme BoggleApp -configuration Release archive -archivePath ./build/Clauddle.xcarchive
```

---

## Important Links

- **App Store Connect**: https://appstoreconnect.apple.com
- **Apple Developer Portal**: https://developer.apple.com/account
- **TestFlight Documentation**: https://developer.apple.com/testflight
- **Certificates & Profiles**: https://developer.apple.com/account/resources

---

## Timeline Summary

| Task | Time Required |
|------|---------------|
| Developer account approval | 24-48 hours |
| Create App Store Connect listing | 5 minutes |
| First archive and upload | 10-15 minutes |
| Build processing | 10-30 minutes |
| Export compliance (one-time) | 2 minutes |
| External testing review (first build) | 24-48 hours |
| Add internal testers | 5 minutes |
| Testers can install | Immediate |
| **Total for first build** | **3-5 days** |
| **Subsequent updates** | **20-30 minutes** |

---

## Next Steps

1. ⏳ **Wait for Apple Developer membership approval** (up to 48 hours)
2. ✅ **Follow Step 1**: Sign into Xcode with approved account
3. ✅ **Follow Step 2**: Create App Store Connect listing
4. ✅ **Follow Steps 3-8**: Archive, upload, and distribute

---

## Need Help?

If you run into issues, check:
1. This troubleshooting section
2. Apple's [TestFlight Documentation](https://developer.apple.com/testflight)
3. Ask me for help with specific errors

Good luck with your beta launch! 🚀
