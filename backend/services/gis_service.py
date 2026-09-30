"""
GIS Processing Service - Haversine Distance & Spatial Buffering
"""
import math

class GISService:
    @staticmethod
    def haversine_distance_km(lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points on Earth in kilometers.
        """
        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def min_distance_to_track_km(point_lat, point_lon, track_points):
        """
        Calculates minimum distance from a coordinate to a list of cyclone track points.
        """
        if not track_points:
            return float('inf')
        
        min_dist = float('inf')
        for tp in track_points:
            lat = tp.get('latitude') or tp.get('lat')
            lon = tp.get('longitude') or tp.get('lon')
            if lat is not None and lon is not None:
                dist = GISService.haversine_distance_km(point_lat, point_lon, lat, lon)
                if dist < min_dist:
                    min_dist = dist
        return min_dist
