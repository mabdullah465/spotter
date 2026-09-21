"""
FMCSA Daily Log Sheet Generation Service.
Splits continuous chronological HOS timelines into discrete 24-hour midnight-to-midnight
Driver's Daily Log sheets (49 CFR 395.8) with grid coordinate lines, remarks, and 70hr/8day recap.
"""

from datetime import datetime, timedelta, date
from typing import Dict, List, Any
import math

from .hos_calculator import (
    STATUS_OFF_DUTY,
    STATUS_SLEEPER_BERTH,
    STATUS_DRIVING,
    STATUS_ON_DUTY_NOT_DRIVING,
    STATUS_TO_LINE
)

LINE_TO_STATUS = {
    1: STATUS_OFF_DUTY,
    2: STATUS_SLEEPER_BERTH,
    3: STATUS_DRIVING,
    4: STATUS_ON_DUTY_NOT_DRIVING
}

LINE_NAMES = {
    1: "1. Off Duty",
    2: "2. Sleeper Berth",
    3: "3. Driving",
    4: "4. On Duty (Not Driving)"
}

def format_hour_string(hours_float: float) -> str:
    """Format decimal hour (e.g. 14.75) into 12-hour AM/PM string (e.g. 02:45 PM)."""
    hours_int = int(hours_float) % 24
    mins_int = int(round((hours_float - int(hours_float)) * 60))
    if mins_int >= 60:
        hours_int = (hours_int + 1) % 24
        mins_int = 0
    period = "AM" if hours_int < 12 else "PM"
    display_hour = 12 if hours_int in (0, 12) else hours_int % 12
    return f"{display_hour:02d}:{mins_int:02d} {period}"

def format_24h_string(hours_float: float) -> str:
    """Format decimal hour into 24h format (e.g. 14:45)."""
    hours_int = int(hours_float) % 24
    mins_int = int(round((hours_float - int(hours_float)) * 60))
    if mins_int >= 60:
        hours_int = (hours_int + 1) % 24
        mins_int = 0
    return f"{hours_int:02d}:{mins_int:02d}"

