# 🍎 Next Steps on Your Mac

All iOS app files have been pushed to GitHub. Here's what to do on your Mac:

## 📥 1. Pull the Repository

```bash
cd ~/path/to/your/projects
git clone https://github.com/zaeaep/dashboard.git
cd dashboard

# Or if you already have it cloned:
git pull origin main
```

## 🔧 2. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install CocoaPods (if not already installed)
sudo gem install cocoapods

# Install iOS pods
cd ios/App
pod install
cd ../..
```

## 📱 3. Open in Xcode

```bash
# Open the workspace (NOT the .xcodeproj)
open ios/App/App.xcworkspace
```

## ⚙️ 4. Configure Xcode Project

1. **Select your Team**:
   - Click on "App" in the project navigator
   - Go to "Signing & Capabilities" tab
   - Select your Apple Developer Team

2. **Change Bundle Identifier** (optional but recommended):
   - In the same screen, change `io.ionic.starter` to something unique
   - Example: `com.yourname.dashboard`

3. **Select Target Device**:
   - Top toolbar: Choose your iPhone or a simulator
   - Recommended: iPhone 14 or newer simulator

## ▶️ 5. Build and Run

Two options:

### Option A: Run in Simulator (Easiest)
```bash
# From project root
npx cap run ios
```

OR click the "Play" button (▶️) in Xcode

### Option B: Run on Physical iPhone
1. Connect your iPhone via USB
2. Trust the computer on your iPhone
3. Select your iPhone as the target device in Xcode
4. Click "Play" button (▶️)
5. First time: Go to iPhone Settings → General → VPN & Device Management → Trust your developer certificate

## 🔌 6. Connect to Backend

The app needs to connect to your dashboard backend:

### Option 1: Local Network (Both devices on same WiFi)
```bash
# On Mac, find your IP address:
ifconfig | grep "inet " | grep -v 127.0.0.1

# Example output: 192.168.1.100

# Update mobile/index.html:
# Change API_BASE_URL from 'http://localhost:5000' to 'http://192.168.1.100:5000'
```

### Option 2: Ngrok Tunnel (Works anywhere)
```bash
# Install ngrok:
brew install ngrok

# Run your dashboard backend:
cd ~/dashboard
python run.py

# In another terminal, create tunnel:
ngrok http 5000

# Copy the https:// URL (e.g., https://abc123.ngrok.io)
# Update mobile/index.html API_BASE_URL to this URL
```

### Option 3: Deploy Backend (Production)
Deploy your Flask backend to:
- Heroku
- DigitalOcean
- AWS
- Google Cloud

Then update API_BASE_URL to your production URL.

## 🧪 7. Test the App

1. **Launch the app** on iPhone/simulator
2. **Check network connectivity**:
   - Open Safari on the iPhone
   - Navigate to your backend URL (e.g., http://192.168.1.100:5000)
   - Should see the dashboard

3. **Test features**:
   - Weather widget
   - Calendar events
   - Garmin data
   - AI suggestions
   - Todo list
   - Timer

## 🐛 Troubleshooting

### Build Errors
```bash
# Clean build folder
cd ios/App
xcodebuild clean
pod deintegrate
pod install
```

### Network Issues
- Check firewall on Mac (System Preferences → Security & Privacy → Firewall)
- Make sure Flask server is running with `HOST=0.0.0.0` in .env
- Test backend URL in iPhone Safari first

### Certificate Issues
- Make sure you're signed in with your Apple ID in Xcode
- Go to Xcode → Preferences → Accounts
- Download manual provisioning profiles if needed

## 📝 Important Files

- **Xcode Project**: `ios/App/App.xcworkspace` ← Open this one!
- **Mobile HTML**: `mobile/index.html`
- **Capacitor Config**: `capacitor.config.json`
- **Build Instructions**: `IOS_BUILD_INSTRUCTIONS.md`
- **Deployment Guide**: `IOS_DEPLOYMENT_PLAN.md`

## 🎨 Customize the App

### Change App Name
1. Open `ios/App/App/Info.plist`
2. Change `CFBundleDisplayName` value

### Change App Icon
1. Create 1024x1024 icon image
2. Use an online tool: https://appicon.co
3. Replace files in `ios/App/App/Assets.xcassets/AppIcon.appiconset/`

### Change Splash Screen
1. Create 2732x2732 splash image
2. Replace files in `ios/App/App/Assets.xcassets/Splash.imageset/`

## 🚀 Rebuild After Changes

```bash
# After changing mobile/index.html or other web files:
npx cap copy ios

# After changing native code or adding plugins:
npx cap sync ios

# Then rebuild in Xcode
```

## 📦 TestFlight Distribution (Optional)

Once your app is working:

1. **Archive the App**:
   - Product → Archive in Xcode
   
2. **Upload to App Store Connect**:
   - Window → Organizer → Archives
   - Click "Distribute App"
   - Choose "App Store Connect"
   
3. **Configure TestFlight**:
   - Go to https://appstoreconnect.apple.com
   - Add testers
   - Distribute beta

## ⏭️ Next Steps

1. ✅ Pull repo on Mac
2. ✅ Run `npm install`
3. ✅ Run `pod install` in ios/App
4. ✅ Open App.xcworkspace in Xcode
5. ✅ Configure signing
6. ✅ Run on simulator
7. ✅ Configure backend connection
8. ✅ Test on physical device
9. 🎉 Enjoy your iOS dashboard app!

## 📞 Need Help?

Check these files for detailed information:
- **IOS_BUILD_INSTRUCTIONS.md** - Complete build guide
- **IOS_DEPLOYMENT_PLAN.md** - Deployment strategy
- **mobile/index.html** - Mobile app code

---

**Your dashboard is now ready to become an iPhone app!** 🎉📱

Follow these steps on your Mac and you'll have the app running in minutes.
