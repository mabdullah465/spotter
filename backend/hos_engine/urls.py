"""
HOS Engine URL routing.
"""

from django.urls import path
from .views import PlanTripAPIView, ExportPdfAPIView, GeocodeAPIView, SampleTripsAPIView

urlpatterns = [
    path('plan-trip/', PlanTripAPIView.as_view(), name='plan-trip'),
    path('export-pdf/', ExportPdfAPIView.as_view(), name='export-pdf'),
    path('geocode/', GeocodeAPIView.as_view(), name='geocode'),
    path('sample-trips/', SampleTripsAPIView.as_view(), name='sample-trips'),
]
