"""
OpenSky Network API Client
OpenSky Network API 클라이언트

Collects ADS-B data from OpenSky Network
"""

import sys
import os

# Add parent directory to path to import opensky_api
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../python'))

try:
    from opensky_api import OpenSkyApi
except ImportError:
    print("Warning: opensky_api not found. Install with: pip install -e python/")
    OpenSkyApi = None

import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import time


class OpenSkyClient:
    """
    Client for OpenSky Network API
    OpenSky Network API 클라이언트
    """
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize OpenSky API client
        
        Parameters:
        -----------
        username : str, optional
            OpenSky Network username for authenticated access
        password : str, optional
            OpenSky Network password
        """
        if OpenSkyApi is None:
            raise ImportError("opensky_api not available. Install with: pip install -e python/")
        
        self.api = OpenSkyApi(username, password)
        self.rate_limit_delay = 10  # seconds between requests
        
    def get_states_in_bbox(
        self,
        bbox: Tuple[float, float, float, float],
        time_secs: Optional[int] = None
    ) -> List[Dict]:
        """
        Get aircraft states within bounding box
        
        Parameters:
        -----------
        bbox : tuple
            Bounding box (min_lat, max_lat, min_lon, max_lon)
        time_secs : int, optional
            Unix timestamp for historical data
        
        Returns:
        --------
        list : List of aircraft state dictionaries
        """
        min_lat, max_lat, min_lon, max_lon = bbox
        
        try:
            states = self.api.get_states(time_secs=time_secs, bbox=(min_lat, max_lat, min_lon, max_lon))
            
            if states is None or states.states is None:
                return []
            
            aircraft_list = []
            for state in states.states:
                aircraft_list.append({
                    'icao24': state.icao24,
                    'callsign': state.callsign.strip() if state.callsign else None,
                    'origin_country': state.origin_country,
                    'time_position': state.time_position,
                    'last_contact': state.last_contact,
                    'longitude': state.longitude,
                    'latitude': state.latitude,
                    'altitude': state.baro_altitude,  # meters
                    'on_ground': state.on_ground,
                    'velocity': state.velocity,  # m/s
                    'heading': state.heading,  # degrees
                    'vertical_rate': state.vertical_rate,  # m/s
                })
            
            return aircraft_list
            
        except Exception as e:
            print(f"Error fetching states: {e}")
            return []
    
    def get_track(
        self,
        icao24: str,
        time_begin: int,
        time_end: int
    ) -> Optional[Dict]:
        """
        Get flight track for specific aircraft
        
        Parameters:
        -----------
        icao24 : str
            ICAO24 address of aircraft
        time_begin : int
            Start time (Unix timestamp)
        time_end : int
            End time (Unix timestamp)
        
        Returns:
        --------
        dict : Track data with waypoints
        """
        try:
            track = self.api.get_track_by_aircraft(icao24, time_begin)
            
            if track is None or track.path is None:
                return None
            
            waypoints = []
            for point in track.path:
                waypoints.append({
                    'time': point.time,
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'altitude': point.baro_altitude,
                    'heading': point.heading,
                    'on_ground': point.on_ground
                })
            
            return {
                'icao24': track.icao24,
                'callsign': track.callsign,
                'start_time': track.startTime,
                'end_time': track.endTime,
                'waypoints': waypoints
            }
            
        except Exception as e:
            print(f"Error fetching track for {icao24}: {e}")
            return None
    
    def collect_route_traffic(
        self,
        route_bbox: Tuple[float, float, float, float],
        start_datetime: datetime,
        end_datetime: datetime,
        interval_minutes: int = 60
    ) -> List[Dict]:
        """
        Collect traffic data for a route over time period
        
        Parameters:
        -----------
        route_bbox : tuple
            Route bounding box (min_lat, max_lat, min_lon, max_lon)
        start_datetime : datetime
            Start date and time
        end_datetime : datetime
            End date and time
        interval_minutes : int
            Sampling interval in minutes
        
        Returns:
        --------
        list : List of traffic snapshots
        """
        all_traffic = []
        current_time = start_datetime
        
        print(f"Collecting traffic data from {start_datetime} to {end_datetime}")
        print(f"Sampling interval: {interval_minutes} minutes")
        
        while current_time <= end_datetime:
            timestamp = int(current_time.timestamp())
            
            print(f"Fetching data for {current_time.isoformat()}...", end=" ")
            states = self.get_states_in_bbox(route_bbox, time_secs=timestamp)
            
            print(f"Found {len(states)} aircraft")
            
            all_traffic.append({
                'timestamp': timestamp,
                'datetime': current_time,
                'aircraft_count': len(states),
                'states': states
            })
            
            # Move to next interval
            current_time += timedelta(minutes=interval_minutes)
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
        
        return all_traffic
    
    def get_aircraft_types_from_states(
        self,
        states: List[Dict]
    ) -> Dict[str, int]:
        """
        Get aircraft type distribution from states
        
        Note: OpenSky API doesn't directly provide aircraft type.
        This would need to be enhanced with aircraft database lookup.
        
        Parameters:
        -----------
        states : list
            List of aircraft states
        
        Returns:
        --------
        dict : Aircraft type counts
        """
        # Placeholder - would need aircraft database for real implementation
        # For now, return generic counts
        return {
            'unknown': len(states)
        }


class BoundingBoxHelper:
    """
    Helper class for creating bounding boxes around airways
    항공로 주변 경계 상자 생성 헬퍼 클래스
    """
    
    @staticmethod
    def create_route_bbox(
        waypoints: List[Tuple[float, float]],
        buffer_nm: float = 50.0
    ) -> Tuple[float, float, float, float]:
        """
        Create bounding box around route waypoints
        
        Parameters:
        -----------
        waypoints : list
            List of (lon, lat) tuples
        buffer_nm : float
            Buffer distance in nautical miles
        
        Returns:
        --------
        tuple : (min_lat, max_lat, min_lon, max_lon)
        """
        if not waypoints:
            raise ValueError("Waypoints list is empty")
        
        lons = [wp[0] for wp in waypoints]
        lats = [wp[1] for wp in waypoints]
        
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)
        
        # Convert buffer from nautical miles to degrees (approximate)
        # 1 degree latitude ≈ 60 nautical miles
        buffer_deg = buffer_nm / 60.0
        
        return (
            min_lat - buffer_deg,
            max_lat + buffer_deg,
            min_lon - buffer_deg,
            max_lon + buffer_deg
        )
    
    @staticmethod
    def point_in_bbox(
        point: Tuple[float, float],
        bbox: Tuple[float, float, float, float]
    ) -> bool:
        """
        Check if point is within bounding box
        
        Parameters:
        -----------
        point : tuple
            (lon, lat)
        bbox : tuple
            (min_lat, max_lat, min_lon, max_lon)
        
        Returns:
        --------
        bool : True if point is in bbox
        """
        lon, lat = point
        min_lat, max_lat, min_lon, max_lon = bbox
        
        return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
