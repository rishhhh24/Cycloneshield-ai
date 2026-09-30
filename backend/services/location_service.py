"""
CycloneShield AI - Location Analysis Service
Performs real-time geospatial risk analysis, live weather lookup, active cyclone proximity calculation,
and infrastructure exposure counts for any coordinate in India or globally.
"""
import urllib.request
import json
import datetime
from services.weather_service import WeatherService
from services.gis_service import GISService
from models.infrastructure import InfrastructureModel
from models.cyclone import CycloneModel
from services.live_manager import LiveManager

class LocationService:
    @staticmethod
    def reverse_geocode(lat, lon):
        """
        Reverse geocodes latitude and longitude using OpenStreetMap Nominatim.
        Fallback to state/coordinate formatting if network request fails.
        """
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'CycloneShield-AI-LocationService/1.0'}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    address = data.get('address', {})
                    name = (
                        address.get('city') or
                        address.get('town') or
                        address.get('district') or
                        address.get('county') or
                        address.get('state_district') or
                        address.get('suburb') or
                        address.get('village') or
                        data.get('display_name', '').split(',')[0]
                    )
                    state = address.get('state') or address.get('country') or 'India'
                    return {"name": name or f"{lat:.2f}°N, {lon:.2f}°E", "state": state}
        except Exception as e:
            print(f"Reverse geocode note: {e}")
        
        return {"name": f"{lat:.2f}°N, {lon:.2f}°E", "state": "India"}

    @staticmethod
    def analyze_location(lat, lon):
        """
        Analyzes a specific location coordinate (lat, lon).
        Returns structured JSON with location name, real weather, risk scores, infrastructure exposure, and cyclone proximity.
        """
        # 1. Reverse Geocode Location
        geo_info = LocationService.reverse_geocode(lat, lon)
        loc_name = geo_info["name"]
        loc_state = geo_info["state"]

        # 2. Fetch Live Weather Telemetry (Open-Meteo)
        weather_res = WeatherService.fetch_live_weather(lat, lon)
        w_data = weather_res.get("weather", {})
        
        wind_spd_kmh = w_data.get("wind_speed_kmh", 0)
        wind_spd_kts = w_data.get("wind_speed_knots", 0)
        pressure = w_data.get("surface_pressure_hpa", 1013)
        rainfall = w_data.get("projected_rainfall_mm", 0)
        temp = w_data.get("temperature_c", 25.0)
        humidity = w_data.get("humidity_percent", 65.0)

        # 3. Active Cyclone Proximity Check
        manager = LiveManager.get_instance()
        live_state = manager.last_state or {}
        active_cyclone_info = live_state.get("cyclone", {})
        
        has_active = live_state.get("has_active_cyclone", False)
        cyclone_name = None
        cyclone_dist_km = None

        if has_active and active_cyclone_info.get("active_cyclone"):
            c_data = active_cyclone_info["active_cyclone"]
            cyclone_name = c_data.get("name")
            c_coords = c_data.get("coordinates", {})
            c_lat = c_coords.get("latitude")
            c_lon = c_coords.get("longitude")
            if c_lat is not None and c_lon is not None:
                cyclone_dist_km = round(GISService.haversine_distance_km(lat, lon, c_lat, c_lon), 1)

        # 4. Calculate Risk & Hazards
        # Wind Hazard (0-100)
        wind_hazard = max(0.0, min(100.0, wind_spd_kts * 1.2))
        
        # Rainfall Hazard (0-100)
        rainfall_hazard = max(0.0, min(100.0, rainfall * 0.35))
        
        # Surge Hazard (0-100) if near coast/storm proximity
        surge_hazard = 0.0
        if cyclone_dist_km is not None and cyclone_dist_km <= 300:
            surge_hazard = max(0.0, min(100.0, 100.0 - (cyclone_dist_km / 3.0)))
        elif wind_spd_kts > 35 or rainfall > 100:
            surge_hazard = max(0.0, min(100.0, (wind_spd_kts + rainfall) * 0.25))

        # Overall Risk Score (0-100)
        if cyclone_dist_km is not None and cyclone_dist_km <= 150:
            proximity_factor = max(0.0, (150.0 - cyclone_dist_km) / 1.5)
            overall_score = min(100.0, max(wind_hazard, rainfall_hazard, surge_hazard) * 0.6 + proximity_factor * 0.4)
        else:
            overall_score = min(100.0, wind_hazard * 0.4 + rainfall_hazard * 0.4 + surge_hazard * 0.2)

        overall_score = round(overall_score, 1)

        if overall_score >= 75.0:
            risk_level = "EXTREME"
        elif overall_score >= 50.0:
            risk_level = "HIGH"
        elif overall_score >= 25.0:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        # 5. Infrastructure Exposure Calculation within 50km radius
        all_infra = InfrastructureModel.get_all()
        infra_features = all_infra.get("features", [])

        infra_counts = {
            "hospitals": 0,
            "shelters": 0,
            "power": 0,
            "transport": 0,
            "total_exposed": 0
        }

        for item in infra_features:
            props = item.get("properties", {})
            geom = item.get("geometry", {})
            cat = (props.get("category") or "").lower()

            if geom.get("type") == "Point":
                coords = geom.get("coordinates", [])
                if len(coords) >= 2:
                    dist = GISService.haversine_distance_km(lat, lon, coords[1], coords[0])
                    if dist <= 50.0:
                        infra_counts["total_exposed"] += 1
                        if cat in ["hospital", "medical"]:
                            infra_counts["hospitals"] += 1
                        elif cat in ["shelter", "cyclone_shelter"]:
                            infra_counts["shelters"] += 1
                        elif cat in ["power", "substation", "grid"]:
                            infra_counts["power"] += 1
                        elif cat in ["road", "railway", "transport"]:
                            infra_counts["transport"] += 1

        return {
            "location": {
                "latitude": round(lat, 4),
                "longitude": round(lon, 4),
                "name": loc_name,
                "state": loc_state
            },
            "weather": {
                "wind_speed": round(wind_spd_kmh, 1),
                "wind_speed_knots": round(wind_spd_kts, 1),
                "pressure": round(pressure, 1),
                "rainfall": round(rainfall, 1),
                "temperature": round(temp, 1),
                "humidity": round(humidity, 1)
            },
            "risk": {
                "score": overall_score,
                "level": risk_level,
                "wind_hazard": round(wind_hazard, 1),
                "rainfall_hazard": round(rainfall_hazard, 1),
                "surge_hazard": round(surge_hazard, 1)
            },
            "infrastructure": infra_counts,
            "cyclone": {
                "active": has_active,
                "name": cyclone_name,
                "distance_km": cyclone_dist_km
            }
        }
