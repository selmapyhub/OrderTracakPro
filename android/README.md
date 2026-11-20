# OrderTrack Pro - Android Studio WebView Project 📱

This is a complete, native Android application project that wraps the **OrderTrack Pro** Django web application in a responsive, high-performance Android WebView.

---

## 🌟 Native Features Built-In

1. **Pull-to-Refresh (`SwipeRefreshLayout`)**:
   - Pull down anywhere at the top of the page to refresh the production floor dashboard.
   - Smoothly disabled when scrolling down tables or cards.

2. **Smart Back Navigation**:
   - Tapping the Android system Back button navigates back through web pages (`webView.goBack()`).
   - Double-tap back required to exit the app to prevent accidental exits on the workshop floor.

3. **Offline / Connection Error Screen**:
   - If the server is unreachable or Wi-Fi drops, a user-friendly error screen appears with a **"Retry Connection"** button.

4. **HTML5 File Upload Support**:
   - `WebChromeClient.onShowFileChooser` is pre-configured with Android's `ActivityResultLauncher` for file uploads or camera attachment.

5. **Cleartext Traffic Enabled (`network_security_config.xml`)**:
   - Android 9+ blocks unencrypted `http://` connections by default. This project has network security rules pre-configured to allow local development servers (`10.0.2.2`, `192.168.x.x`, `127.0.0.1`).

---

## 🛠️ How to Open & Run in Android Studio

### Step 1: Start your Django Server First
In your terminal, navigate to the `OrderTrackPro` root directory and start the server:
```powershell
python manage.py runserver 0.0.0.0:8000
```

### Step 2: Open the Project in Android Studio
1. Launch **Android Studio**.
2. Click **Open** (or `File` > `Open...`).
3. Select the `OrderTrackPro/android` folder.
4. Wait for Gradle sync to complete automatically.

### Step 3: Configure Server URL (if using a physical phone)
Open [`app/src/main/java/com/ordertrackpro/app/MainActivity.java`](file:///c:/Users/User/Desktop/OrderTrackPro/android/app/src/main/java/com/ordertrackpro/app/MainActivity.java):

```java
// For Android Studio Emulator:
public static final String SERVER_URL = "http://10.0.2.2:8000/";

// For Physical Android Phone (same Wi-Fi network):
// public static final String SERVER_URL = "http://192.168.1.XX:8000/";

// For Production Cloud Server:
// public static final String SERVER_URL = "https://your-production-domain.com/";
```

> **Note for Emulator**: `10.0.2.2` is the special Android Emulator alias that points to your host computer's `127.0.0.1:8000`.

### Step 4: Run the App
- Select your Emulator or connected physical device from the top device toolbar.
- Click the green **Run (▶)** button or press `Shift + F10`.

---

## 📦 How to Export a Standalone APK

1. In Android Studio, go to the top menu: **Build** &rarr; **Build Bundle(s) / APK(s)** &rarr; **Build APK(s)**.
2. Android Studio will compile the APK.
3. When finished, click **locate** in the popup notification to get the `app-debug.apk` file.
4. Transfer this `.apk` to any Android phone or tablet to install and run!