class LogSheetGenerator:
    def __init__(
        self,
        events: List[Dict[str, Any]],
        carrier_info: Dict[str, Any] = None,
        initial_cycle_used: float = 0.0
    ):
        self.events = events
        self.carrier_info = carrier_info or {}
        self.initial_cycle_used = initial_cycle_used

    def generate_log_sheets(self) -> List[Dict[str, Any]]:
        """
        Processes simulation events and generates 24-hour log sheets for each calendar day.
        """
        if not self.events:
            return []

        # Find trip start and end datetime
        first_event = self.events[0]
        last_event = self.events[-1]

        start_dt = first_event["start_dt"]
        end_dt = last_event["end_dt"]

        cur_date = start_dt.date()
        end_date = end_dt.date()

        log_sheets = []
        cumulative_cycle = self.initial_cycle_used
        day_number = 1

        # Iterate day by day from start_date to end_date
        while cur_date <= end_date:
            day_start = datetime(cur_date.year, cur_date.month, cur_date.day, 0, 0, 0)
            day_end = day_start + timedelta(days=1)

            # Daily segments list
            day_segments = []
            day_remarks = []
            day_miles = 0.0

            cur_time_cursor = day_start

            # Find all event slices falling inside this day
            for event in self.events:
                e_start = event["start_dt"]
                e_end = event["end_dt"]

                # Check overlap
                overlap_start = max(day_start, e_start)
                overlap_end = min(day_end, e_end)

                if overlap_end > overlap_start:
                    # If cursor is before overlap_start, fill gap with Off Duty
                    if overlap_start > cur_time_cursor:
                        gap_dur = (overlap_start - cur_time_cursor).total_seconds() / 3600.0
                        start_h = (cur_time_cursor - day_start).total_seconds() / 3600.0
                        end_h = (overlap_start - day_start).total_seconds() / 3600.0
                        day_segments.append({
                            "status": STATUS_OFF_DUTY,
                            "status_line": 1,
                            "start_hour": round(start_h, 3),
                            "end_hour": round(end_h, 3),
                            "duration_hours": round(gap_dur, 3),
                            "remark": "Off Duty",
                            "location_name": event.get("location_name", ""),
                            "time_display": f"{format_24h_string(start_h)} - {format_24h_string(end_h)}"
                        })
                        cur_time_cursor = overlap_start

                    # Add event slice
                    slice_dur = (overlap_end - overlap_start).total_seconds() / 3600.0
                    start_h = (overlap_start - day_start).total_seconds() / 3600.0
                    end_h = (overlap_end - day_start).total_seconds() / 3600.0
                    
                    # Proportional miles for slice
                    event_total_dur = max(0.001, (e_end - e_start).total_seconds() / 3600.0)
                    slice_fraction = slice_dur / event_total_dur
                    slice_miles = event.get("miles", 0.0) * slice_fraction
                    day_miles += slice_miles

                    day_segments.append({
                        "status": event["status"],
                        "status_line": event["status_line"],
                        "start_hour": round(start_h, 3),
                        "end_hour": round(end_h, 3),
                        "duration_hours": round(slice_dur, 3),
                        "remark": event["remark"],
                        "location_name": event.get("location_name", ""),
                        "time_display": f"{format_24h_string(start_h)} - {format_24h_string(end_h)}",
                        "event_type": event.get("event_type", "")
                    })

                    # If this event started today or transitioned today, record in daily remarks
                    if e_start >= day_start and e_start < day_end:
                        day_remarks.append({
                            "time": e_start.strftime("%H:%M"),
                            "time_12h": e_start.strftime("%I:%M %p"),
                            "hour_val": round(start_h, 2),
                            "status": event["status"],
                            "status_line": event["status_line"],
                            "location": event.get("location_name", "En Route"),
                            "remark": event["remark"],
                            "miles": round(event.get("miles", 0.0), 1)
                        })

                    cur_time_cursor = overlap_end

            # If end of day has remaining gap up to 24:00, fill with Off Duty
            if cur_time_cursor < day_end:
                gap_dur = (day_end - cur_time_cursor).total_seconds() / 3600.0
                start_h = (cur_time_cursor - day_start).total_seconds() / 3600.0
                end_h = 24.0
                day_segments.append({
                    "status": STATUS_OFF_DUTY,
                    "status_line": 1,
                    "start_hour": round(start_h, 3),
                    "end_hour": round(end_h, 3),
                    "duration_hours": round(gap_dur, 3),
                    "remark": "Off Duty",
                    "location_name": last_event.get("location_name", ""),
                    "time_display": f"{format_24h_string(start_h)} - {format_24h_string(end_h)}"
                })

            # Calculate line totals
            line_totals = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
            for seg in day_segments:
                line_totals[seg["status_line"]] += seg["duration_hours"]

            # Round line totals and balance to exactly 24.0
            for line in line_totals:
                line_totals[line] = round(line_totals[line], 2)

            total_sum = sum(line_totals.values())
            diff = round(24.0 - total_sum, 2)
            if abs(diff) > 0.001:
                # Adjust off duty to ensure exact 24.0 sum
                line_totals[1] = round(max(0.0, line_totals[1] + diff), 2)

            # Today's on-duty hours (Line 3 Driving + Line 4 On Duty Not Driving)
            today_on_duty = round(line_totals[3] + line_totals[4], 2)
            recap_a = round(cumulative_cycle + today_on_duty, 2)
            recap_b = round(max(0.0, 70.0 - recap_a), 2)
            recap_c = recap_a
            cumulative_cycle = recap_a

            # Generate Grid Stepped Polyline Coordinates for Canvas / SVG rendering
            # Grid has X: 0 to 24 (hours), Y: 1 to 4 (line status)
            grid_polyline = []
            for i, seg in enumerate(day_segments):
                # Start of segment
                if i == 0:
                    grid_polyline.append({"x": seg["start_hour"], "y": seg["status_line"]})
                else:
                    prev_seg = day_segments[i - 1]
                    if prev_seg["status_line"] != seg["status_line"]:
                        # Vertical transition line
                        grid_polyline.append({"x": seg["start_hour"], "y": prev_seg["status_line"]})
                        grid_polyline.append({"x": seg["start_hour"], "y": seg["status_line"]})
                # End of segment
                grid_polyline.append({"x": seg["end_hour"], "y": seg["status_line"]})

            # Format log sheet
            date_str = cur_date.strftime("%m/%d/%Y")
            date_display = cur_date.strftime("%A, %B %d, %Y")

            log_sheet = {
                "day_number": day_number,
                "date": date_str,
                "date_display": date_display,
                "date_iso": cur_date.isoformat(),
                # Header Information
                "carrier_name": self.carrier_info.get("carrier_name", "Spotter Logistics Freight Inc."),
                "main_office_address": self.carrier_info.get("main_office_address", "100 Logistics Blvd, Suite 400, Dallas, TX"),
                "home_terminal_address": self.carrier_info.get("home_terminal_address", self.carrier_info.get("main_office_address", "Dallas, TX")),
                "driver_name": self.carrier_info.get("driver_name", "Professional Driver"),
                "co_driver_name": self.carrier_info.get("co_driver_name", "N/A"),
                "truck_tractor_number": self.carrier_info.get("truck_tractor_number", "TRK-8842"),
                "trailer_number": self.carrier_info.get("trailer_number", "TRL-5390"),
                "from_location": self.carrier_info.get("from_location", "Origin Terminal"),
                "to_location": self.carrier_info.get("to_location", "Destination Terminal"),
                "shipping_documents": self.carrier_info.get("shipping_documents", "BOL #984214-SP / General Freight"),
                "miles_today": round(day_miles, 1),
                "total_mileage_today": round(day_miles, 1),
                # 24-Hour Grid Data
                "segments": day_segments,
                "grid_polyline": grid_polyline,
                "line_totals": {
                    "line_1_off_duty": line_totals[1],
                    "line_2_sleeper_berth": line_totals[2],
                    "line_3_driving": line_totals[3],
                    "line_4_on_duty_not_driving": line_totals[4],
                    "total_hours": 24.0
                },
                # Remarks
                "remarks": day_remarks,
                # 70-Hour / 8-Day Recap
                "recap": {
                    "today_on_duty": today_on_duty,
                    "recap_a_total_last_7_days": recap_a,
                    "recap_b_available_tomorrow": recap_b,
                    "recap_c_total_last_8_days": recap_c,
                    "cycle_limit": 70.0,
                    "is_cycle_warning": recap_a > 70.0
                }
            }

            log_sheets.append(log_sheet)
            cur_date += timedelta(days=1)
            day_number += 1

        return log_sheets
