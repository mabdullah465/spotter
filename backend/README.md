# 🚚 Spotter HOS & ELD Backend Engine

The backend for **Spotter ELD & HOS Trip Planner** is a high-performance **Django REST Framework** service that simulates real-world commercial trucking itineraries, enforces **FMCSA 49 CFR Part 395** compliance, and generates official 24-hour **Driver's Daily Log (RODS)** sheets with high-resolution vector PDF export.

---

## 🏛️ Backend Architecture & Directory Structure

```
backend/
├── manage.py
├── requirements.txt
├── spotter_backend/
│   ├── __init__.py
│   ├── settings.py           # Django settings, DRF configuration, CORS setup
│   ├── urls.py               # Main URL dispatcher & health check endpoint
│   ├── asgi.py
│   └── wsgi.py
└── hos_engine/
    ├── __init__.py
    ├── models.py
    ├── serializers.py        # Request & Response serializers with data validation
    ├── urls.py               # /api/ endpoints routing
    ├── views.py              # PlanTrip, ExportPdf, Geocode, SampleTrips views
    ├── tests.py              # Automated test suite (HOS limits, fueling, 24h balance)
    └── services/
        ├── __init__.py
        ├── router.py         # OpenStreetMap Nominatim geocoding & OSRM routing
        ├── hos_calculator.py # Core FMCSA HOS chronological simulation engine
        ├── log_sheet_generator.py # 24-hr midnight-to-midnight log splitter & recap
        └── pdf_generator.py  # ReportLab vector PDF generator for FMCSA paper logs
```

---

## ⚙️ Core Services Breakdown

### 1. `services/router.py` (Routing & Geocoding)
- **Geocoding**: Interfaces with OpenStreetMap Nominatim API with query caching and an offline fallback directory of major US metropolitan hubs.
- **Routing**: Interfaces with the Open Source Routing Machine (OSRM) driving API to retrieve highway distances, travel durations, and GeoJSON coordinate polyline arrays.
- **Coordinate Interpolation**: Determines precise geographic latitude/longitude for any waypoint along the route based on cumulative odometer mileage.

### 2. `services/hos_calculator.py` (FMCSA HOS Simulation)
Implements all property-carrying driver regulations (49 CFR Part 395):
- **11-Hour Driving Limit**: Tracks cumulative driving per shift. Halts driving and triggers a 10-hour rest when 11.0 hours is reached.
- **14-Hour Duty Window**: Starts when driver first goes on duty (e.g. 15-min pre-trip inspection). Halts driving when the 14-hour window expires.
- **30-Minute Rest Break**: Enforces a mandatory 30-minute break before exceeding 8 consecutive/cumulative hours of driving.
- **10-Hour Consecutive Rest (Sleeper Berth)**: Executes 10-hour rest periods resetting the 11-hour driving and 14-hour window clocks.
- **1,000-Mile Fueling Interval**: Automatically schedules 30-minute fueling stops (On Duty Not Driving) at or before every 1,000 miles.
- **Pickup & Drop-off Loading**: Simulates 1.0 hour each of On Duty Not Driving for loading at the Shipper and unloading at the Consignee.
- **70-Hour / 8-Day Cycle**: Computes rolling cumulative duty hours and alerts if trip exceeds the 70.0-hour threshold.

### 3. `services/log_sheet_generator.py` (24-Hour Daily Log Splitting)
- Splits continuous multi-day trip timelines into discrete **calendar days (00:00 to 24:00 midnight)** in accordance with FMCSA logbook standards.
- Calculates exact hours spent across the 4 standard duty lines:
  - **Line 1**: Off Duty
  - **Line 2**: Sleeper Berth
  - **Line 3**: Driving
  - **Line 4**: On Duty (Not Driving)
- Balances line sums to guarantee `Line 1 + Line 2 + Line 3 + Line 4 = 24.00` hours per daily sheet.
- Generates continuous stepped SVG/Canvas coordinates including vertical duty transition segments.
- Computes the official **70-Hour / 8-Day Recap**:
  - `Today's On Duty Hours` (Lines 3 + 4)
  - `Line A`: Total hours on duty last 7 days including today
  - `Line B`: Total hours available tomorrow ($70 - A$)
  - `Line C`: Total hours on duty last 8 days including today

### 4. `services/pdf_generator.py` (ReportLab Vector PDF Exporter)
- Builds printable multi-page PDF documents replicating the official FMCSA Form 49 CFR Part 395 layout.
- Renders 15-minute grid tick marks, carrier metadata, vehicle identifiers, continuous stepped blue duty line, timestamped remarks table, and driver signature blocks.

---

## 📡 REST API Reference

