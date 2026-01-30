# iOS App Build Instructions

## ⚠️ Important: macOS Required

iOS apps can only be built on macOS with Xcode installed. This project has been prepared for iOS deployment, but the final build steps must be completed on a Mac.

## Current Status

✅ **Completed on Linux:**
- Capacitor project initialized
- Mobile-optimized HTML created
- Configuration files set up
- All dependencies installed
- Project structure prepared

⏳ **Requires macOS:**
- Adding iOS platform
- Opening in Xcode
- Building and testing
- App Store submission

## Transfer to macOS

### Option 1: Direct Transfer
```bash
# On Linux machine, create archive
tar -czf dashboard-ios-ready.tar.gz OpenWebUI/

# Transfer to Mac (via USB, network, cloud storage)
# Then on Mac:
tar -xzf dashboard-ios-ready.tar.gz
cd OpenWebUI
```

### Option 2: Git Clone
```bash
# If you have this pushed to Git
# On Mac:
git clone https://github.com/zaeaep/dashboard.git
cd dashboard
```

### Option 3: Cloud Sync
- Use Dropbox, Google Drive, iCloud
- Sync the OpenWebUI folder
- Access on Mac

## Setup on macOS

### 1. Install Prerequisites

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node

# Install CocoaPods (iOS dependency manager)
sudo gem install cocoapods

# Install Xcode from App Store (required!)
# Open Xcode at least once to accept license
```

### 2. Install Project Dependencies

```bash
cd /path/to/OpenWebUI

# Install npm packages
npm install

# Add iOS platform
npx cap add ios

# Sync web files to iOS
npx cap sync ios
```

### 3. Open in Xcode

```bash
# Open iOS project in Xcode
npx cap open ios

# Or manually:
open ios/App/App.xcworkspace
```

### 4. Configure iOS Project in Xcode

1. **Select your development team:**
   - Click on "App" in project navigator
   - Select "App" target
   - Go to "Signing & Capabilities"
   - Select your Apple ID team

2. **Configure Bundle Identifier:**
   - Change `com.dashboard.personal` to your own
   - Format: `com.yourname.dashboard`

3. **Update Display Name:**
   - General tab → Display Name: "Dashboard"

4. **Set Deployment Target:**
   - Minimum: iOS 13.0
   - Recommended: iOS 15.0+

### 5. Backend Configuration

#### For Testing (Local Network):

1. Find your Mac's IP address:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. Update `mobile/index.html`:
   ```javascript
   const API_BASE_URL = 'http://YOUR_MAC_IP:5000';
   ```

3. Start Flask server on Mac:
   ```bash
   python run.py
   ```

4. Ensure iPhone and Mac are on same WiFi network

#### For Production (Cloud):

1. Deploy Flask backend to cloud (Railway, Render, etc.)

2. Update `mobile/index.html`:
   ```javascript
   const API_BASE_URL = 'https://your-app.railway.app';
   ```

3. Ensure CORS is configured in Flask

### 6. Build and Run

#### In iOS Simulator:

1. Select a simulator from device menu (e.g., "iPhone 14")
2. Click ▶️ Play button or press Cmd+R
3. App will launch in simulator

#### On Physical iPhone:

1. Connect iPhone via USB
2. Trust computer on iPhone (first time)
3. Select your iPhone from device menu
4. Click ▶️ Play button
5. On iPhone: Settings → General → Device Management
6. Trust your developer certificate

### 7. Testing Checklist

- [ ] App launches successfully
- [ ] Dashboard loads data from backend
- [ ] All widgets display correctly
- [ ] Touch interactions work
- [ ] Scrolling is smooth
- [ ] Settings button works
- [ ] Pull to refresh works
- [ ] Network errors handled gracefully
- [ ] Safe areas respected (notch, home indicator)
- [ ] Works in light and dark mode

## Troubleshooting on macOS

### CocoaPods Issues
```bash
cd ios/App
pod repo update
pod install
cd ../..
```

### Certificate Issues
- Ensure you're signed into Xcode with Apple ID
- Xcode → Preferences → Accounts → Add Account
- Free Apple ID works for development/testing

### Network Connection Failed
- Check Flask server is running
- Verify IP address is correct
- Check firewall isn't blocking port 5000
- iPhone and Mac must be on same network

### App Won't Install on Device
- Check bundle identifier is unique
- Ensure device is trusted
- Try cleaning build: Product → Clean Build Folder
- Restart Xcode and iPhone

## App Store Submission (Optional)

### Requirements:
1. **Apple Developer Account ($99/year)**
   - Sign up at https://developer.apple.com

2. **App Store Assets:**
   - App Icon (1024x1024)
   - Screenshots for all device sizes
   - App description and keywords
   - Privacy policy URL
   - Support URL

3. **Preparation:**
   ```bash
   # Create archive
   # In Xcode: Product → Archive
   
   # Upload to App Store Connect
   # Window → Organizer → Archives → Upload
   ```

4. **Submission Process:**
   - Create app in App Store Connect
   - Fill in metadata
   - Submit for review
   - Wait 1-3 days for approval

## Alternative: TestFlight Beta

Before App Store submission, test with TestFlight:

1. Upload build to App Store Connect
2. Add app to TestFlight
3. Invite testers (up to 10,000 external testers)
4. Testers install via TestFlight app
5. Collect feedback and iterate

## Cloud Backend Deployment

### Option 1: Railway.app (Easiest)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up
```

### Option 2: Render.com

1. Create account at render.com
2. Connect GitHub repository
3. Create new "Web Service"
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn -w 4 -b 0.0.0.0:$PORT "app:create_app()"`
6. Add environment variables from .env
7. Deploy

### Option 3: DigitalOcean App Platform

1. Create account
2. Connect GitHub
3. Select Python app
4. Configure environment variables
5. Deploy

## Cost Breakdown

### Development (Free):
- ✅ Xcode (free)
- ✅ iOS Simulator (free)
- ✅ Testing on personal device (free)
- ✅ TestFlight beta testing (free)

### Optional Costs:
- 💰 Apple Developer Account: $99/year (for App Store)
- 💰 Backend hosting: $0-5/month (Railway, Render free tiers)
- 💰 Custom domain: $10/year (optional)

## Next Steps

1. ✅ Transfer project to Mac
2. ✅ Install Xcode and prerequisites
3. ✅ Run `npm install` and `npx cap add ios`
4. ✅ Open in Xcode and configure signing
5. ✅ Start Flask backend
6. ✅ Build and run in simulator
7. ✅ Test all features
8. ✅ Test on physical iPhone
9. ⏳ Deploy backend to cloud (optional)
10. ⏳ Submit to App Store (optional)

## Support

If you encounter issues:
1. Check Capacitor docs: https://capacitorjs.com/docs/ios
2. Check Xcode console for errors
3. Verify Flask server is accessible
4. Test API endpoints in browser first

## Files to Review on Mac

- `mobile/index.html` - Main app HTML
- `capacitor.config.json` - Capacitor configuration
- `ios/App/App/Info.plist` - iOS app settings (after adding iOS platform)
- `package.json` - Dependencies

---

**Status**: Ready for macOS development
**Created**: January 30, 2026
**Platform**: Prepared on Linux, requires macOS for final build
