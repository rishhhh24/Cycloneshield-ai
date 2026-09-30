"""
CycloneShield AI - Real-Time Cyclone Telemetry Service
Delegates to LiveDataService for external ingestion (IMD, NOAA IBTrACS, GDACS).
"""
from services.live_data_service import LiveDataService

class LiveCycloneService:
    @staticmethod
    def get_live_cyclone_telemetry():
        """
        Retrieves real-time cyclone telemetry from external data feeds.
        If no active storm is present in external feeds, returns status="MONITORING"
        and has_active_cyclone=False without fabricating active coordinates.
        """
        return LiveDataService.fetch_live_cyclone_telemetry()
