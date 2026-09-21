"""
Routing and Geocoding Service.
Uses OpenStreetMap Nominatim and OSRM (Open Source Routing Machine) with
resilient fallback for offline and rate-limited environments.
"""

import math
import logging
import requests
from typing import Dict, List, Tuple, Any, Optional

logger = logging.getLogger(__name__)

# Cache for geocoding queries
_GEOCODE_CACHE: Dict[str, Dict[str, Any]] = {}

# Major US Cities fallback dictionary
US_CITIES_FALLBACK = {
    "new york, ny": {"lat": 40.7128, "lng": -74.0060, "display_name": "New York, NY, USA"},
    "los angeles, ca": {"lat": 34.0522, "lng": -118.2437, "display_name": "Los Angeles, CA, USA"},
    "chicago, il": {"lat": 41.8781, "lng": -87.6298, "display_name": "Chicago, IL, USA"},
    "houston, tx": {"lat": 29.7604, "lng": -95.3698, "display_name": "Houston, TX, USA"},
    "phoenix, az": {"lat": 33.4484, "lng": -112.0740, "display_name": "Phoenix, AZ, USA"},
    "philadelphia, pa": {"lat": 39.9526, "lng": -75.1652, "display_name": "Philadelphia, PA, USA"},
    "san antonio, tx": {"lat": 29.4241, "lng": -98.4936, "display_name": "San Antonio, TX, USA"},
    "san diego, ca": {"lat": 32.7157, "lng": -117.1611, "display_name": "San Diego, CA, USA"},
    "dallas, tx": {"lat": 32.7767, "lng": -96.7970, "display_name": "Dallas, TX, USA"},
    "san jose, ca": {"lat": 37.3382, "lng": -121.8863, "display_name": "San Jose, CA, USA"},
    "austin, tx": {"lat": 30.2672, "lng": -97.7431, "display_name": "Austin, TX, USA"},
    "jacksonville, fl": {"lat": 30.3322, "lng": -81.6557, "display_name": "Jacksonville, FL, USA"},
    "fort worth, tx": {"lat": 32.7555, "lng": -97.3308, "display_name": "Fort Worth, TX, USA"},
    "columbus, oh": {"lat": 39.9612, "lng": -82.9988, "display_name": "Columbus, OH, USA"},
    "indianapolis, in": {"lat": 39.7684, "lng": -86.1581, "display_name": "Indianapolis, IN, USA"},
    "charlotte, nc": {"lat": 35.2271, "lng": -80.8431, "display_name": "Charlotte, NC, USA"},
    "san francisco, ca": {"lat": 37.7749, "lng": -122.4194, "display_name": "San Francisco, CA, USA"},
    "seattle, wa": {"lat": 47.6062, "lng": -122.3321, "display_name": "Seattle, WA, USA"},
    "denver, co": {"lat": 39.7392, "lng": -104.9903, "display_name": "Denver, CO, USA"},
    "washington, dc": {"lat": 38.9072, "lng": -77.0369, "display_name": "Washington, DC, USA"},
    "boston, ma": {"lat": 42.3601, "lng": -71.0589, "display_name": "Boston, MA, USA"},
    "el paso, tx": {"lat": 31.7619, "lng": -106.4850, "display_name": "El Paso, TX, USA"},
    "nashville, tn": {"lat": 36.1627, "lng": -86.7816, "display_name": "Nashville, TN, USA"},
    "detroit, mi": {"lat": 42.3314, "lng": -83.0458, "display_name": "Detroit, MI, USA"},
    "oklahoma city, ok": {"lat": 35.4676, "lng": -97.5164, "display_name": "Oklahoma City, OK, USA"},
    "portland, or": {"lat": 45.5152, "lng": -122.6784, "display_name": "Portland, OR, USA"},
    "las vegas, nv": {"lat": 36.1699, "lng": -115.1398, "display_name": "Las Vegas, NV, USA"},
    "memphis, tn": {"lat": 35.1495, "lng": -90.0490, "display_name": "Memphis, TN, USA"},
    "louisville, ky": {"lat": 38.2527, "lng": -85.7585, "display_name": "Louisville, KY, USA"},
    "baltimore, md": {"lat": 39.2904, "lng": -76.6122, "display_name": "Baltimore, MD, USA"},
    "milwaukee, wi": {"lat": 43.0389, "lng": -87.9065, "display_name": "Milwaukee, WI, USA"},
    "albuquerque, nm": {"lat": 35.0844, "lng": -106.6504, "display_name": "Albuquerque, NM, USA"},
    "tucson, az": {"lat": 32.2226, "lng": -110.9747, "display_name": "Tucson, AZ, USA"},
    "fresno, ca": {"lat": 36.7468, "lng": -119.7726, "display_name": "Fresno, CA, USA"},
    "sacramento, ca": {"lat": 38.5816, "lng": -121.4944, "display_name": "Sacramento, CA, USA"},
    "mesa, az": {"lat": 33.4152, "lng": -111.8315, "display_name": "Mesa, AZ, USA"},
    "kansas city, mo": {"lat": 39.0997, "lng": -94.5786, "display_name": "Kansas City, MO, USA"},
    "atlanta, ga": {"lat": 33.7490, "lng": -84.3880, "display_name": "Atlanta, GA, USA"},
    "omaha, ne": {"lat": 41.2565, "lng": -95.9345, "display_name": "Omaha, NE, USA"},
    "raleigh, nc": {"lat": 35.7796, "lng": -78.6382, "display_name": "Raleigh, NC, USA"},
    "miami, fl": {"lat": 25.7617, "lng": -80.1918, "display_name": "Miami, FL, USA"},
    "minneapolis, mn": {"lat": 44.9778, "lng": -93.2650, "display_name": "Minneapolis, MN, USA"},
    "tulsa, ok": {"lat": 36.1540, "lng": -95.9928, "display_name": "Tulsa, OK, USA"},
    "cleveland, oh": {"lat": 41.4993, "lng": -81.6944, "display_name": "Cleveland, OH, USA"},
    "wichita, ks": {"lat": 37.6872, "lng": -97.3301, "display_name": "Wichita, KS, USA"},
    "new orleans, la": {"lat": 29.9511, "lng": -90.0715, "display_name": "New Orleans, LA, USA"},
    "st. louis, mo": {"lat": 38.6270, "lng": -90.1994, "display_name": "St. Louis, MO, USA"},
    "pittsburgh, pa": {"lat": 40.4406, "lng": -79.9959, "display_name": "Pittsburgh, PA, USA"},
    "salt lake city, ut": {"lat": 40.7608, "lng": -111.8910, "display_name": "Salt Lake City, UT, USA"},
    "little rock, ar": {"lat": 34.7465, "lng": -92.2896, "display_name": "Little Rock, AR, USA"},
    "des moines, ia": {"lat": 41.5868, "lng": -93.6250, "display_name": "Des Moines, IA, USA"},
    "boise, id": {"lat": 43.6150, "lng": -116.2023, "display_name": "Boise, ID, USA"},
    "richmond, va": {"lat": 37.5407, "lng": -77.4360, "display_name": "Richmond, VA, USA"},
    "newark, nj": {"lat": 40.7357, "lng": -74.1724, "display_name": "Newark, NJ, USA"},
    "bakersfield, ca": {"lat": 35.3733, "lng": -119.0187, "display_name": "Bakersfield, CA, USA"},
    "birmingham, al": {"lat": 33.5186, "lng": -86.8104, "display_name": "Birmingham, AL, USA"},
    "cincinnati, oh": {"lat": 39.1031, "lng": -84.5120, "display_name": "Cincinnati, OH, USA"},
    "orlando, fl": {"lat": 28.5383, "lng": -81.3792, "display_name": "Orlando, FL, USA"},
    "tampa, fl": {"lat": 27.9506, "lng": -82.4572, "display_name": "Tampa, FL, USA"},
}