### 1. `POST /api/plan-trip/`
Calculates route geometry, runs HOS simulation, and generates daily log sheets.

**Request Body:**
```json
{
  "current_location": "Chicago, IL",
  "pickup_location": "Indianapolis, IN",
  "dropoff_location": "Atlanta, GA",
  "current_cycle_used": 18.5,
  "start_date": "2026-09-21",
  "start_time": "07:00",
  "carrier_name": "Spotter Logistics Freight Inc.",
  "driver_name": "Marcus Vance",
  "truck_number": "TRK-8842",
  "trailer_number": "TRL-5390",
  "shipping_documents": "BOL #984214-SP / General Freight"
}
```

**Response Format:**
```json
{
  "success": true,
  "inputs": { ... },
  "locations": {
    "origin": { "lat": 41.8781, "lng": -87.6298, "city": "Chicago" },
    "pickup": { "lat": 39.7684, "lng": -86.1581, "city": "Indianapolis" },
    "dropoff": { "lat": 33.7490, "lng": -84.3880, "city": "Atlanta" }
  },
  "route": {
    "total_miles": 684.3,
    "coordinates": [[41.8781, -87.6298], ...],
    "bounds": [[33.24, -88.12], [42.37, -83.88]],
    "markers": [
      { "type": "origin", "lat": 41.8781, "lng": -87.6298, "label": "Start" },
      { "type": "pickup", "lat": 39.7684, "lng": -86.1581, "label": "Pickup (1h)" },
      { "type": "break_30m", "lat": 36.1627, "lng": -86.7816, "label": "30m Break" },
      { "type": "rest_10h", "lat": 35.0456, "lng": -85.3097, "label": "10h Rest" },
      { "type": "dropoff", "lat": 33.7490, "lng": -84.3880, "label": "Dropoff (1h)" }
    ]
  },
  "timeline": [ ... ],
  "log_sheets": [
    {
      "day_number": 1,
      "date": "09/21/2026",
      "line_totals": {
        "line_1_off_duty": 7.5,
        "line_2_sleeper_berth": 4.25,
        "line_3_driving": 11.0,
        "line_4_on_duty_not_driving": 1.25,
        "total_hours": 24.0
      },
      "grid_polyline": [ { "x": 0.0, "y": 1 }, { "x": 7.0, "y": 1 }, ... ],
      "remarks": [ ... ],
      "recap": {
        "today_on_duty": 12.25,
        "recap_a_total_last_7_days": 30.75,
        "recap_b_available_tomorrow": 39.25,
        "recap_c_total_last_8_days": 30.75
      }
    }
  ],
  "summary": {
    "total_miles": 684.3,
    "total_driving_hours": 13.44,
    "total_duty_hours": 16.19,
    "fuel_stops_count": 0,
    "rest_breaks_count": 1,
    "layovers_10h_count": 1,
    "final_cycle_used": 34.69,
    "cycle_remaining": 35.31
  }
}
```

---

### 2. `POST /api/export-pdf/`
Generates and streams the official PDF logbook binary.

**Request Body:**
```json
{
  "log_sheets": [ ... ],
  "trip_summary": { ... }
}
```
**Response:** `application/pdf` binary with `Content-Disposition: attachment; filename="drivers_daily_logbook.pdf"`.

---

### 3. `GET /api/geocode/?q=<location>`
Autocomplete search for US addresses and cities.

---

### 4. `GET /api/sample-trips/`
Returns curated test presets (Cross-Country, Regional Midwest, Short Haul, Near Cycle Limit).

---

## 🚀 Installation & Running

### Requirements
- Python 3.10+
- `pip`

```bash
# 1. Navigate to backend directory
cd D:\spotter\backend

# 2. (Optional) Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Start development server
python manage.py runserver 127.0.0.1:8000
```

---

## 🧪 Automated Testing

Execute the comprehensive test suite:
```bash
python manage.py test
```
**Tests Covered:**
- `test_short_trip_simulation`: Complete trip lifecycle (pre-trip, leg 1, loading, leg 2, unloading, post-trip).
- `test_11_hour_driving_limit_and_10hr_reset`: Verification of 10-hour sleeper berth insertion and shift clock reset.
- `test_fuel_stop_rule_at_1000_miles`: Verification of 30-min fueling stop insertion before 1,000 miles.
- `test_daily_log_sheets_exact_24hr_sum`: Verification that 4 status lines sum to exactly 24.00 hours per day.
- `test_pdf_generation`: ReportLab vector PDF binary generation integrity test.
- `test_api_plan_trip_endpoint`: End-to-end HTTP integration test.
- `test_api_sample_trips_endpoint`: Sample scenarios availability test.
