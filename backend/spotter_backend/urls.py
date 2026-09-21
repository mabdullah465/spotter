"""
URL configuration for spotter_backend project.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "healthy", "service": "Spotter HOS & ELD Engine", "version": "1.0.0"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health_check'),
    path('api/', include('hos_engine.urls')),
]
