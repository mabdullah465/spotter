"""
Views and API Endpoints for HOS Trip Planning, Geocoding, and PDF Generation.
"""

from datetime import datetime, date
import logging
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import TripPlanRequestSerializer, ExportPdfRequestSerializer
from .services.router import geocode_location, get_route_segment, search_location_suggestions
from .services.hos_calculator import HOSCalculator
from .services.log_sheet_generator import LogSheetGenerator
from .services.pdf_generator import generate_hos_log_pdf

logger = logging.getLogger(__name__)

class PlanTripAPIView(APIView):
    """
    POST /api/plan-trip/
    Calculates FMCSA compliant route, timeline, and 24-hr daily log sheets.
    """
    def post(self, request):
        serializer = TripPlanRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Validation failed", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        cur_loc_query = data["current_location"]
        pickup_loc_query = data["pickup_location"]
        dropoff_loc_query = data["dropoff_location"]
        current_cycle_used = data["current_cycle_used"]

        # Parse start datetime
        start_date_str = data.get("start_date")
        start_time_str = data.get("start_time", "07:00")
        try:
            if start_date_str:
                start_dt = datetime.strptime(f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M")
            else:
                today = date.today()
                start_dt = datetime.strptime(f"{today.isoformat()} {start_time_str}", "%Y-%m-%d %H:%M")
        except Exception:
            start_dt = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)

        # 1. Geocode locations
        origin = geocode_location(cur_loc_query)
        pickup = geocode_location(pickup_loc_query)
        dropoff = geocode_location(dropoff_loc_query)

        # 2. Compute route segments
        leg1_route = get_route_segment((origin["lat"], origin["lng"]), (pickup["lat"], pickup["lng"]))
        leg2_route = get_route_segment((pickup["lat"], pickup["lng"]), (dropoff["lat"], dropoff["lng"]))

        # 3. Simulate HOS Compliant Schedule
        calc = HOSCalculator(
            current_cycle_used=current_cycle_used,
            start_datetime=start_dt,
            max_driving_per_shift=11.0,
            max_duty_window=14.0,
            max_drive_before_break=8.0,
            fuel_interval_miles=1000.0
        )

        sim_result = calc.simulate_trip(
            origin_data=origin,
            pickup_data=pickup,
            dropoff_data=dropoff,
            leg1_route=leg1_route,
            leg2_route=leg2_route
        )

        events = sim_result["events"]
        summary = sim_result["summary"]

        # 4. Generate 24-Hour FMCSA Daily Log Sheets
        carrier_info = {
            "carrier_name": data.get("carrier_name", "Spotter Logistics Freight Inc."),
            "main_office_address": data.get("main_office_address", "100 Logistics Blvd, Dallas, TX"),
            "home_terminal_address": origin.get("display_name", origin.get("city", "Home Terminal")),
            "driver_name": data.get("driver_name", "John Doe"),
            "truck_tractor_number": data.get("truck_number", "TRK-8842"),
            "trailer_number": data.get("trailer_number", "TRL-5390"),
            "from_location": f"{origin.get('city', cur_loc_query)} -> {pickup.get('city', pickup_loc_query)}",
            "to_location": f"{dropoff.get('city', dropoff_loc_query)}",
            "shipping_documents": data.get("shipping_documents", "BOL #984214-SP / General Freight")
        }

        log_gen = LogSheetGenerator(
            events=events,
            carrier_info=carrier_info,
            initial_cycle_used=current_cycle_used
        )
        log_sheets = log_gen.generate_log_sheets()

        # 5. Build Map Markers & Combined Polyline
        combined_coordinates = leg1_route["coordinates"] + leg2_route["coordinates"]
        
        # Stop Markers
        markers = [
            {
                "id": "origin",
                "type": "origin",
                "label": "Current Location (Start)",
                "city": origin.get("city", cur_loc_query),
                "name": origin.get("display_name", cur_loc_query),
                "lat": origin["lat"],
                "lng": origin["lng"],
                "mile": 0.0,
                "time": start_dt.strftime("%I:%M %p, %b %d")
            },
            {
                "id": "pickup",
                "type": "pickup",
                "label": "Pickup Location (Shipper)",
                "city": pickup.get("city", pickup_loc_query),
                "name": pickup.get("display_name", pickup_loc_query),
                "lat": pickup["lat"],
                "lng": pickup["lng"],
                "mile": round(leg1_route["distance_miles"], 1),
                "duration": "1 Hour (Loading)"
            },
            {
                "id": "dropoff",
                "type": "dropoff",
                "label": "Dropoff Location (Consignee)",
                "city": dropoff.get("city", dropoff_loc_query),
                "name": dropoff.get("display_name", dropoff_loc_query),
                "lat": dropoff["lat"],
                "lng": dropoff["lng"],
                "mile": round(summary["total_miles"], 1),
                "duration": "1 Hour (Unloading)"
            }
        ]

        # Add En-Route Stops (Fuel, Rest Breaks, 10h Layovers)
        for i, ev in enumerate(events):
            if ev["event_type"] in ("fuel", "break_30m", "rest_10h"):
                markers.append({
                    "id": f"stop_{i}_{ev['event_type']}",
                    "type": ev["event_type"],
                    "label": ev["remark"],
                    "city": ev.get("location_name", "En Route"),
                    "name": ev.get("location_name", "En Route"),
                    "lat": ev["lat"],
                    "lng": ev["lng"],
                    "mile": round(ev["odometer_end"], 1),
                    "time": ev["start_dt"].strftime("%I:%M %p, %b %d"),
                    "duration": f"{ev['duration_hours']} hrs"
                })

        # Calculate Bounding Box
        all_lats = [c[0] for c in combined_coordinates] + [origin["lat"], pickup["lat"], dropoff["lat"]]
        all_lngs = [c[1] for c in combined_coordinates] + [origin["lng"], pickup["lng"], dropoff["lng"]]
        bounds = [
            [min(all_lats) - 0.5, min(all_lngs) - 0.5],
            [max(all_lats) + 0.5, max(all_lngs) + 0.5]
        ]

        response_payload = {
            "success": True,
            "inputs": {
                "current_location": cur_loc_query,
                "pickup_location": pickup_loc_query,
                "dropoff_location": dropoff_loc_query,
                "current_cycle_used": current_cycle_used,
                "start_datetime": start_dt.isoformat()
            },
            "locations": {
                "origin": origin,
                "pickup": pickup,
                "dropoff": dropoff
            },
            "route": {
                "total_miles": summary["total_miles"],
                "leg1_miles": leg1_route["distance_miles"],
                "leg2_miles": leg2_route["distance_miles"],
                "coordinates": combined_coordinates,
                "bounds": bounds,
                "markers": markers
            },
            "timeline": [
                {
                    "status": e["status"],
                    "status_line": e["status_line"],
                    "start_time": e["start_time"],
                    "end_time": e["end_time"],
                    "start_formatted": e["start_dt"].strftime("%b %d, %I:%M %p"),
                    "end_formatted": e["end_dt"].strftime("%b %d, %I:%M %p"),
                    "duration_hours": e["duration_hours"],
                    "miles": e["miles"],
                    "odometer_start": e["odometer_start"],
                    "odometer_end": e["odometer_end"],
                    "location_name": e["location_name"],
                    "lat": e["lat"],
                    "lng": e["lng"],
                    "remark": e["remark"],
                    "event_type": e["event_type"],
                    "driving_shift_remaining": e["driving_shift_remaining"],
                    "window_remaining": e["window_remaining"],
                    "break_countdown": e["break_countdown"]
                }
                for e in events
            ],
            "log_sheets": log_sheets,
            "summary": summary,
            "hos_clocks": {
                "driving_limit": 11.0,
                "duty_window_limit": 14.0,
                "rest_break_limit": 8.0,
                "cycle_limit": 70.0,
                "initial_cycle_used": current_cycle_used,
                "final_cycle_used": summary["final_cycle_used"],
                "cycle_remaining": summary["cycle_remaining"],
                "days_count": len(log_sheets)
            }
        }

        return Response(response_payload, status=status.HTTP_200_OK)

