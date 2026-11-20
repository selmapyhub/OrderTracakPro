# OrderTrack Pro 🛠️
> **Commercial Kitchen Equipment Production Tracking Web Application**  
> Built with Python (Django 5) & SQLite. Designed with modern Bootstrap 5 for desktop, workshop tablets, and bundled with a native Android Studio WebView wrapper.

---

## 📋 Features Overview

1. **Top Summary KPI Cards**:
   - **Total Orders**: All registered manufacturing jobs.
   - **Active (In Workshop Floor)**: Units actively being fabricated.
   - **On Track**: Equipment on schedule.
   - **Urgent**: High-priority jobs needing floor attention.
   - **Completed**: Quality-checked equipment ready for dispatch.
   - *Interactive*: Click any card to filter the view immediately.

2. **Search & Filter Bar**:
   - Instant search across **Customer Name**, **Equipment Model**, **Order ID** (`#101`, `#102`), and **Assigned Staff**.
   - Filter chips: **All**, **On Track**, **Urgent**, **Delayed**, **Completed**.
   - **View Toggle**: Switch between **Table View** and **Card View** (preference persists automatically).

3. **5 Production Stages & Dynamic Progress Calculation**:
   - **Stage 1: Cutting** (Blanking and CNC laser/guillotine sheet metal).
   - **Stage 2: Welding** (TIG/MIG argon welding and framework assembly).
   - **Stage 3: Glass** (Toughened display glass, sneeze guards, door seals).
   - **Stage 4: Finishing** (Buffing, satin grain polishing, insulation, electrical wiring).
   - **Stage 5: QC** (Pressure testing, thermostat calibration, quality sign-off).
   - *Automatic 0% – 100% progress formula*: Each completed stage adds 20% (in-progress adds 10%).
   - *1-Click Stage Advance*: Click any stage pill on the dashboard to advance its status with instant AJAX visual feedback.

4. **Order Management**:
   - Create new orders with validation.
   - Edit specifications, gauge notes, delivery deadlines, and assigned technicians.
   - Safe delete confirmation dialog.
   - Detailed Order View with visual workflow timeline and print-friendly job sheet.

5. **Ready Native Android App Project (`android/`)**:
   - Full native Android Studio project included in the `android/` folder with `SwipeRefreshLayout` (pull-to-refresh), smart back button handling, connection error recovery, and camera/file upload support.

---

## 📁 Complete Repository Structure

```text
OrderTrackPro/
├── manage.py                          # Django management CLI
├── db.sqlite3                         # Local SQLite database
├── requirements.txt                   # Project dependencies
├── README.md                          # Documentation & quickstart
├── .vscode/
│   ├── launch.json                    # F5 debug runner for VS Code
│   └── settings.json                  # VS Code Django template syntax associations
├── ordertrack_project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                    # Project configuration
│   ├── urls.py                        # Master URL routing
│   └── wsgi.py
├── tracking/
│   ├── __init__.py
│   ├── admin.py                       # Django Admin configuration
│   ├── apps.py
│   ├── forms.py                       # OrderForm with Bootstrap 5 widgets
│   ├── models.py                      # Order model, 5 stages & progress calculation
│   ├── tests.py                       # Automated test suite
│   ├── urls.py                        # App route patterns
│   ├── views.py                       # Dashboard, CRUD views, and AJAX stage updater
│   ├── migrations/
│   │   └── 0001_initial.py
│   └── management/
│       └── commands/
│           └── seed_orders.py         # Realistic demo commercial kitchen equipment seeder
├── static/
│   ├── css/
│   │   └── style.css                  # Custom workshop styling & badge animations
│   ├── js/
│   │   └── app.js                     # AJAX stage cycling, view switcher, toasts
│   ├── icons/
│   │   ├── icon-192.png               # Web/PWA App Icon (192x192)
│   │   └── icon-512.png               # Web/PWA App Icon (512x512)
│   ├── manifest.json                  # Web App Manifest for PWA
│   └── sw.js                          # Service Worker for offline shell caching
├── templates/
│   ├── base.html                      # Layout, navbar, mobile FAB, CDNs
│   └── tracking/
│       ├── dashboard.html             # Summary cards, search/filter, table & card views
│       ├── order_form.html            # Add / Edit Order form
│       ├── order_detail.html          # Timeline workflow, notes, print view
        └── order_confirm_delete.html  # Delete confirmation screen
└── android/                           # Complete Native Android Studio Project
    ├── build.gradle                   # Root Gradle build file
    ├── settings.gradle                # Gradle settings
    ├── gradle.properties              # JVM & AndroidX properties
    ├── README.md                      # Detailed Android guide & APK export steps
    └── app/
        ├── build.gradle               # App module dependencies (SwipeRefreshLayout, Material)
        ├── proguard-rules.pro
        └── src/
            └── main/
                ├── AndroidManifest.xml # Internet permissions & cleartext traffic rules
                ├── java/com/ordertrackpro/app/
                │   └── MainActivity.java # WebView, pull-to-refresh, back navigation, retry UI
                └── res/
                    ├── layout/activity_main.xml # Layout with WebView & connection retry screen
                    ├── values/ (colors.xml, strings.xml, themes.xml)
                    └── xml/network_security_config.xml # Allows HTTP local dev servers
```

---

## 🚀 How to Run the Django Web App

```powershell
# 1. Run migrations
python manage.py migrate

# 2. Seed realistic kitchen equipment demo data
python manage.py seed_orders

# 3. Start the server
python manage.py runserver 0.0.0.0:8000
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 📱 How to Run the Android App (Method 2)

1. Open **Android Studio**.
2. Select **Open** and choose the `OrderTrackPro/android` folder.
3. In `MainActivity.java`, ensure `SERVER_URL` points to `http://10.0.2.2:8000/` (for emulator) or your computer's local Wi-Fi IP (for a real phone).
4. Click **Run (▶)** to launch on your Android Emulator or USB-connected phone.
5. To export an APK: Go to **Build** &rarr; **Build Bundle(s) / APK(s)** &rarr; **Build APK(s)**.
