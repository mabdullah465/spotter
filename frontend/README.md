# 💻 Spotter HOS & ELD Frontend Dashboard

The frontend for **Spotter ELD & HOS Trip Planner** is a responsive single-page web application built with **React 18**, **Vite**, **Tailwind CSS**, and **Leaflet**. It provides interactive route mapping, dynamic HOS compliance gauge clocks, a multi-day Driver's Daily Log viewer with an SVG 24-hour graph grid, and one-click PDF export.

---

## 🏛️ Frontend Architecture & Directory Structure

```
frontend/
├── package.json
├── vite.config.js            # Vite configuration with backend API proxying
├── tailwind.config.js        # Custom theme colors and typography
├── postcss.config.js
├── index.html                # Entry HTML with Leaflet CSS and typography imports
└── src/
    ├── main.jsx              # React DOM root entry
    ├── App.jsx               # Main state container & layout orchestrator
    ├── index.css             # Tailwind base styles, animations, and Leaflet overrides
    ├── services/
    │   └── api.js            # API client for backend communication & PDF streaming
    ├── utils/
    │   └── formatters.js     # Duration, mileage, and duty status styling helpers
    └── components/
        ├── Header.jsx        # Navigation bar, branding, and modal triggers
        ├── TripInputForm.jsx # Origin/pickup/dropoff form with autocomplete & presets
        ├── HosClocks.jsx     # Live compliance clocks (11h, 14h, 8h break, 70h cycle)
        ├── RouteMap.jsx      # Leaflet map with custom HTML DivIcons for HOS stops
        ├── DailyLogSheet.jsx # Multi-day logbook viewer with day tabs & PDF export
        ├── LogGridCanvas.jsx # High-definition SVG 24-hour FMCSA graph grid
        ├── ItineraryTimeline.jsx # Step-by-step chronological itinerary
        ├── TripSummary.jsx   # Performance metrics card
        ├── HosRulesGuideModal.jsx # Interactive FMCSA 49 CFR Part 395 guide
        └── SampleTripsModal.jsx   # Curated test scenarios modal
```

---

## 🎨 Component Breakdown

### 1. `LogGridCanvas.jsx` (24-Hour FMCSA Graph Grid)
- Custom high-resolution vector SVG component that renders the official FMCSA 24-hour graph.
- Features:
  - Top header with standard midnight-to-midnight hour markings.
  - 4 distinct duty rows:
    1. *Off Duty*
    2. *Sleeper Berth*
    3. *Driving*
    4. *On Duty (Not Driving)*
  - 15-minute, 30-minute, and 45-minute tick subdivisions.
  - Continuous stepped polyline with vertical transitions when status changes.
  - Interactive hover tooltips displaying the exact time window, duration, and activity description.
  - Right column displaying balanced total hours for each line.

### 2. `RouteMap.jsx` (Interactive Route & Stops Map)
- Powered by **Leaflet** & **React-Leaflet** using free CartoDB / OpenStreetMap tile layers.
- Custom styled markers for:
  - 📍 Origin (Start)
  - 📦 Shipper Pickup (1 Hour Loading)
  - 🏁 Consignee Dropoff (1 Hour Unloading)
  - ⛽ Fuel Stops (at least once every 1,000 miles)
  - ☕ 30-Minute FMCSA Rest Breaks
  - 🛏️ 10-Hour Mandatory Sleeper Berth Layovers
- Interactive popups with arrival times, odometer miles, and stop durations.
- Automatic viewport bounding box fitting.

### 3. `HosClocks.jsx` (HOS Compliance Gauges)
- **11-Hour Drive Limit Clock**: Monitors driving time per shift.
- **14-Hour Duty Window Clock**: Tracks consecutive hours from shift start.
- **8-Hour Break Countdown**: Countdown to mandatory 30-minute break.
- **70-Hour / 8-Day Cycle Meter**: Dynamic progress bar with automatic warning alerts when approaching or exceeding 70.0 hours.

### 4. `DailyLogSheet.jsx` (Multi-Day Paper Log Replica)
- Day switcher carousel tabs for trips spanning multiple calendar days.
- Complete header with carrier name, office address, home terminal, truck/trailer numbers, and shipping documents.
- Official **70-Hour / 8-Day Recap Box** (Lines 3 & 4 today, Line A last 7 days, Line B available tomorrow, Line C last 8 days).
- Timestamped Remarks table.
- Direct PDF Download & Print view.

---

## 🚀 Installation & Running

### Requirements
- Node.js 18+
- npm

```bash
# 1. Navigate to frontend directory
cd D:\spotter\frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

Frontend application will be accessible at: `http://localhost:5173/`

---

## 📦 Production Build

```bash
# Compile and optimize production bundle
npm run build

# Preview production build locally
npm run preview
```
Production assets are generated in `frontend/dist/`.
