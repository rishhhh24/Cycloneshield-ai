"""
CycloneShield AI - Server-Side Live Manager & Background Update Loop
Manages background telemetry refresh, risk recalculation, and SSE streaming queues.
"""
import os
import time
import threading
import datetime
import json
from services.cyclone_service import LiveCycloneService
from services.weather_service import WeatherService
from services.risk_engine import RiskEngine
from services.exposure_service import ExposureService

class LiveManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.mode = "LIVE"  # "LIVE" or "DEMO"
        self.active_cyclone_id = "amphan_2020"
        self.refresh_interval = int(os.getenv('CYCLONE_REFRESH_SECONDS', 300))
        self.listeners = []
        self.last_state = {}
        self.running = False
        self.thread = None

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._background_loop, daemon=True)
            self.thread.start()
            print(f"[LIVE MANAGER] Started background telemetry update loop (Interval: {self.refresh_interval}s).")

    def _background_loop(self):
        while self.running:
            try:
                self.update_live_state()
            except Exception as e:
                print(f"[LIVE MANAGER ERROR] {e}")
            time.sleep(self.refresh_interval)

    def update_live_state(self):
        if self.mode == "DEMO":
            # DEMO / HISTORICAL SCENARIO MODE
            cyclone_info = {
                "status": "HISTORICAL",
                "mode": "DEMO",
                "has_active_cyclone": True,
                "source": "IMD Historical Disaster Archive (May 2020)",
                "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "display_status": "HISTORICAL SCENARIO — AMPHAN (2020)",
                "active_cyclone": {
                    "cyclone_id": "amphan_2020",
                    "name": "Amphan",
                    "year": 2020,
                    "basin": "North Indian Ocean (Bay of Bengal)",
                    "wind_speed_knots": 115.0,
                    "central_pressure_hpa": 920.0,
                    "status_category": "Super Cyclonic Storm (SuCS)",
                    "landfall_region": "South 24 Parganas, West Bengal",
                    "coordinates": {"latitude": 21.7, "longitude": 88.3}
                }
            }
            lat, lon = 21.7, 88.3
            cyclone_id_for_eval = "amphan_2020"
        else:
            # LIVE MODE
            cyclone_info = LiveCycloneService.get_live_cyclone_telemetry()
            if cyclone_info.get("has_active_cyclone") and cyclone_info.get("active_cyclone"):
                active_c = cyclone_info.get("active_cyclone", {})
                coords = active_c.get('coordinates', {'latitude': 21.7, 'longitude': 88.3})
                lat, lon = coords['latitude'], coords['longitude']
                cyclone_id_for_eval = active_c.get('cyclone_id', 'amphan_2020')
                cyclone_info['display_status'] = f"LIVE · {active_c.get('name', 'Active Cyclone').upper()}"
            else:
                lat, lon = 20.0, 88.0
                cyclone_id_for_eval = "amphan_2020"
                cyclone_info['display_status'] = "MONITORING — NO ACTIVE CYCLONE"

        # Fetch Live Weather telemetry from Open-Meteo at storm/basin coordinates
        weather_info = WeatherService.fetch_live_weather(lat, lon)

        # Recalculate Risk Score deterministically from live inputs
        wind_kts = weather_info.get('weather', {}).get('wind_speed_knots', 115.0)
        rain_mm = weather_info.get('weather', {}).get('projected_rainfall_mm', 280.0)

        risk_result = RiskEngine.calculate_vulnerability_score(
            cyclone_id=cyclone_id_for_eval,
            buffer_km=50.0,
            wind_knots=wind_kts,
            rainfall_mm=rain_mm
        )

        exposed_infra = ExposureService.calculate_exposure(
            cyclone_id=cyclone_id_for_eval,
            buffer_km=50.0
        )

        state = {
            "mode": self.mode,
            "status": cyclone_info.get('status', 'LIVE'),
            "has_active_cyclone": cyclone_info.get('has_active_cyclone', False),
            "display_status": cyclone_info.get('display_status', 'LIVE'),
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "cyclone": cyclone_info,
            "weather": weather_info,
            "risk": risk_result,
            "infrastructure": exposed_infra
        }

        self.last_state = state
        self._notify_listeners(state)
        return state

    def register_listener(self, queue):
        self.listeners.append(queue)

    def unregister_listener(self, queue):
        if queue in self.listeners:
            self.listeners.remove(queue)

    def _notify_listeners(self, state):
        payload = f"data: {json.dumps(state)}\n\n"
        for q in list(self.listeners):
            try:
                q.put(payload)
            except Exception:
                self.unregister_listener(q)