def haversine_distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in miles."""
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def geocode_location(query: str) -> Dict[str, Any]:
    """
    Geocode an address or city query to lat/lng and formatted address.
    """
    clean_query = query.strip()
    cache_key = clean_query.lower()
    
    if cache_key in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[cache_key]

    # Check direct lat,lng format
    if "," in clean_query:
        parts = [p.strip() for p in clean_query.split(",")]
        if len(parts) == 2:
            try:
                lat = float(parts[0])
                lng = float(parts[1])
                res = {
                    "lat": lat,
                    "lng": lng,
                    "name": f"{lat:.4f}, {lng:.4f}",
                    "display_name": f"Coordinates ({lat:.4f}, {lng:.4f})",
                    "city": "Custom Location",
                    "state": ""
                }
                _GEOCODE_CACHE[cache_key] = res
                return res
            except ValueError:
                pass

    # Check fallback dictionary
    for city_key, city_data in US_CITIES_FALLBACK.items():
        if city_key == cache_key or city_key in cache_key:
            res = {
                "lat": city_data["lat"],
                "lng": city_data["lng"],
                "name": clean_query.title(),
                "display_name": city_data["display_name"],
                "city": city_key.split(",")[0].title(),
                "state": city_key.split(",")[1].strip().upper() if "," in city_key else ""
            }
            _GEOCODE_CACHE[cache_key] = res
            return res

    # Query Nominatim API with 3s timeout
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "Spotter-HOS-ELD-Trip-Planner-App/1.0"}
        params = {
            "q": clean_query,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
            "countrycodes": "us,ca,mx"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=3.5)
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                item = data[0]
                addr = item.get("address", {})
                city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or clean_query
                state = addr.get("state") or addr.get("state_code", "")
                res = {
                    "lat": float(item["lat"]),
                    "lng": float(item["lon"]),
                    "name": clean_query.title(),
                    "display_name": item.get("display_name", clean_query),
                    "city": city,
                    "state": state
                }
                _GEOCODE_CACHE[cache_key] = res
                return res
    except Exception as e:
        logger.warning(f"Nominatim geocode exception for '{query}': {e}")

    # Fallback to rough centroid if unmatched
    logger.info(f"Using default fallback for '{query}'")
    res = {
        "lat": 39.8283,
        "lng": -98.5795,
        "name": clean_query.title(),
        "display_name": f"{clean_query}, USA",
        "city": clean_query,
        "state": "US"
    }
    _GEOCODE_CACHE[cache_key] = res
    return res

def search_location_suggestions(query: str, limit: int = 6) -> List[Dict[str, Any]]:
    """
    Search autocomplete suggestions for a location query.
    """
    clean_query = query.strip().lower()
    if not clean_query:
        return []

    results = []
    # Match fallback cities first
    for city_key, data in US_CITIES_FALLBACK.items():
        if clean_query in city_key or clean_query in data["display_name"].lower():
            results.append({
                "lat": data["lat"],
                "lng": data["lng"],
                "display_name": data["display_name"],
                "name": city_key.title()
            })
            if len(results) >= limit:
                return results

    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "Spotter-HOS-ELD-Trip-Planner-App/1.0"}
        params = {
            "q": clean_query,
            "format": "json",
            "limit": limit,
            "addressdetails": 1,
            "countrycodes": "us,ca,mx"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=3.0)
        if resp.status_code == 200:
            for item in resp.json():
                results.append({
                    "lat": float(item["lat"]),
                    "lng": float(item["lon"]),
                    "display_name": item.get("display_name", ""),
                    "name": item.get("name", item.get("display_name", ""))
                })
    except Exception as e:
        logger.warning(f"Suggestions search error: {e}")

    return results[:limit]

def fetch_osrm_route(start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Optional[Dict[str, Any]]:
    """
    Query OSRM driving service for route geometry, distance, and duration.
    Coordinates format: (lat, lng)
    """
    lat1, lng1 = start_coords
    lat2, lng2 = end_coords

    # OSRM expects lon,lat format
    url = f"https://router.project-osrm.org/route/v1/driving/{lng1},{lat1};{lng2},{lat2}?overview=full&geometries=geojson&steps=true"
    headers = {"User-Agent": "Spotter-HOS-ELD-Trip-Planner-App/1.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "Ok" and data.get("routes"):
                route = data["routes"][0]
                distance_meters = route["distance"]
                duration_seconds = route["duration"]
                coordinates = [[pt[1], pt[0]] for pt in route["geometry"]["coordinates"]] # Convert [lng, lat] to [lat, lng]
                
                # Convert meters to miles (1 meter = 0.000621371 miles)
                distance_miles = distance_meters * 0.000621371
                
                # Realistic CMV speed adjustment: heavy commercial truck average highway speed is ~55-60 mph
                # OSRM assumes car speed, so calculate realistic truck driving duration
                realistic_truck_hours = max(distance_miles / 55.0, duration_seconds / 3600.0)

                return {
                    "distance_miles": round(distance_miles, 1),
                    "duration_hours": round(realistic_truck_hours, 2),
                    "coordinates": coordinates,
                    "source": "osrm"
                }
    except Exception as e:
        logger.warning(f"OSRM routing failed: {e}")

    return None

def compute_fallback_route(start_coords: Tuple[float, float], end_coords: Tuple[float, float], num_points: int = 50) -> Dict[str, Any]:
    """
    Compute smooth geometric route fallback with realistic road winding factor.
    """
    lat1, lng1 = start_coords
    lat2, lng2 = end_coords
    
    crow_miles = haversine_distance_miles(lat1, lon1=lng1, lat2=lat2, lon2=lng2)
    # Winding factor for US road network is approx 1.18 - 1.25x crow flies distance
    winding_factor = 1.22 if crow_miles > 100 else 1.15
    distance_miles = max(1.0, crow_miles * winding_factor)
    
    # Commercial truck average highway speed is approx 55 mph
    duration_hours = distance_miles / 55.0

    coordinates = []
    for i in range(num_points + 1):
        t = i / float(num_points)
        # Add slight curvature for visual realism
        curve = math.sin(t * math.pi) * 0.15 * (1.0 if (lng2 - lng1) > 0 else -0.15)
        cur_lat = lat1 + (lat2 - lat1) * t + curve
        cur_lng = lng1 + (lng2 - lng1) * t
        coordinates.append([round(cur_lat, 5), round(cur_lng, 5)])

    return {
        "distance_miles": round(distance_miles, 1),
        "duration_hours": round(duration_hours, 2),
        "coordinates": coordinates,
        "source": "fallback"
    }

def get_route_segment(start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Dict[str, Any]:
    """
    Get route segment using OSRM with graceful fallback.
    """
    route = fetch_osrm_route(start_coords, end_coords)
    if not route:
        route = compute_fallback_route(start_coords, end_coords)
    return route

def interpolate_point_on_route(coordinates: List[List[float]], fraction: float) -> Tuple[float, float]:
    """
    Given a list of [lat, lng] coordinates and a progress fraction (0.0 - 1.0),
    interpolate the exact coordinate along the polyline.
    """
    if not coordinates:
        return (39.8283, -98.5795)
    if len(coordinates) == 1 or fraction <= 0.0:
        return (coordinates[0][0], coordinates[0][1])
    if fraction >= 1.0:
        return (coordinates[-1][0], coordinates[-1][1])

    total_idx = (len(coordinates) - 1) * fraction
    idx1 = int(total_idx)
    idx2 = min(idx1 + 1, len(coordinates) - 1)
    local_t = total_idx - idx1

    lat = coordinates[idx1][0] + (coordinates[idx2][0] - coordinates[idx1][0]) * local_t
    lng = coordinates[idx1][1] + (coordinates[idx2][1] - coordinates[idx1][1]) * local_t
    return (round(lat, 5), round(lng, 5))
