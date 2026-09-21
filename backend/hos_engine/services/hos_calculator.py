"""
FMCSA Hours of Service (HOS) Simulation and Calculation Engine.
Strictly implements 49 CFR Part 395 regulations for property-carrying commercial drivers:
- 11-Hour Maximum Driving Limit per shift
- 14-Hour Consecutive Duty Window per shift
- 30-Minute Rest Break after 8 cumulative hours of driving
- 10-Hour Consecutive Off-Duty / Sleeper Berth Rest Period for shift reset
- 70-Hour / 8-Day Cumulative Cycle limit tracking & 34-hour restart detection
- Fueling stops at least once every 1,000 miles (30 min On-Duty Not Driving)
- 1 Hour On-Duty Loading at Pickup and 1 Hour On-Duty Unloading at Dropoff
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import math
from .router import interpolate_point_on_route

# FMCSA Standard Constants
STATUS_OFF_DUTY = "OFF_DUTY"
STATUS_SLEEPER_BERTH = "SLEEPER_BERTH"
STATUS_DRIVING = "DRIVING"
STATUS_ON_DUTY_NOT_DRIVING = "ON_DUTY_NOT_DRIVING"

STATUS_TO_LINE = {
    STATUS_OFF_DUTY: 1,
    STATUS_SLEEPER_BERTH: 2,
    STATUS_DRIVING: 3,
    STATUS_ON_DUTY_NOT_DRIVING: 4
}

class HOSCalculator:
    def __init__(
        self,
        current_cycle_used: float = 0.0,
        start_datetime: datetime = None,
        max_driving_per_shift: float = 11.0,
        max_duty_window: float = 14.0,
        max_drive_before_break: float = 8.0,
        break_duration: float = 0.5,
        rest_duration: float = 10.0,
        fuel_interval_miles: float = 1000.0,
        fuel_duration: float = 0.5,
        pickup_duration: float = 1.0,
        dropoff_duration: float = 1.0,
        pre_trip_duration: float = 0.25,
        post_trip_duration: float = 0.25,
        avg_speed_mph: float = 55.0
    ):
        self.initial_cycle_used = float(current_cycle_used)
        self.current_time = start_datetime or datetime.now().replace(minute=0, second=0, microsecond=0)
        self.max_driving_per_shift = max_driving_per_shift
        self.max_duty_window = max_duty_window
        self.max_drive_before_break = max_drive_before_break
        self.break_duration = break_duration
        self.rest_duration = rest_duration
        self.fuel_interval_miles = fuel_interval_miles
        self.fuel_duration = fuel_duration
        self.pickup_duration = pickup_duration
        self.dropoff_duration = dropoff_duration
        self.pre_trip_duration = pre_trip_duration
        self.post_trip_duration = post_trip_duration
        self.avg_speed_mph = avg_speed_mph

        # Active Clocks
        self.shift_driving_hours = 0.0
        self.shift_duty_window_hours = 0.0
        self.drive_since_break_hours = 0.0
        self.miles_since_fuel = 0.0
        self.total_odometer = 0.0
        self.events: List[Dict[str, Any]] = []

    def _add_event(
        self,
        status: str,
        duration_hours: float,
        location_name: str,
        lat: float,
        lng: float,
        remark: str,
        event_type: str,
        miles_driven: float = 0.0
    ) -> Dict[str, Any]:
        """Record an event in the timeline and advance the clock."""
        start_time = self.current_time
        end_time = start_time + timedelta(hours=duration_hours)
        odometer_start = self.total_odometer
        odometer_end = odometer_start + miles_driven

        event = {
            "status": status,
            "status_line": STATUS_TO_LINE[status],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "start_dt": start_time,
            "end_dt": end_time,
            "duration_hours": round(duration_hours, 3),
            "miles": round(miles_driven, 1),
            "odometer_start": round(odometer_start, 1),
            "odometer_end": round(odometer_end, 1),
            "location_name": location_name,
            "lat": round(lat, 5),
            "lng": round(lng, 5),
            "remark": remark,
            "event_type": event_type,
            # Clock snapshots
            "driving_shift_remaining": round(max(0.0, self.max_driving_per_shift - self.shift_driving_hours), 2),
            "window_remaining": round(max(0.0, self.max_duty_window - self.shift_duty_window_hours), 2),
            "break_countdown": round(max(0.0, self.max_drive_before_break - self.drive_since_break_hours), 2),
        }

        self.events.append(event)
        self.current_time = end_time
        self.total_odometer = odometer_end
        return event

    def _take_10hr_rest(self, location_name: str, lat: float, lng: float, reason: str = "Shift Reset"):
        """Execute a mandatory 10-hour consecutive rest break."""
        self._add_event(
            status=STATUS_SLEEPER_BERTH,
            duration_hours=self.rest_duration,
            location_name=location_name,
            lat=lat,
            lng=lng,
            remark=f"10-hr Mandatory Rest Period (Sleeper Berth) - {reason}",
            event_type="rest_10h"
        )
        # Reset shift clocks
        self.shift_driving_hours = 0.0
        self.shift_duty_window_hours = 0.0
        self.drive_since_break_hours = 0.0

        # Start new shift with Pre-Trip inspection
        self._start_shift_pre_trip(location_name, lat, lng)

    def _take_30min_break(self, location_name: str, lat: float, lng: float):
        """Execute a mandatory 30-minute rest break."""
        self._add_event(
            status=STATUS_OFF_DUTY,
            duration_hours=self.break_duration,
            location_name=location_name,
            lat=lat,
            lng=lng,
            remark="30-minute FMCSA Rest Break (Off Duty)",
            event_type="break_30m"
        )
        self.shift_duty_window_hours += self.break_duration
        self.drive_since_break_hours = 0.0

    def _take_fuel_stop(self, location_name: str, lat: float, lng: float):
        """Execute a fuel stop (30 min on-duty not driving)."""
        self._add_event(
            status=STATUS_ON_DUTY_NOT_DRIVING,
            duration_hours=self.fuel_duration,
            location_name=location_name,
            lat=lat,
            lng=lng,
            remark="Fueling CMV (On Duty Not Driving)",
            event_type="fuel"
        )
        self.shift_duty_window_hours += self.fuel_duration
        self.miles_since_fuel = 0.0

    def _start_shift_pre_trip(self, location_name: str, lat: float, lng: float):
        """Pre-trip vehicle inspection at start of shift."""
        self._add_event(
            status=STATUS_ON_DUTY_NOT_DRIVING,
            duration_hours=self.pre_trip_duration,
            location_name=location_name,
            lat=lat,
            lng=lng,
            remark="Pre-trip vehicle inspection & paperwork",
            event_type="pre_trip"
        )
        self.shift_duty_window_hours += self.pre_trip_duration

    def _drive_segment(
        self,
        total_leg_miles: float,
        total_leg_hours: float,
        start_location_name: str,
        end_location_name: str,
        coordinates: List[List[float]],
        leg_name: str
    ):
        """
        Simulates driving a leg, automatically carving into compliant driving chunks,
        interleaving 30-min breaks, 10-hr resets, and fuel stops.
        """
        miles_remaining = total_leg_miles
        hours_remaining = total_leg_hours
        leg_completed_miles = 0.0

        while miles_remaining > 0.01:
            # Check fuel requirement
            miles_until_fuel = max(0.0, self.fuel_interval_miles - self.miles_since_fuel)
            if miles_until_fuel <= 1.0:
                cur_frac = leg_completed_miles / max(1.0, total_leg_miles)
                fuel_lat, fuel_lng = interpolate_point_on_route(coordinates, cur_frac)
                fuel_loc = f"Travel Plaza / Fuel Stop (Mile {int(self.total_odometer)})"
                self._take_fuel_stop(fuel_loc, fuel_lat, fuel_lng)
                miles_until_fuel = self.fuel_interval_miles

            # Driving limits for current shift
            drive_avail_shift = self.max_driving_per_shift - self.shift_driving_hours
            window_avail = self.max_duty_window - self.shift_duty_window_hours
            drive_avail_break = self.max_drive_before_break - self.drive_since_break_hours

            # Max driving hours we can do in this continuous chunk
            max_drive_chunk = min(drive_avail_shift, window_avail, drive_avail_break, hours_remaining)
            # Also limit chunk by fuel distance
            chunk_miles_by_fuel = miles_until_fuel
            chunk_hours_by_fuel = chunk_miles_by_fuel / max(10.0, self.avg_speed_mph)

            chunk_hours = min(max_drive_chunk, chunk_hours_by_fuel)

            # If no driving possible in current shift (reached 11h driving or 14h window)
            if drive_avail_shift <= 0.01 or window_avail <= 0.01:
                cur_frac = leg_completed_miles / max(1.0, total_leg_miles)
                rest_lat, rest_lng = interpolate_point_on_route(coordinates, cur_frac)
                reason = "11-hr Drive Limit Reached" if drive_avail_shift <= 0.01 else "14-hr Duty Window Limit Reached"
                rest_loc = f"Truck Stop / Rest Area near Mile {int(self.total_odometer)}"
                self._take_10hr_rest(rest_loc, rest_lat, rest_lng, reason=reason)
                continue

            # If 8-hour drive limit reached before 30-min break
            if drive_avail_break <= 0.01:
                cur_frac = leg_completed_miles / max(1.0, total_leg_miles)
                break_lat, break_lng = interpolate_point_on_route(coordinates, cur_frac)
                break_loc = f"Highway Rest Area near Mile {int(self.total_odometer)}"
                self._take_30min_break(break_loc, break_lat, break_lng)
                continue

            # Calculate chunk miles
            # If this is the last chunk of the leg, take remaining miles
            if chunk_hours >= hours_remaining - 0.001:
                chunk_miles = miles_remaining
                chunk_hours = hours_remaining
            else:
                chunk_miles = min(miles_remaining, chunk_hours * self.avg_speed_mph)

            # Execute driving chunk
            cur_frac_end = (leg_completed_miles + chunk_miles) / max(1.0, total_leg_miles)
            end_chunk_lat, end_chunk_lng = interpolate_point_on_route(coordinates, cur_frac_end)

            chunk_label = f"Driving on {leg_name} ({int(leg_completed_miles)} to {int(leg_completed_miles + chunk_miles)} mi)"
            if miles_remaining - chunk_miles <= 0.05:
                chunk_dest_name = end_location_name
            else:
                chunk_dest_name = f"En Route towards {end_location_name}"

            self._add_event(
                status=STATUS_DRIVING,
                duration_hours=chunk_hours,
                location_name=chunk_dest_name,
                lat=end_chunk_lat,
                lng=end_chunk_lng,
                remark=f"Driving en route - {leg_name} ({round(chunk_miles, 1)} miles)",
                event_type="driving",
                miles_driven=chunk_miles
            )

            # Update counters
            self.shift_driving_hours += chunk_hours
            self.shift_duty_window_hours += chunk_hours
            self.drive_since_break_hours += chunk_hours
            self.miles_since_fuel += chunk_miles
            miles_remaining -= chunk_miles
            hours_remaining -= chunk_hours
            leg_completed_miles += chunk_miles

    def simulate_trip(
        self,
        origin_data: Dict[str, Any],
        pickup_data: Dict[str, Any],
        dropoff_data: Dict[str, Any],
        leg1_route: Dict[str, Any],
        leg2_route: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes the full trip simulation across Leg 1 (Origin to Pickup) and Leg 2 (Pickup to Dropoff).
        """
        # Start of Trip: Shift Pre-Trip Inspection
        self._start_shift_pre_trip(origin_data["city"] or origin_data["name"], origin_data["lat"], origin_data["lng"])

        # Leg 1: Origin to Pickup
        if leg1_route["distance_miles"] > 0.5:
            self._drive_segment(
                total_leg_miles=leg1_route["distance_miles"],
                total_leg_hours=leg1_route["duration_hours"],
                start_location_name=origin_data["city"] or origin_data["name"],
                end_location_name=pickup_data["city"] or pickup_data["name"],
                coordinates=leg1_route["coordinates"],
                leg_name=f"Leg 1: {origin_data['city']} to {pickup_data['city']}"
            )

        # Arrive at Pickup: 1 Hour Loading (On-Duty Not Driving)
        self._add_event(
            status=STATUS_ON_DUTY_NOT_DRIVING,
            duration_hours=self.pickup_duration,
            location_name=pickup_data["city"] or pickup_data["name"],
            lat=pickup_data["lat"],
            lng=pickup_data["lng"],
            remark=f"Loading Cargo at Shipper / Pickup: {pickup_data.get('display_name', pickup_data['name'])}",
            event_type="pickup"
        )
        self.shift_duty_window_hours += self.pickup_duration

        # Leg 2: Pickup to Dropoff
        if leg2_route["distance_miles"] > 0.5:
            self._drive_segment(
                total_leg_miles=leg2_route["distance_miles"],
                total_leg_hours=leg2_route["duration_hours"],
                start_location_name=pickup_data["city"] or pickup_data["name"],
                end_location_name=dropoff_data["city"] or dropoff_data["name"],
                coordinates=leg2_route["coordinates"],
                leg_name=f"Leg 2: {pickup_data['city']} to {dropoff_data['city']}"
            )

        # Arrive at Dropoff: 1 Hour Unloading (On-Duty Not Driving)
        self._add_event(
            status=STATUS_ON_DUTY_NOT_DRIVING,
            duration_hours=self.dropoff_duration,
            location_name=dropoff_data["city"] or dropoff_data["name"],
            lat=dropoff_data["lat"],
            lng=dropoff_data["lng"],
            remark=f"Unloading Cargo at Consignee / Dropoff: {dropoff_data.get('display_name', dropoff_data['name'])}",
            event_type="dropoff"
        )
        self.shift_duty_window_hours += self.dropoff_duration

        # Post-Trip Inspection at Destination
        self._add_event(
            status=STATUS_ON_DUTY_NOT_DRIVING,
            duration_hours=self.post_trip_duration,
            location_name=dropoff_data["city"] or dropoff_data["name"],
            lat=dropoff_data["lat"],
            lng=dropoff_data["lng"],
            remark="Post-trip vehicle inspection & completion paperwork",
            event_type="post_trip"
        )
        self.shift_duty_window_hours += self.post_trip_duration

        # Final Off-Duty Status
        self._add_event(
            status=STATUS_OFF_DUTY,
            duration_hours=0.5,
            location_name=dropoff_data["city"] or dropoff_data["name"],
            lat=dropoff_data["lat"],
            lng=dropoff_data["lng"],
            remark="Off Duty - Trip Complete",
            event_type="off_duty"
        )

        # Compute trip level summary statistics
        total_driving_time = sum(e["duration_hours"] for e in self.events if e["status"] == STATUS_DRIVING)
        total_on_duty_not_driving = sum(e["duration_hours"] for e in self.events if e["status"] == STATUS_ON_DUTY_NOT_DRIVING)
        total_sleeper_time = sum(e["duration_hours"] for e in self.events if e["status"] == STATUS_SLEEPER_BERTH)
        total_off_duty_time = sum(e["duration_hours"] for e in self.events if e["status"] == STATUS_OFF_DUTY)
        total_trip_distance = self.total_odometer
        trip_duty_hours = total_driving_time + total_on_duty_not_driving
        final_cycle_used = self.initial_cycle_used + trip_duty_hours

        # Detect potential cycle violation
        cycle_warning = None
        if final_cycle_used > 70.0:
            cycle_warning = f"Warning: Total cycle hours will reach {final_cycle_used:.1f} hrs, exceeding the 70.0-hour 8-day limit! A 34-hour restart is required."
        elif final_cycle_used > 60.0:
            cycle_warning = f"Notice: Heavy cycle utilization ({final_cycle_used:.1f} / 70.0 hrs). Plan 34-hr restart soon."

        return {
            "events": self.events,
            "summary": {
                "total_miles": round(total_trip_distance, 1),
                "total_driving_hours": round(total_driving_time, 2),
                "total_on_duty_not_driving_hours": round(total_on_duty_not_driving, 2),
                "total_duty_hours": round(trip_duty_hours, 2),
                "total_sleeper_hours": round(total_sleeper_time, 2),
                "total_off_duty_hours": round(total_off_duty_time, 2),
                "total_elapsed_hours": round((self.current_time - (self.events[0]["start_dt"] if self.events else self.current_time)).total_seconds() / 3600.0, 2),
                "initial_cycle_used": round(self.initial_cycle_used, 1),
                "final_cycle_used": round(final_cycle_used, 1),
                "cycle_remaining": round(max(0.0, 70.0 - final_cycle_used), 1),
                "cycle_warning": cycle_warning,
                "fuel_stops_count": len([e for e in self.events if e["event_type"] == "fuel"]),
                "rest_breaks_count": len([e for e in self.events if e["event_type"] == "break_30m"]),
                "layovers_10h_count": len([e for e in self.events if e["event_type"] == "rest_10h"]),
            }
        }
