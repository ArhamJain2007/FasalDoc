# FasalDoc 🌿

AI-based Plant Disease Detection app for Indian farmers. Built with React Native CLI, TypeScript, TensorFlow Lite (on-device inference), and Firebase.

---

## Features

- 📷 **Camera & gallery scan** — capture or upload a leaf photo
- 🧠 **On-device AI** — TFLite model runs offline, no internet required
- 🌐 **Multi-language** — English, हिंदी, ਪੰਜਾਬੀ (all 3 fully translated including backend content)
- 📴 **Offline-first** — SQLite local storage, auto-syncs to cloud when connectivity returns
- 📋 **Scan history** — all results stored locally, filterable by status
- 🔔 **Push alerts** — FCM-powered seasonal disease alerts with weather triggers
- 💊 **Treatment plans** — organic + chemical options with dosage schedules
- 🌙 **Dark mode** — full dark/light theme via `useColorScheme()`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React Native CLI 0.73 |
| Language | TypeScript (strict mode) |
| Navigation | React Navigation v6 (Bottom Tabs + Native Stack) |
| i18n | i18next + react-i18next |
| State | Zustand + AsyncStorage persistence |
| Local DB | react-native-quick-sqlite (SQLite) |
| AI Inference | react-native-fast-tflite |
| Camera | react-native-image-picker |
| HTTP | Axios |
| Push | Firebase Cloud Messaging (FCM) |
| Animations | React Native Reanimated 3 |
| Haptics | react-native-haptic-feedback |

---

## Folder Structure

```
src/
├── screens/
│   ├── ScanScreen.tsx          # Main scan + detect
│   ├── ResultScreen.tsx        # Full disease result
│   ├── HistoryScreen.tsx       # Past scans
│   ├── AlertsScreen.tsx        # Seasonal alerts
│   ├── TreatmentScreen.tsx     # Treatment guide
│   └── SettingsScreen.tsx      # Language, notifs, account
├── components/
│   ├── LanguageSwitcher.tsx
│   ├── ScanButton.tsx          # With haptic + Reanimated press
│   ├── DiseaseCard.tsx
│   ├── ConfidenceBar.tsx       # Animated fill bar
│   ├── HistoryItem.tsx
│   ├── AlertBadge.tsx
│   ├── TreatmentTag.tsx
│   └── OfflineBanner.tsx       # Animated slide-down
├── navigation/
│   └── AppNavigator.tsx        # Bottom tabs + stack
├── i18n/
│   ├── index.ts
│   ├── en.json
│   ├── hi.json                 # Full Hindi translation
│   └── pa.json                 # Full Punjabi translation
├── store/
│   ├── useLanguageStore.ts     # Zustand + AsyncStorage
│   ├── useHistoryStore.ts      # Zustand + SQLite
│   └── useAlertStore.ts        # Zustand
├── services/
│   ├── api.ts                  # Axios + auth interceptor
│   ├── offlineDB.ts            # SQLite CRUD + sync helpers
│   ├── notifications.ts        # FCM setup + handlers
│   └── tflite.ts               # On-device inference
├── constants/
│   ├── colors.ts               # Light + dark palettes
│   ├── fonts.ts                # Typography + spacing tokens
│   └── diseases.ts             # 38 PlantVillage class names
└── assets/
    └── model/
        └── plant_disease.tflite   # Drop your trained model here
```

---

## Setup

### 1. Prerequisites

- Node.js 18+
- React Native CLI: `npm install -g react-native-cli`
- Xcode 15+ (iOS) / Android Studio (Android)
- JDK 17+
- CocoaPods (iOS): `sudo gem install cocoapods`

### 2. Install dependencies

```bash
npm install
cd ios && pod install && cd ..
```

### 3. Environment

Create `.env` in project root:

```
REACT_APP_API_URL=https://your-api.example.com
```

### 4. Firebase setup

1. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
2. Add iOS app → download `GoogleService-Info.plist` → place in `ios/FasalDoc/`
3. Add Android app → download `google-services.json` → place in `android/app/`
4. Enable Cloud Messaging in Firebase console

