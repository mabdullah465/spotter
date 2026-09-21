"""
Unit tests for HOS Calculator, Log Sheet Generator, PDF Export, and REST APIs.
"""

from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime
import json

from .services.hos_calculator import HOSCalculator, STATUS_DRIVING, STATUS_SLEEPER_BERTH, STATUS_OFF_DUTY, STATUS_ON_DUTY_NOT_DRIVING
from .services.log_sheet_generator import LogSheetGenerator
from .services.pdf_generator import generate_hos_log_pdf

class HOSTripEngineTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.start_dt = datetime(2026, 9, 21, 7, 0, 0)
        self.origin = {
            "name": "Chicago, IL",
            "city": "Chicago",
            "lat": 41.8781,
            "lng": -87.6298,
            "display_name": "Chicago, IL, USA"
        }
        self.pickup = {
            "name": "Indianapolis, IN",
            "city": "Indianapolis",
            "lat": 39.7684,
            "lng": -86.1581,
            "display_name": "Indianapolis, IN, USA"
        }
        self.dropoff = {
            "name": "Atlanta, GA",
            "city": "Atlanta",
            "lat": 33.7490,
            "lng": -84.3880,
            "display_name": "Atlanta, GA, USA"
        }

    def test_short_trip_simulation(self):
        calc = HOSCalculator(current_cycle_used=10.0, start_datetime=self.start_dt)
        leg1 = {"distance_miles": 180.0, "duration_hours": 3.0, "coordinates": [[41.87, -87.62], [39.76, -86.15]]}
        leg2 = {"distance_miles": 530.0, "duration_hours": 9.0, "coordinates": [[39.76, -86.15], [33.74, -84.38]]}

        res = calc.simulate_trip(self.origin, self.pickup, self.dropoff, leg1, leg2)
        events = res["events"]
        summary = res["summary"]

        self.assertTrue(len(events) > 0)
        self.assertAlmostEqual(summary["total_miles"], 710.0, delta=1.0)
        # Check event sequence includes pre-trip, driving, pickup, 30m break (since 3h+9h = 12h total drive), 10h rest, dropoff
        event_types = [e["event_type"] for e in events]
        self.assertIn("pre_trip", event_types)
        self.assertIn("pickup", event_types)
        self.assertIn("dropoff", event_types)
        self.assertIn("post_trip", event_types)

    def test_11_hour_driving_limit_and_10hr_reset(self):
        # Long trip requiring 16 hours of driving
        calc = HOSCalculator(current_cycle_used=0.0, start_datetime=self.start_dt)
        leg1 = {"distance_miles": 50.0, "duration_hours": 1.0, "coordinates": [[41.87, -87.62], [41.5, -87.5]]}
        leg2 = {"distance_miles": 850.0, "duration_hours": 15.0, "coordinates": [[41.5, -87.5], [33.74, -84.38]]}

        res = calc.simulate_trip(self.origin, self.pickup, self.dropoff, leg1, leg2)
        events = res["events"]
        summary = res["summary"]

        # Should have at least one 10-hour rest break
        self.assertGreaterEqual(summary["layovers_10h_count"], 1)
        rest_events = [e for e in events if e["event_type"] == "rest_10h"]
        self.assertTrue(len(rest_events) >= 1)
        self.assertEqual(rest_events[0]["duration_hours"], 10.0)

    def test_fuel_stop_rule_at_1000_miles(self):
        # Trip over 1,000 miles
        calc = HOSCalculator(current_cycle_used=0.0, start_datetime=self.start_dt, fuel_interval_miles=1000.0)
        leg1 = {"distance_miles": 100.0, "duration_hours": 2.0, "coordinates": [[34.05, -118.24], [35.0, -117.0]]}
        leg2 = {"distance_miles": 1200.0, "duration_hours": 22.0, "coordinates": [[35.0, -117.0], [40.71, -74.0]]}

        res = calc.simulate_trip(self.origin, self.pickup, self.dropoff, leg1, leg2)
        summary = res["summary"]
        self.assertGreaterEqual(summary["fuel_stops_count"], 1)

    def test_daily_log_sheets_exact_24hr_sum(self):
        calc = HOSCalculator(current_cycle_used=15.0, start_datetime=self.start_dt)
        leg1 = {"distance_miles": 200.0, "duration_hours": 3.5, "coordinates": [[41.87, -87.62], [39.76, -86.15]]}
        leg2 = {"distance_miles": 1500.0, "duration_hours": 26.0, "coordinates": [[39.76, -86.15], [33.74, -84.38]]}

        sim_res = calc.simulate_trip(self.origin, self.pickup, self.dropoff, leg1, leg2)
        generator = LogSheetGenerator(events=sim_res["events"], initial_cycle_used=15.0)
        sheets = generator.generate_log_sheets()

        self.assertGreaterEqual(len(sheets), 2)
        for sheet in sheets:
            totals = sheet["line_totals"]
            line_sum = (
                totals["line_1_off_duty"] +
                totals["line_2_sleeper_berth"] +
                totals["line_3_driving"] +
                totals["line_4_on_duty_not_driving"]
            )
            self.assertAlmostEqual(line_sum, 24.0, places=1, msg=f"Day {sheet['day_number']} total hours should equal 24.0")
            self.assertTrue(len(sheet["grid_polyline"]) > 0)
            self.assertIn("recap", sheet)

    def test_pdf_generation(self):
        calc = HOSCalculator(current_cycle_used=5.0, start_datetime=self.start_dt)
        leg1 = {"distance_miles": 50.0, "duration_hours": 1.0, "coordinates": [[41.87, -87.62], [41.5, -87.5]]}
        leg2 = {"distance_miles": 300.0, "duration_hours": 5.5, "coordinates": [[41.5, -87.5], [39.76, -86.15]]}

        sim_res = calc.simulate_trip(self.origin, self.pickup, self.dropoff, leg1, leg2)
        generator = LogSheetGenerator(events=sim_res["events"], initial_cycle_used=5.0)
        sheets = generator.generate_log_sheets()

        pdf_bytes = generate_hos_log_pdf(sheets, sim_res["summary"])
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_api_plan_trip_endpoint(self):
        payload = {
            "current_location": "Chicago, IL",
            "pickup_location": "Indianapolis, IN",
            "dropoff_location": "Atlanta, GA",
            "current_cycle_used": 20.0,
            "start_time": "08:00"
        }
        response = self.client.post(
            reverse("plan-trip"),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("route", data)
        self.assertIn("timeline", data)
        self.assertIn("log_sheets", data)
        self.assertIn("summary", data)

    def test_api_sample_trips_endpoint(self):
        response = self.client.get(reverse("sample-trips"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("samples", data)
        self.assertTrue(len(data["samples"]) >= 3)