class ExportPdfAPIView(APIView):
    """
    POST /api/export-pdf/
    Generates and downloads the filled Driver's Daily Log PDF.
    """
    def post(self, request):
        serializer = ExportPdfRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid request for PDF export", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        log_sheets = serializer.validated_data["log_sheets"]
        trip_summary = serializer.validated_data.get("trip_summary", {})

        try:
            pdf_bytes = generate_hos_log_pdf(log_sheets, trip_summary)
            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="drivers_daily_logbook.pdf"'
            response["Content-Length"] = len(pdf_bytes)
            return response
        except Exception as e:
            logger.error(f"PDF generation error: {e}", exc_info=True)
            return Response({"error": f"Failed to generate PDF: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GeocodeAPIView(APIView):
    """
    GET /api/geocode/?q=...
    Location search and autocomplete.
    """
    def get(self, request):
        query = request.query_params.get("q", "")
        if not query or len(query.strip()) < 2:
            return Response({"results": []})
        results = search_location_suggestions(query.strip())
        return Response({"results": results})

class SampleTripsAPIView(APIView):
    """
    GET /api/sample-trips/
    Returns curated preset test scenarios.
    """
    def get(self, request):
        samples = [
            {
                "id": "cross_country",
                "title": "Cross-Country Long Haul (LA to New York)",
                "description": "2,800 miles, 4 log sheets, 3 fuel stops, mandatory 10-hr sleeper layovers and 30-min breaks.",
                "current_location": "Los Angeles, CA",
                "pickup_location": "Dallas, TX",
                "dropoff_location": "New York, NY",
                "current_cycle_used": 12.5,
                "carrier_name": "Trans-America Freight Express",
                "driver_name": "Marcus Vance",
                "truck_number": "TRK-9021",
                "trailer_number": "TRL-4420",
                "shipping_documents": "BOL #TA-88921 / Electronics"
            },
            {
                "id": "regional_midwest",
                "title": "Regional Haul (Chicago to Atlanta)",
                "description": "720 miles, 2 log sheets, pickup loading and dropoff unloading with 30-min break.",
                "current_location": "Chicago, IL",
                "pickup_location": "Indianapolis, IN",
                "dropoff_location": "Atlanta, GA",
                "current_cycle_used": 24.0,
                "carrier_name": "Midwest Intermodal Logistics",
                "driver_name": "Sarah Jenkins",
                "truck_number": "TRK-3310",
                "trailer_number": "TRL-8910",
                "shipping_documents": "BOL #MW-55201 / Auto Parts"
            },
            {
                "id": "short_haul",
                "title": "Short Haul Tri-State (Philadelphia to Baltimore)",
                "description": "210 miles, single 24-hr log sheet, quick delivery showing daily recap.",
                "current_location": "Philadelphia, PA",
                "pickup_location": "Newark, NJ",
                "dropoff_location": "Baltimore, MD",
                "current_cycle_used": 8.0,
                "carrier_name": "Eastern Seaboard Carriers",
                "driver_name": "David Miller",
                "truck_number": "TRK-1120",
                "trailer_number": "TRL-3004",
                "shipping_documents": "BOL #ES-10492 / Medical Supplies"
            },
            {
                "id": "heavy_cycle",
                "title": "Heavy Cycle Utilization (Approaching 70h)",
                "description": "Houston to Nashville with 58.5h already on 70h cycle, demonstrating HOS cycle threshold alert.",
                "current_location": "Houston, TX",
                "pickup_location": "Memphis, TN",
                "dropoff_location": "Nashville, TN",
                "current_cycle_used": 58.5,
                "carrier_name": "Southern Haulers Inc.",
                "driver_name": "Robert Taylor",
                "truck_number": "TRK-7740",
                "trailer_number": "TRL-6612",
                "shipping_documents": "BOL #SH-40912 / Building Materials"
            }
        ]
        return Response({"samples": samples})
