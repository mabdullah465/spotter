"""
DRF Serializers for HOS Trip Planning and PDF Export.
"""

from rest_framework import serializers
from datetime import datetime

class TripPlanRequestSerializer(serializers.Serializer):
    current_location = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=300,
        help_text="Current location (e.g., 'Chicago, IL' or '100 Main St, Dallas, TX')"
    )
    pickup_location = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=300,
        help_text="Pickup / Shipper location"
    )
    dropoff_location = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=300,
        help_text="Dropoff / Consignee location"
    )
    current_cycle_used = serializers.FloatField(
        required=True,
        min_value=0.0,
        max_value=70.0,
        help_text="Current 70-hour / 8-day cycle hours used (0.0 - 70.0 hrs)"
    )
    start_date = serializers.CharField(
        required=False,
        default="",
        allow_blank=True,
        help_text="Start date (YYYY-MM-DD), defaults to today"
    )
    start_time = serializers.CharField(
        required=False,
        default="07:00",
        allow_blank=True,
        help_text="Start time (HH:MM in 24h format, e.g. 07:00)"
    )
    carrier_name = serializers.CharField(
        required=False,
        default="Spotter Logistics Freight Inc.",
        allow_blank=True
    )
    driver_name = serializers.CharField(
        required=False,
        default="John Doe",
        allow_blank=True
    )
    truck_number = serializers.CharField(
        required=False,
        default="TRK-8842",
        allow_blank=True
    )
    trailer_number = serializers.CharField(
        required=False,
        default="TRL-5390",
        allow_blank=True
    )
    main_office_address = serializers.CharField(
        required=False,
        default="100 Logistics Blvd, Dallas, TX",
        allow_blank=True
    )
    shipping_documents = serializers.CharField(
        required=False,
        default="BOL #984214-SP / General Freight",
        allow_blank=True
    )

    def validate_current_cycle_used(self, value):
        if value < 0 or value > 70.0:
            raise serializers.ValidationError("Current cycle used must be between 0.0 and 70.0 hours.")
        return value

class ExportPdfRequestSerializer(serializers.Serializer):
    log_sheets = serializers.ListField(
        child=serializers.DictField(),
        required=True
    )
    trip_summary = serializers.DictField(
        required=False,
        default=dict
    )