### 5. TFLite model

1. Train your model on [PlantVillage dataset](https://www.kaggle.com/datasets/emmarex/plantdisease) + Indian crop varieties
2. Convert to TFLite: `tflite_convert --output_file=plant_disease.tflite ...`
3. Place at `src/assets/model/plant_disease.tflite`
4. Update Metro config to bundle `.tflite` files (see below)

### 6. Metro config — add tflite to asset extensions

```js
// metro.config.js
const { getDefaultConfig } = require('@react-native/metro-config');
const config = getDefaultConfig(__dirname);
config.resolver.assetExts.push('tflite');
module.exports = config;
```

### 7. Run

```bash
# iOS
npx react-native run-ios

# Android
npx react-native run-android
```

---

## API Endpoints

The app expects a backend at `REACT_APP_API_URL` with these endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/detect` | Multipart image → disease detection result |
| `GET` | `/api/alerts?region=X` | Seasonal alerts for a region |
| `GET` | `/api/treatment/:id` | Treatment data for a disease |
| `POST` | `/api/sync` | Batch sync offline scan records |
| `POST` | `/api/register-token` | Register FCM device token |

### Detection response schema

```json
{
  "diseaseName": "Yellow Rust",
  "confidence": 94,
  "cropName": "Wheat",
  "stage": "Stage 1",
  "treatmentId": "T006",
  "description": "Caused by Puccinia striiformis. Appears as yellow stripes on leaves.",
  "severity": "high"
}
```

---

## SQLite Schema

```sql
CREATE TABLE scan_history (
  id           TEXT PRIMARY KEY,
  disease_name TEXT NOT NULL,
  crop_name    TEXT NOT NULL,
  confidence   REAL NOT NULL,
  stage        TEXT NOT NULL,
  image_uri    TEXT NOT NULL,
  scan_date    TEXT NOT NULL,
  status       TEXT NOT NULL DEFAULT 'active',
  treatment_id TEXT NOT NULL,
  synced       INTEGER NOT NULL DEFAULT 0,
  description  TEXT,
  severity     TEXT DEFAULT 'medium'
);
```

---

## Design System

### Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `PRIMARY_GREEN` | `#1D9E75` | CTA buttons, active states |
| `LIGHT_GREEN` | `#E1F5EE` | Card backgrounds, scan area |
| `DARK_GREEN` | `#0F6E56` | Headings on green backgrounds |
| `AMBER` | `#EF9F27` | Warnings, treated status |
| `RED` | `#E24B4A` | Danger, active disease |
| `BLUE` | `#378ADD` | Info, gallery button |
| `PURPLE` | `#7F77DD` | Language, region tags |

### Typography

- Heading: 18px / 500
- Subheading: 15px / 500
- Body: 14px / 400 / lh 22
- Caption: 11px / TEXT_SECONDARY
- Minimum font size: 11px

### Spacing

Multiples of 4px: `4, 8, 12, 16, 20, 24, 32`

---

## AI Model Notes

The `tflite.ts` service expects:
- **Input**: `float32[1, 224, 224, 3]` normalized to `[0, 1]`
- **Output**: `float32[1, 38]` — softmax probabilities over 38 PlantVillage classes

The 38 class labels are defined in `src/constants/diseases.ts` in PlantVillage dataset order.

For production, replace the placeholder pixel normalization in `tflite.ts` with actual pixel decoding using `react-native-fs` or `fetch()` + `ArrayBuffer`.

---

## Offline Sync Strategy

1. On every scan (offline): `synced = 0`, stored locally in SQLite
2. On connectivity restore (NetInfo listener in `App.tsx`): `getUnsynced()` → `POST /api/sync` → `markSynced()`
3. All scans accessible from history regardless of sync status

---

## Contributing

1. All strings must go through `useTranslation()` — no hardcoded English in components
2. All colors from `constants/colors.ts` — no inline hex values
3. No `any` types — TypeScript strict mode enforced
4. All lists must use `FlatList`, not `ScrollView + map`
5. Memoize list item components with `React.memo`
